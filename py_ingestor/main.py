from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
import zmq
import time
from datetime import datetime
from database import logs_collection

#data structs needed

class LogInput(BaseModel):
  service: str
  level: str
  message: str

class SearchQuery(BaseModel):
  term: str

#app definition 

app = FastAPI(title="LogStream API")

#cors permissions

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:4200"], #explicit permission for angular
  allow_credentials=True,
  allow_methods=["*"],#allow all methods
  allow_headers=["*"],#allow all options
)

#zmq socket 

zmq_context = None
zmq_socket = None

@app.on_event("startup")
def startup_event():
  global zmq_context, zmq_socket
  print("Connecting to C++ engine...")
  zmq_context = zmq.Context()
  zmq_socket = zmq_context.socket(zmq.REQ)
  zmq_socket.connect("tcp://localhost:5555")

@app.on_event("shutdown")
def shutdown_event():
  global zmq_context, zmq_socket
  if zmq_socket: zmq_socket.close()
  if zmq_context: zmq_context.term()

#endpoints

@app.post("/ingest")
def ingest_log(log: LogInput):
  log_id = int(time.time() * 1000000)#unique id

  log_entry = {
    "_id": log_id,
    "timestamp": datetime.utcnow().isoformat(),
    "service": log.service,
    "level": log.level,
    "message": log.message
  }

  #save to db
  try:
    logs_collection.insert_one(log_entry)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Mongo Error: {str(e)}")

  #send to C++ for indexing
  try:
    cmd = {
      "command": "ADD",
      "id": log_id,
      "text": log.message
    }
    zmq_socket.send_json(cmd)

    reply = zmq_socket.recv_json()

    if reply.get("status") != "OK":
      print(f"C++ Warning: {reply.get('message')}")

  except zmq.ZMQError as e:
    raise HTTPException(status_code=503, detail=f"Search Engine Unavailable: {str(e)}")

  return {"status": "indexed", "id": log_id}

@app.get("/search")
def search_logs(term: str):
  #ask c++ engine
  cmd = {"command": "SEARCH", "term": term}
  zmq_socket.send_json(cmd)
  reply = zmq_socket.recv_json()

  if reply.get("status") != "OK":
    raise HTTPException(status_code=500, detail=reply.get("message"))

  matching_ids = reply.get("results", [])

  if not matching_ids:  
    return {"count": 0, "results": []}

  #fetch from db
  cursor = logs_collection.find({"_id": {"$in": matching_ids}})

  results = [doc for doc in cursor]

  return {"count": len(results), "results": results};
