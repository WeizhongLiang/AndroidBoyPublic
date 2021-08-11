//
//  WbxTracerDef.h
//  WBXTraceAnalyzer
//
//  Created by WeizhongLiang on 2021/8/9.
//

#ifndef WbxTracerDef_h
#define WbxTracerDef_h


#define WBXTRA_OS_WIN                       1
#define WBXTRA_OS_MAC                       2
#define WBXTRA_OS_LINUX                     3
#define WBXTRA_OS_SOLARIS                   4
#define WBXTRA_OS_JAVA                      5
#define WBXTRA_OS_WINCE                     6

#define WBXTRA_FLAG_SERIAL                  1
#define WBXTRA_FLAG_ADDONS                  2            //useless

#define WBXTRA_FLAG_ITEM_DELTA              1
#define WBXTRA_FLAG_ITEM_SOURCE             2

////////////////////////////////////////////////////////////////////
#define WBXTRA_ENCODE_AUTO                  0
#define WBXTRA_ENCODE_ANSI                  1
#define WBXTRA_ENCODE_UTF16_LE              2
#define WBXTRA_ENCODE_UTF16_BE              3
#define WBXTRA_ENCODE_UTF8                  4

////////////////////////////////////////////////////////////////////
#define WBXTRA_ENCRYPT_NONE                 0
#define WBXTRA_ENCRYPT_SIMPLE               1
#define WBXTRA_ENCRYPT_AES256               2
#define WBXTRA_ENCRYPT_AES128               3
#define WBXTRA_ENCRYPT_AES256B              4
#define WBXTRA_ENCRYPT_AES_KEYSIZE          256
#define WBXTRA_ENCRYPT_AES_KEY1             {0x05, 0x43, 0x18, 0x01, 0x2B, 0xB6, 0x4F, 0x85, 0x84, 0x31, 0x50, 0xA7, 0xEE, 0x8C, 0x19, 0xE1, \
        0xCD, 0x77, 0x01, 0x4D, 0xE9, 0x9F, 0xB3, 0x85, 0xEC, 0x7C, 0x30, 0x76, 0x7B, 0x11, 0x04, 0x15}
#define WBXTRA_ENCRYPT_AES_KEY2             {0x08, 0x63, 0xEB, 0x95, 0xD2, 0x1C, 0x01, 0x65, 0xFB, 0x22, 0x4C, 0x3F, 0x75, 0x4B, 0xDE, 0x81, \
        0x40, 0xBD, 0xD8, 0x25, 0x3E, 0x9C, 0xBC, 0x52, 0x43, 0x20, 0x73, 0xA5, 0xD7, 0xB8, 0x86, 0x1C}

#define WBXTRA_ENCRYPT_AES_KEY128           {0xF1, 0x08, 0xF9, 0x16, 0x62, 0x03, 0x1B, 0xD5, 0xFD, 0x50, 0x44, 0x57, 0xE0, 0xA4, 0xBA, 0x1C}
#define WBXTRA_ENCRYPT_AES_KEYSIZE128       128

#define WBXTRA_ENCRYPT_AES_BLOCK            16
#define WBXTRA_ENCRYPT_AES_IV               {0x99, 0x99, 0x34, 0x34, 0x34, 0x56, 0x56, 0x56, 0x56, 0x97, 0x94, 0x53, 0x44, 0x46, 0x38, 0x43}

////////////////////////////////////////////////////////////////////
#define WBXTRA_ITEM_NAME_MAX                128                 //trace item max dll name length, in tchars
#define WBXTRA_ITEM_HINT_MAX                128                 //trace item max hint length, in tchars
#define WBXTRA_ITEM_MSG_MAX                 (2 * 1024)          //trace item max trace msg length, in tchars

////////////////////////////////////////////////////////////////////
#define WBXTRA_MAPFILE_SIZE1                (256 * 1024)        //can save about 1000-1500 trace item
#define WBXTRA_MAPFILE_SIZE2                (512 * 1024)        //default map file size, can save about 2000-3000 trace item
#define WBXTRA_MAPFILE_SIZE3                (1024 * 1024)       //can save about 4000-6000 trace item
#define WBXTRA_MAPFILE_SIZE4                (2 * 1024 * 1024)   //can save about 8000-12000 trace item
#define WBXTRA_MAPFILE_SIZE                 WBXTRA_MAPFILE_SIZE4

#define WBXTRA_MAPFILE_FORMAT               _T("wbxtra_%02hu%02hu%04hu_%02hu%02hu%02hu.wbt")
#define WBXTRA_MAPFILE_PATT                 _T("wbxtra_*.wbt")
#define WBXTRA_MAPFILE_MAX                  5

