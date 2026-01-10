from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
import zmq
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database import get_db, LogEntrySQL

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
pub_socket = None
req_socket = None #for search

@app.on_event("startup")
def startup_event():
  global zmq_context, pub_socket, req_socket
  print("Initiliazing ZMQ content...")
  
  zmq_context = zmq.Context()
  
  pub_socket = zmq_context.socket(zmq.PUB)
  pub_socket.setsockopt(zmq.SNDHWM, 10000)
  pub_socket.bind("tcp://*:5556")

  req_socket = zmq_context.socket(zmq.REQ)
  req_socket.setsockopt(zmq.RCVHWM, 10000)
  req_socket.connect("tcp://localhost:5555")

@app.on_event("shutdown")
def shutdown_event():
  global zmq_context, pub_socket, req_socket
  if pub_socket: pub_socket.close()
  if req_socket: req_socket.close()
  if zmq_context: zmq_context.term()

#endpoints

@app.post("/ingest")
async def ingest_log(log: LogInput):
  log_id = int(time.time() * 1000000)#unique id

  log_entry = {
    "id": log_id,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "service": log.service,
    "level": log.level,
    "message": log.message
  }

  try:
    pub_socket.send_json(log_entry)
    return {"status": "queued", "id": log_id}
  except zmq.ZMQError as e:
    raise HTTPException(status_code=503, detail=f"Queue unavailable: {str(e)}") 


@app.get("/search")
def search_logs(term: str, db: Session = Depends(get_db)):
  #ask c++ engine
  cmd = {"command": "SEARCH", "term": term}
  
  try:
    req_socket.send_json(cmd)
    reply = req_socket.recv_json()

  except zmq.ZMQError as e:
    raise HTTPException(status_code=503, detail=f"Search Engine unavailable: {str(e)}") 

  if reply.get("status") != "OK":
    raise HTTPException(status_code=500, detail=reply.get("message"))

  matching_ids = reply.get("results", [])

  if not matching_ids:  
    return {"count": 0, "results": []}

  #use SQL Query here after configuring reqs
  results = []
  print(f"Need to fetch SQL details for IDs: {matching_ids}")

  try:
    results = db.query(LogEntrySQL).filter(LogEntrySQL.id.in_(matching_ids)).all()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

  return {
      "count": len(results), 
      "results": results
  }