#include "InvertedIndex.h"
#include <algorithm>
#include <cctype>
#include <vector>
#include <mutex>

// OPTIMIZED: Single-pass tokenization without stringstream overhead
std::vector<std::string> InvertedIndex::tokensize(const std::string& text){
  std::vector<std::string> tokens;
  std::string currentToken;
  // Reserve memory to prevent re-allocations for average word length
  currentToken.reserve(32); 

  for(char c : text){
    if(std::isalnum(c)){
        // If it's a letter/number, build the word
        currentToken += std::tolower(c);
    } else {
        // If it's a separator (space, symbol, etc.), push the completed word
        if(!currentToken.empty()){
            tokens.push_back(currentToken);
            currentToken.clear();
        }
    }
  }
  
  // Don't forget the last word if the string doesn't end with a space
  if(!currentToken.empty()){
      tokens.push_back(currentToken);
  }
  
  return tokens;
}

void InvertedIndex::addLog(long long logId, const std::string& message){
  // Tokenize OUTSIDE the lock to keep the critical section small
  std::vector<std::string> tokens = tokensize(message);

  std::unique_lock<std::shared_mutex> lock(mutex_);

  for(const auto& token : tokens) {
    // Assuming 'index' is std::map or std::unordered_map<std::string, std::vector<long long>>
    // If it's std::set, .insert() is fine. If it's std::vector, use .push_back() for speed!
    index[token].insert(logId); 
  }
}

std::vector<long long> InvertedIndex::search(const std::string& term){
  std::string query = term;
  
  // Optimize: Lowercase in place
  std::transform(query.begin(), query.end(), query.begin(), ::tolower);

  std::shared_lock<std::shared_mutex> lock(mutex_);

  auto it = index.find(query);
  if(it != index.end()){
      // Return copy of the list
      return std::vector<long long>(it->second.begin(), it->second.end());
  }
  return {};
}