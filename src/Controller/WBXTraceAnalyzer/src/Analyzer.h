//
//  Analyzer.hpp
//  Analyzer
//
//  Created by WeizhongLiang on 2021/8/5.
//

#ifndef Analyzer_
#define Analyzer_

#include "nlohmann/json.hpp"
using namespace nlohmann;

namespace WBXTracer{

    inline bool isLittleEnd(){ int n = 1; return *(char *)&n == 1;}
    using funTracerItem = bool(*)(std::uint32_t level, std::uint32_t pid, std::uint32_t tid, std::uint32_t id, std::uint64_t time,
                                  std::string& name, std::string& instance, std::string& message,
                                  std::uint32_t index, std::uint32_t pos, intptr_t userData);

    class WBXTraceReader{
    public:
        WBXTraceReader(funTracerItem funOnRead, intptr_t userData);
        void setCallback(funTracerItem funOnRead, intptr_t userData);
        bool readFrom(std::uint8_t* data, std::uint32_t len);
    private:
        funTracerItem   mFunOnRead;
        intptr_t        mUserData;
        bool            mIsLittleEnd;
    };

    class WBXTraceAnalyzer{
    public:
        void setErrorDefine(const char* errDefine);
        const char* analyze(std::uint8_t* data, std::uint32_t len, const char* logFileName);
        const char* analyze(const char* wbtPath, const char* logFileName);
    private:
        static bool onReadItem(std::uint32_t level, std::uint32_t pid, std::uint32_t tid, std::uint32_t id, std::uint64_t time,
                               std::string& name, std::string& instance, std::string& message,
                               std::uint32_t index, std::uint32_t pos, intptr_t userData);
        bool checkItem(std::string& message, std::uint32_t index, std::uint32_t pos);
        const char* getAnalyzeResult();
        json mJsonErrorDefine;
        json mJsonErrors;
        std::string mErrors;
        std::string mLogFileName;
    };
}

#endif
