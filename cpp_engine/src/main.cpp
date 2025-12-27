#include <iostream>
#include <string>
#include <vector>
#include <zmq.hpp>
#include <nlohmann/json.hpp>
#include "InvertedIndex.h"

using json = nlohmann::json;

int main(){
  zmq::context_t context(1);
  zmq::socket_t socket(context, ZMQ_REP);

  std::cout << "C++ engine started on tcp://*:5555..." << std::endl;
  socket.bind("tcp://*:5555");

  InvertedIndex engine;

  while(true){
    zmq::message_t request;

    auto result = socket.recv(request, zmq::recv_flags::none);

    std::string req_str(static_cast<char*>(request.data()), request.size());
    std::cout << "[DEBUG] Received: " << req_str << std::endl;

    json response_json;
    
    try{
      auto req_json = json::parse(req_str);
      std::string command = req_json["command"];

      if(command=="ADD"){
        long long id = req_json["id"];
        std::string text = req_json["text"];
        std::cout << "[DEBUG] Indexing ID: " << id << " | Text: " << text << std::endl;

        engine.addLog(id, text);

        response_json["status"] = "OK";
        response_json["message"] = "Log indexed";
      } 
      else if(command=="SEARCH"){
        std::string term = req_json["term"];
        std::cout << "[DEBUG] Searching for term: " << term << std::endl;

        std::vector<long long> results = engine.search(term);
        std::cout << "[DEBUG] Found " << results.size() << " matches." << std::endl;

        response_json["status"] = "OK";
        response_json["results"] = results;
      }
      else{
        std::cout << "[DEBUG] Unknown command: " << command << std::endl;
        response_json["status"] = "ERROR";
        response_json["message"] = "Unknown command";
      }
    }
    catch(const std::exception& e){
      std::cerr << "[C++] Error processing request : " << e.what() << std::endl;
      response_json["status"] = "ERROR";
      response_json["message"] = e.what();
    }

    std::string dump = response_json.dump();
    zmq::message_t reply(dump.data(), dump.size());
    socket.send(reply, zmq::send_flags::none);
  }

  return 0;
}
