//
//  WBXTraceAnalyzer.hpp
//  WBXTraceAnalyzer
//
//  Created by WeizhongLiang on 2021/8/5.
//

#ifndef WBXTraceAnalyzer_
#define WBXTraceAnalyzer_

// Functions below are exported
#pragma GCC visibility push(default)
extern "C"  {
void setErrDefine(const char* errDefine);
const char* analyzeData(std::uint8_t* data, std::uint32_t len, const char* logFileName);
const char* analyzeFile(const char* wbtPath);
}
#pragma GCC visibility pop
#endif