#define WBXTRA_LOCAL_MUTEX                  _T("WBXTRA_TRACE_MUTEX")        //windows local session trace access mutex
#define WBXTRA_LOCAL_MUTEX_EX               _T("WBXTRA_TRACE_MUTEX_EX")     //windows local session trace access mutex for max size >1M

#define WBXTRA_LOCAL_EVENT                  _T("WBXTRA_TRACE_EVENT")        //windows local session trace ready event
#define WBXTRA_LOCAL_EVENT_EX               _T("WBXTRA_TRACE_EVENT_EX")     //windows local session trace ready event for max size >1M

#define WBXTRA_LOCAL_FILE                   _T("WBXTRA_TRACE_FILE")         //windows local session mapfile name
#define WBXTRA_LOCAL_FILE_EX                _T("WBXTRA_TRACE_FILE_EX")      //windows local session mapfile name for max size >1M


#define WBXTRA_GLOBAL_MUTEX                 _T("Global\\WBXTRA_TRACE_MUTEX")     //windows global session trace access mutex
#define WBXTRA_GLOBAL_MUTEX_EX              _T("Global\\WBXTRA_TRACE_MUTEX_EX")   //windows global session trace access mutex for max size >1M

#define WBXTRA_GLOBAL_EVENT                 _T("Global\\WBXTRA_TRACE_EVENT")     //windows global session trace ready event
#define WBXTRA_GLOBAL_EVENT_EX              _T("Global\\WBXTRA_TRACE_EVENT_EX")   //windows global session trace ready event for max size >1M

#define WBXTRA_GLOBAL_FILE                  _T("Global\\WBXTRA_TRACE_FILE")       //windows global session mapfile name
#define WBXTRA_GLOBAL_FILE_EX               _T("Global\\WBXTRA_TRACE_FILE_EX")     //windows global session mapfile namefor max size >1M

#define WBXTRA_FLT_STATUS_IDLE              0
#define WBXTRA_FLT_STATUS_DIRTY             1
#define WBXTRA_FLT_STATUS_SEARCH            2

#define WBXTRA_FILE_TYPE_AUTO               -1
#define WBXTRA_FILE_TYPE_LE                 0
#define WBXTRA_FILE_TYPE_BE                 1

#define WBXTRA_WTN_MESSAGE                  WM_APP
#define WBXTRA_WTN_CAPTURE                  0

#define WBXTRA_WTN_CAPTURE_SUCCESS          0
#define WBXTRA_WTN_CAPTURE_REFRESH          1

#define WBXTRA_WTN_CAPTURE_TIMER            1000
#define WBXTRA_WTN_WBXMAPFILE_DELAY         100
#define WBXTRA_WTN_MUTEX_WAIT               50
#define WBXTRA_WTN_WBXMUTEX_WAIT            25

#define WBXTRA_MESSAGE_BUFFER_SIZE          (2 * 1024)
#define WBXTRA_MESSAGE_DATA_SIZE            1024

#define WBXTRA_ITEM_MAX_SIZE                (12 * 1024)

#define WBXTRA_ITEM_SOURCE_DEFAULT          0
#define WBXTRA_ITEM_SOURCE_WBX              1
#define WBXTRA_ITEM_SOURCE_MESSAGE          2
#define WBXTRA_ITEM_SOURCE_GPC              3
#define WBXTRA_ITEM_SOURCE_DBWIN            4
#define WBXTRA_ITEM_SOURCE_WTC              5
#define WBXTRA_ITEM_SOURCE_WTV              6

#define WBXTRA_TIME_SORT_DELAY              2

////////////////////////////////////////////////////////////////////
#define WBXTRA_VERSION_HEADER_V3            3
#define WBXTRA_VERSION_ITEM_V3              3
#define WBXTRA_VERSION_ADDONS_V3            3

#define WBXTRA_SIGNATURE                    "WBXT"

//////////////////////////////////////////////////////////////////////////
#define WBXTRACK_MAPFILE_FORMAT             _T("wbxtrack_%02hu%02hu%04hu_%02hu%02hu%02hu.log")
#define WBXTRACK_MAPFILE_PATT               _T("wbxtrack_*.log")
#define WBXTTRACK_MAPFILE_SIZE              (4*1024*1024)


