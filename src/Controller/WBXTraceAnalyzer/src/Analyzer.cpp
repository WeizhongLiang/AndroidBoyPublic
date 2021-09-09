//
//  Analyzer.cpp
//  Analyzer
//
//  Created by WeizhongLiang on 2021/8/5.
//

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#pragma comment(lib, "wsock32.lib")
#define EXPORT __declspec(dllexport)

BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved
)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
#else
#define EXPORT 
#endif

#include <iostream>
#include <fstream>
#include "Analyzer.h"
#include "WBXTracer/WbxTracerDef.h"
using namespace WBXTracer;

#include "openssl/aes.h"
bool            sAESKeyReady = false;
AES_KEY         sAESKeyDec128;
AES_KEY         sAESKeyDec256;


void initWBXTracerAESKey(){
    if (!sAESKeyReady){
        BYTE aeskey128[] = WBXTRA_ENCRYPT_AES_KEY128;
        AES_set_decrypt_key(aeskey128, WBXTRA_ENCRYPT_AES_KEYSIZE128, &sAESKeyDec128);

        BYTE aeskey[] = WBXTRA_ENCRYPT_AES_KEY1;
        BYTE aeskey2[] = WBXTRA_ENCRYPT_AES_KEY2;
        for(size_t i = 0; i < sizeof(aeskey); i ++)
            aeskey[i] = (BYTE)(~(aeskey[i] ^ aeskey2[i]));
        AES_set_decrypt_key(aeskey, WBXTRA_ENCRYPT_AES_KEYSIZE, &sAESKeyDec256);
    }
}
void AESDecrypt(std::uint8_t* data, size_t len, const AES_KEY* key){
    BYTE aesiv[] = WBXTRA_ENCRYPT_AES_IV;
    AES_cbc_encrypt(data, data, len, key, aesiv, AES_DECRYPT);
}
void SimpleDecrypt(std::uint8_t* data, size_t len){
    for (int i=0; i<(std::int32_t)len; i++){
        data[i] = ~data[i] - 0xc5;
    }
}
bool decryptWbxTracerItemData(wbxtraceitem_v3* lpItem){
    BYTE* cryptoData = (BYTE*)lpItem + lpItem->nameof;
    int cryptoLen = lpItem->size - lpItem->nameof;
    switch(lpItem->encrypt){
        case WBXTRA_ENCRYPT_NONE:
            break;
        case WBXTRA_ENCRYPT_SIMPLE:
            SimpleDecrypt(cryptoData, cryptoLen);
            break;
        case WBXTRA_ENCRYPT_AES256:
            AESDecrypt(cryptoData, cryptoLen, &sAESKeyDec256);
            break;
        case WBXTRA_ENCRYPT_AES128:
            AESDecrypt(cryptoData, cryptoLen, &sAESKeyDec128);
            break;
        case WBXTRA_ENCRYPT_AES256B:
            AESDecrypt(cryptoData, cryptoLen, &sAESKeyDec256);
            break;
    }
    return true;
}


WBXTraceReader::WBXTraceReader(funTracerItem funOnRead, intptr_t userData){
    initWBXTracerAESKey();
    mIsLittleEnd = isLittleEnd();
    setCallback(funOnRead, userData);
}

void WBXTraceReader::setCallback(funTracerItem funOnRead, intptr_t userData){
    mFunOnRead = funOnRead;
    mUserData = userData;
}

void convert2Little(wbxtraceheader_v3* lpHeader){
    lpHeader->size = htons(lpHeader->size);
    lpHeader->flag = htons(lpHeader->flag);
    
    lpHeader->total = htonl(lpHeader->total);
    lpHeader->number = htonl(lpHeader->number);
    lpHeader->free = htonl(lpHeader->free);
    lpHeader->border = htonl(lpHeader->border);
    lpHeader->read = htonl(lpHeader->read);
    lpHeader->write = htonl(lpHeader->write);
    lpHeader->id = htonl(lpHeader->id);
    lpHeader->tick = htonl(lpHeader->tick);
    lpHeader->reserved = htonl(lpHeader->reserved);
}
void convert2Little(wbxtraceitem_v3* lpItem){
    lpItem->size = htons(lpItem->size);
    lpItem->flag = htons(lpItem->flag);
    
    lpItem->level = htonl(lpItem->level);
    lpItem->pid = htonl(lpItem->pid);
    lpItem->tid = htonl(lpItem->tid);
    lpItem->id = htonl(lpItem->id);
    lpItem->time = htonl(lpItem->time);
    
    lpItem->millitm = htons(lpItem->millitm);
    lpItem->nameof = htons(lpItem->nameof);
    lpItem->hintof = htons(lpItem->hintof);
    lpItem->msgof = htons(lpItem->msgof);
    
    lpItem->deltalow = htonl(lpItem->deltalow);
    lpItem->deltahigh = htonl(lpItem->deltahigh);
    lpItem->reserved2 = htonl(lpItem->reserved2);
}

