#include "InvertedIndex.h"
#include <sstream>
#include <algorithm>
#include <cctype>
#include <vector>
#include <mutex>

std::vector<std::string> InvertedIndex::tokensize(const std::string& text){
  std::vector<std::string> tokens;
  std::string cleanText;
  
  for(char c : text){
    if(std::isalnum(c) || std::isspace(c)) cleanText+=std::tolower(c);
    else cleanText += ' ';
  }

  std::stringstream ss(cleanText);
  std::string word;
  
  while(ss >> word){
    if(!word.empty())tokens.push_back(word);
  }
  
  return tokens;
}

void InvertedIndex::addLog(long long logId, const std::string& message){
  std::vector<std::string> tokens = tokensize(message);

  std::unique_lock<std::shared_mutex> lock(mutex_);

  for(const auto& token : tokens)
    index[token].insert(logId);
}

std::vector<long long> InvertedIndex::search(const std::string& term){
  std::string query = term;
  
  std::transform(query.begin(), query.end(), query.begin(), ::tolower);

  std::shared_lock<std::shared_mutex> lock(mutex_);

  if(index.find(query)!=index.end())return std::vector<long long>(index[query].begin(), index[query].end());
  else return {};
}