// add by weizlian begin
#ifndef        SAFE_FREE
#define        SAFE_FREE(pMem)              if(pMem){free(pMem);pMem=NULL;}
#endif
#ifndef        SAFE_DELETE
#define        SAFE_DELETE(pMem)            if(pMem){delete pMem;pMem=NULL;}
#endif
#ifndef        SAFE_DELETE_A
#define        SAFE_DELETE_A(pMem)          if(pMem){delete [] pMem;pMem=NULL;}
#endif
#ifndef        SAFE_DELETE_T
#define        SAFE_DELETE_T(pMem,Type)     if(pMem){delete (Type *)pMem;pMem=NULL;}
#endif
#ifndef        SAFE_CLOSE_A
#define        SAFE_CLOSE_A(pMem)           if(pMem){pMem->Close();delete(pMem);pMem=NULL;}
#endif
#ifndef        SAFE_CLOSE_B
#define        SAFE_CLOSE_B(pMem)           if(pMem){pMem->Close();pMem=NULL;}
#endif
#ifndef        SAFE_RELEASE_A
#define        SAFE_RELEASE_A(pMem)         if(pMem){pMem->Release();delete(pMem);pMem=NULL;}
#endif
#ifndef        SAFE_RELEASE_B
#define        SAFE_RELEASE_B(pMem)         if(pMem){pMem->Release();pMem=NULL;}
#endif
// stl support begin
#if (defined _WIN32) || (defined _WIN64)
    #pragma warning(disable:4100)
    #pragma warning(disable:4189)
    #pragma warning(disable:4541)
    #pragma warning(disable:4786)
#endif
#include <string>
#include <list>
#include <map>
#include <vector>
using namespace std;
// stl support end
#ifndef _WINDEF_
typedef std::uint8_t BYTE;
typedef std::uint16_t WORD;
typedef std::uint32_t DWORD;
typedef std::int8_t TCHAR;
typedef std::int32_t LONG;
typedef std::int32_t BOOL;
typedef TCHAR* LPTSTR;
#else
#endif // _WINDEF_
typedef enum
{
    eJTErrSuccess    = 0,
    eJTErrParam      = 1,
    eJTErrInvalid    = 2,
}eJTError;
// add by weizlian end

#pragma pack(push, 4)
////////////////////////////////////////////////////////////////////wbxtraceheader_v3
//trace file header
struct wbxtraceheader_v3
{
    BYTE            signature[4];           //A 4-byte signature "WBXT"
    BYTE            bom[2];                 //byte order mark, oxff 0xfe = litten endian/pc, oxfe 0xff = big endian/unix mac
    BYTE            version;                //version = WBXTRA_VERSION_HEADER_V3
    BYTE            os;                     //operator system, WBXTRA_OS_WIN/WBXTRA_OS_MAC...
    WORD            size;                   //the size of file header, in bytes
    WORD            flag;                   //flag
                                            //WBXTRA_FLAG_SERIAL: serial file(mac/unix), total/number/free/border/write has no mean
                                            //WBXTRA_FLAG_ADDONS: addons is available, offset = this->border
    DWORD            total;                 //total size of trace file
    DWORD            number;                //number of traceitem
    DWORD            free;                  //free space of circular buffer
    DWORD            border;                //border of circular buffer
    DWORD            read;                  //read offset
    DWORD            write;                 //write offset
    DWORD            id;                    //id
    DWORD            tick;                  //tick
    DWORD            reserved;              //reserved
    //BYTE            data[ANY_SIZE];       //traceitems, traceitem 0 = (char*)this + this->read
};

////////////////////////////////////////////////////////////////////wbxtraceitem_v3
//trace item
struct wbxtraceitem_v3
{
    WORD            size;                   //the size of this item, in bytes
    BYTE            version;                //version = WBXTRA_VERSION_ITEM_V3
    BYTE            reserved1;              //reserved, source
    WORD            flag;                   //flag
                                            //WBXTRA_FLAG_ITEM_DELTA : deltalow/deltahigh is available
    BYTE            encode;                 //dll/exe name/hint/trace msg string encode
                                            //WBXTRA_ENCODE_ANSI/WBXTRA_ENCODE_UTF16_LE
    BYTE            encrypt;                //dll/exe name/hint/trace msg string encrypt
                                            //WBXTRA_ENCRYPT_NONE/WBXTRA_ENCRYPT_DEFAULT
    DWORD            level;                 //level, WBXTRA_LEVEL_INFO...
    DWORD            pid;                   //process id
    DWORD            tid;                   //thread id
    DWORD            id;                    //id
    LONG            time;                   //time
    WORD            millitm;                //millisecond
    WORD            nameof;                 //name offset, dll/exe name = (char*)this + this->nameof
    WORD            hintof;                 //hint offset, hint = (char*)this + this->hintof
    WORD            msgof;                  //msg offset, trace msg = (char*)this + this->msgof
    DWORD            deltalow;              //accurate delta time low part
    LONG            deltahigh;              //accurate delta time high part
    DWORD            reserved2;             //reserved, session id/ip address
    //BYTE            data[ANY_SIZE];       //dll name/hint/trace msg
};