bool WBXTraceReader::readFrom(std::uint8_t* data, std::uint32_t len){
    if (data==nullptr || len<=0 || mFunOnRead==nullptr){
        return false;
    }
    
    std::int32_t leftLen = len;
    const std::uint8_t* curData = data;
    int sHeaderLen = sizeof(wbxtraceheader_v3);
    int sItemLen = sizeof(wbxtraceitem_v3);
    int itemCount = 0;
    wbxtraceheader_v3* lpFileHeader = (wbxtraceheader_v3*)curData;
    if (mIsLittleEnd){
        convert2Little(lpFileHeader);
    }
    if (lpFileHeader->version!=WBXTRA_VERSION_HEADER_V3){
        return false;
    }
    leftLen -= sHeaderLen;
    curData += sHeaderLen;
    while (leftLen > sItemLen){
        wbxtraceitem_v3* lpItem = (wbxtraceitem_v3*)curData;
        if (mIsLittleEnd) {
            convert2Little(lpItem);
            if (lpItem->version != WBXTRA_VERSION_ITEM_V3) {
                return false;
            }
        }
        if (lpItem->size > leftLen) {
            lpItem->size = leftLen;
        }
        decryptWbxTracerItemData(lpItem);

        std::uint32_t itemIndex = itemCount;
        std::uint64_t itemTime = (std::uint64_t)lpItem->time * 1000 + (std::uint64_t)lpItem->millitm;
        std::uint32_t itemPosInFile = (std::uint32_t)(curData - data);
        int nameLen = lpItem->hintof - lpItem->nameof;
        int instanceLen = lpItem->msgof - lpItem->hintof;
        int msgLen = lpItem->size - lpItem->msgof;
        if (nameLen < 0 || instanceLen < 0 || msgLen < 0) {
            return false;
        }
        std::string name((const char*)(curData + lpItem->nameof), nameLen);
        std::string instance((const char*)(curData + lpItem->hintof), instanceLen);
        std::string message((const char*)(curData + lpItem->msgof), msgLen);
        if (mFunOnRead(lpItem->level, lpItem->pid, lpItem->tid, lpItem->id, itemTime,
            name, instance, message, itemIndex, itemPosInFile,
            mUserData) == false) {
            return false;
        }
        leftLen -= lpItem->size;
        curData += lpItem->size;
        itemCount++;
    }
    return true;
}


const char* WBXTraceAnalyzer::analyze(std::uint8_t* data, std::uint32_t len, const char* logFileName){
    mLogFileName = logFileName;
    mJsonErrors = json::parse("{}");
    WBXTraceReader reader(onReadItem, (intptr_t)this);
    reader.readFrom(data, len);
    return getAnalyzeResult();
}
const char* WBXTraceAnalyzer::analyze(const char* wbtPath, const char* logFileName){
    std::ifstream fileHandle;
    fileHandle.open(wbtPath, std::ios::binary);
    fileHandle.seekg(0, std::ios::end);
    auto fileLen = fileHandle.tellg();
    std::uint8_t* byBuffer = nullptr;
    fileHandle.seekg(0, std::ios::beg);
    if (fileLen>0){
        byBuffer = new std::uint8_t[(std::int32_t)fileLen];
        fileHandle.read((char*)byBuffer, fileLen);
    }
    fileHandle.close();
        
    return analyze(byBuffer, (std::uint32_t)fileLen, logFileName);
}
bool WBXTraceAnalyzer::onReadItem(std::uint32_t level, std::uint32_t pid, std::uint32_t tid, std::uint32_t id,
                                  std::uint64_t time,
                                  std::string& name, std::string& instance, std::string& message,
                                  std::uint32_t index, std::uint32_t pos, intptr_t userData){
    WBXTraceAnalyzer* analyzer = (WBXTraceAnalyzer*)userData;
    return analyzer->checkItem(message, index, pos);
}

bool WBXTraceAnalyzer::checkItem(std::string& message, std::uint32_t index, std::uint32_t pos){
    if (mJsonErrorDefine.size()==0){
        return false;
    }
    for (const auto& item : mJsonErrorDefine.items()){
        if (message.find(item.key())!=message.npos){
            auto key = item.key();
            auto value = item.value();
            mJsonErrors[key]["errName"] = value.at(0);
            mJsonErrors[key]["errType"] = value.at(1);
            mJsonErrors[key]["logIndex"] = index;
            mJsonErrors[key]["logPos"] = pos;
            mJsonErrors[key]["logFile"] = mLogFileName;
            mJsonErrorDefine.erase(key);
            return true;
        }
    }
    return true;
}
void WBXTraceAnalyzer::setErrorDefine(const char* errDefine){
    mJsonErrorDefine = json::parse(errDefine);
    return;
}
const char* WBXTraceAnalyzer::getAnalyzeResult(){
    if (mJsonErrors.size()==0){
        mErrors = "{}";
    }
    else{
        mErrors = mJsonErrors.dump();
    }
    return mErrors.c_str();
}

WBXTracer::WBXTraceAnalyzer sAnalyzer;
#ifdef __APPLE__
#pragma GCC visibility push(default)
#endif
extern "C"  {
    EXPORT void setErrDefine(const char* errDefine){
        sAnalyzer.setErrorDefine(errDefine);
    }
    EXPORT const char* analyzeData(std::uint8_t* data, std::uint32_t len, const char* logFileName){
        return sAnalyzer.analyze(data, len, logFileName);
    }
    EXPORT const char* analyzeFile(const char* wbtPath){
        return sAnalyzer.analyze(wbtPath, wbtPath);
    }
}
#ifdef __APPLE__
#pragma GCC visibility pop
#endif

