#include <iostream>
#include <string>
#include <vector>
#include <zmq.hpp>
#include <nlohmann/json.hpp>
#include "InvertedIndex.h"

using json = nlohmann::json;

int main(){
  zmq::context_t context(1);
  
  zmq::socket_t search_socket(context, ZMQ_REP);
  search_socket.bind("tcp://*:5555");

  zmq::socket_t ingest_socket(context, ZMQ_SUB);
  ingest_socket.set(zmq::sockopt::rcvhwm, 10000);
  ingest_socket.set(zmq::sockopt::subscribe, "");
  ingest_socket.connect("tcp://127.0.0.1:5556");

  std::cout << "[C++] Engine Running..." << std::endl;
  std::cout << "      - Listening for Logs on Port 5556 (SUB)" << std::endl;
  std::cout << "      - Ready for Searches on Port 5555 (REP)" << std::endl;

  // Use a Poller to listen to both sockets at once
  zmq::pollitem_t items[] = {
      { search_socket, 0, ZMQ_POLLIN, 0 },
      { ingest_socket, 0, ZMQ_POLLIN, 0 }
  };

  InvertedIndex index;

  while (true) {
        // Poll with -1 timeout (infinite wait until an event happens)
        zmq::poll(items, 2, -1);

        // --- Event 1: Search Request Received ---
        if (items[0].revents & ZMQ_POLLIN) {
            zmq::message_t request;
            search_socket.recv(request, zmq::recv_flags::none);
            
            // Parse Request
            std::string req_str = request.to_string();
            auto req_json = json::parse(req_str);
            
            if (req_json["command"] == "SEARCH") {
                std::string term = req_json["term"];
                std::vector<long long> results = index.search(term);

                // Send Result back to Python
                json response;
                response["status"] = "OK";
                response["results"] = results;
                
                std::string reply_str = response.dump();
                search_socket.send(zmq::buffer(reply_str), zmq::send_flags::none);
            }
        }

        // --- Event 2: New Log Arrived ---
        if (items[1].revents & ZMQ_POLLIN) {
            zmq::message_t log_msg;
            ingest_socket.recv(log_msg, zmq::recv_flags::none);

            // Parse Log
            std::string log_str = log_msg.to_string();
            try {
                auto log_json = json::parse(log_str);

                // Extract fields needed for Indexing
                long long id = log_json["id"];
                std::string message = log_json["message"];

                // Update In-Memory Index
                index.addLog(id, message);
                std::cout << "[Index]Indexed Log: " << id << std::endl; // Debug
            } 
            catch (json::parse_error& e) {
                std::cerr << "JSON Error: " << e.what() << std::endl;
            }
        }
    }

    return 0;
}