////////////////////////////////////////////////////////////////////wbxtraceaddons_v3
//trace file addons, useless
struct wbxtraceaddons_v3
{
    DWORD            size;                  //size
    BYTE            version;                //version = WBXTRA_VERSION_ADDONS_V3
    BYTE            reserved1;              //reserved1
    BYTE            encode;                 //addons encode
    BYTE            encrypt;                //addons encrypt
    WORD            nameof;                 //addons name offset
    WORD            msgof;                  //addons msg offset
    DWORD            reserved2;             //reserved2
    //BYTE            data[ANY_SIZE];
};

//////////////////////////////////////////////////////////////////////////
// For Feature tracking task;
#define WBXFEAT_SIGNATURE                    _T("WBXF")
#define    WBXTRACK_FEATRUE_ITEM_MAX         (1024*2)
#define WBXTRA_FEATURE_TRACK_HEADER_SIZE     (1024*4)    //Reserve 4k for feature track header;
struct wbxfeaturetrackheader
{
    BYTE            signature[4];           //A 4-byte signature "WBXT"
    BYTE            bom[2];                 //byte order mark, oxff 0xfe = litten endian/pc, oxfe 0xff = big endian/unix mac
    BYTE            version;                //version = WBXTRA_VERSION_HEADER_V3
    BYTE            os;                     //operator system, WBXTRA_OS_WIN/WBXTRA_OS_MAC...
    WORD            size;                   //the size of file header, in bytes
    DWORD            dwTimeOut;
    DWORD            dwConfID;
    DWORD            number;                // Track number
    DWORD           trackstart;             // start address of track content
    DWORD            trackend;              // End address of track content
    char            szUrl[512];             // The URL for upload trace
    char            szToken[512];
};

//////////////////////////////////////////////////////////////////////////
// For Filter
// Filter Definition
#define    TFILTER_MAX_STR_LEN              32
#define    TFILTER_MAX_COMBO                8
typedef struct stFilterDefinition
{
    char    m_szFilterName[TFILTER_MAX_STR_LEN];
    char    m_szContent[TFILTER_MAX_STR_LEN];
    char    m_szModel[TFILTER_MAX_STR_LEN];
    char    m_szName[TFILTER_MAX_STR_LEN];
    DWORD    m_dwPID[TFILTER_MAX_COMBO];
    DWORD    m_dwTID[TFILTER_MAX_COMBO];
    DWORD    m_dwLevel[TFILTER_MAX_COMBO];

    int HasPID(DWORD dwPID)
    {
        // to do
        if ( dwPID==0 ) return 0;
        for (int i=0; i<TFILTER_MAX_COMBO; i++)
        {
            if (m_dwPID[i]==dwPID) return 1;
        }
        return 0;
    }
    int HasTID(DWORD dwTID)
    {
        // to do
        if ( dwTID==0 ) return 0;
        for (int i=0; i<TFILTER_MAX_COMBO; i++)
        {
            if (m_dwTID[i]==dwTID) return 1;
        }
        return 0;
    }
    int HasLevel(DWORD dwLevel)
    {
        // to do
        if ( dwLevel==0 ) return 0;
        for (int i=0; i<TFILTER_MAX_COMBO; i++)
        {
            if (m_dwLevel[i]==dwLevel) return 1;
        }
        return 0;
    }
}* PSTFilterDefinition;
// Filter Report Item
typedef struct stFilterItem
{
    DWORD        m_dwID;                    // id
    DWORD        m_dwLevel;                 // level, WBXTRA_LEVEL_INFO...
    DWORD        m_dwPID;                   // process id
    DWORD        m_dwTID;                   // thread id
    LONG        m_tTime;                    // time
    LONG        m_lDataOffset;              // data offset
    WORD        m_wMillitm;                 // millisecond
    WORD        m_wNameLen;                 // name len
    WORD        m_wHintLen;                 // hint len
    WORD        m_wMsgLen;                  // msg len
}* PSTFilterItem;
// Filter Report
typedef class CFilterReport
{
public:
    stFilterDefinition      m_stFilter;
    int                     m_iCurIndex;
    list<PSTFilterItem>     m_ltReport;
    list<PSTFilterItem>::iterator    m_itorCur;
public:
    CFilterReport()
    {
        Clear();
    }
    ~CFilterReport()
    {
        Clear();
    }
    void ClearData()
    {
        m_iCurIndex    = -1;
        m_ltReport.clear();
        m_itorCur = m_ltReport.begin();
    }
    void Clear()
    {
        memset(&m_stFilter,0,sizeof(m_stFilter));
        ClearData();
    }
    void ResetItor()
    {
        m_iCurIndex    = -1;
        m_itorCur = m_ltReport.begin();
    }
}* LPFilterReport;
typedef map<string,LPFilterReport>                t_mapFilterReport;
typedef map<string,LPFilterReport>::value_type    t_valueFilterReport;
typedef map<string,LPFilterReport>::iterator    t_itorFilterReport;
#pragma pack(pop)

#endif /* WbxTracerDef_h */
