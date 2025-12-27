#pragma once

#include<string>
#include<vector>
#include<unordered_map>
#include<shared_mutex>
#include<set>

class InvertedIndex{
    private:
    //map tokenised srtings to ids, set for autsort of ids  
    std::unordered_map<std::string, std::set<long long>> index;
    //mutex fo mulitple reads but only one write
    mutable std::shared_mutex mutex_;

    public:
    InvertedIndex() = default;
    void addLog(long long logId, const std::string& message);
    std::vector<long long> search(const std::string& term);
    std::vector<std::string> tokensize(const std::string& text);
};