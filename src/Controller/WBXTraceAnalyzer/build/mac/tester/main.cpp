//
//  main.cpp
//  tester
//
//  Created by WeizhongLiang on 2021/8/9.
//

#include <iostream>
#include <fstream>
#include "WBXTraceAnalyzer.h"
#include "nlohmann/json.hpp"
using namespace nlohmann;

std::uint64_t getTickCount() {
    struct timespec ts;
    std::uint64_t theTick = 0U;
    clock_gettime( CLOCK_REALTIME, &ts );
    theTick  = ts.tv_nsec / 1000000;
    theTick += ts.tv_sec * 1000;
    return theTick;
}

int main(int argc, const char * argv[]) {
    std::string configPath = "/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoyPublic/"
        "src/Application/Assets/AndroidBoyCfg.json";
    std::string wbtPath = "/Users/weizlian/Desktop/debug log/can't hear/log-2021-0720-083628.wbt";
    std::string wbtPathErr = "/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoyPublic/src/Application/Assets/OutlookDetector/08102021_091010_adithyaasanthoshi@gmail.com/webex-trace/key-2021-0810-063026.wbt";
    std::string wbtPathErr2 = "/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoyPublic/src/Application/Assets/OutlookDetector/08102021_091010_adithyaasanthoshi@gmail.com/webex-trace/key-2021-0806-072548.wbt";
    
    std::ifstream ifs(configPath);
    json jf = json::parse(ifs);
    std::string def = jf["ViewOutlookDetector"]["errorDefinition"].dump();
    
    auto start = getTickCount();
    auto analyze = analyzeFile(wbtPathErr2.c_str());
    auto end = getTickCount();
    std::cout << "analyze:\n"
        << analyze
        << "\nin " << (end - start)/1000.0f << " seconds.\n";
    
    return 0;
}
