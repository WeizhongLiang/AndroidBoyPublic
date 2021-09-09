// tester.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <fstream>
#include <Windows.h>
#include "WBXTraceAnalyzer.h"
#include "nlohmann/json.hpp"
using namespace nlohmann;

int main(){
    std::string configPath = "..\\..\\..\\..\\Application\\Assets\\AndroidBoyCfg.json";
    std::string wbtPath = "..\\..\\..\\..\\..\\log-2021-0825-154707.wbt";

    std::ifstream ifs(configPath);
    json jf = json::parse(ifs);
    std::string def = jf["ViewOutlookDetector"]["errorDefinition"].dump();

    setErrDefine(def.c_str());
    auto start = GetTickCount64();
    auto analyze = analyzeFile(wbtPath.c_str());
    auto end = GetTickCount64();
    std::cout << "analyze:\n"
        << analyze
        << "\nin " << (end - start) / 1000.0f << " seconds.\n";

    return 0;
}

