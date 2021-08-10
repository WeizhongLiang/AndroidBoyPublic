from datetime import datetime

from Crypto.Cipher import AES

from src.Common import DateTimeHelper
from src.Common.Logger import Logger
from src.Common.StructPointer import StructPointer
from src.Model.AppModel import appModel


def cryptoSimple(cryptoData: memoryview):
    outData = []
    for by in cryptoData:
        by = ~ by - 0xC5
        by = by.to_bytes(length=2, byteorder='little', signed=True)
        outData.extend((by[0],))

    return bytes(outData)


def cryptoAES128(cryptoData: memoryview, encrypt: bool):
    _aes_key = bytes([0xF1, 0x08, 0xF9, 0x16, 0x62, 0x03, 0x1B, 0xD5,
                      0xFD, 0x50, 0x44, 0x57, 0xE0, 0xA4, 0xBA, 0x1C]
                     )
    _aes_iv = bytes([0x99, 0x99, 0x34, 0x34, 0x34, 0x56, 0x56, 0x56,
                     0x56, 0x97, 0x94, 0x53, 0x44, 0x46, 0x38, 0x43
                     ])
    _aesCipher = AES.new(_aes_key, IV=_aes_iv, mode=AES.MODE_CBC)
    if encrypt:
        return _aesCipher.encrypt(cryptoData)
    else:
        return _aesCipher.decrypt(cryptoData)


def cryptoAES256B(cryptoData: memoryview, encrypt: bool):
    _aes_key = bytes([242, 223, 12, 107, 6, 85, 177, 31,
                      128, 236, 227, 103, 100, 56, 56, 159,
                      114, 53, 38, 151, 40, 252, 240, 40,
                      80, 163, 188, 44, 83, 86, 125, 246]
                     )
    _aes_iv = bytes([0x99, 0x99, 0x34, 0x34, 0x34, 0x56, 0x56, 0x56,
                     0x56, 0x97, 0x94, 0x53, 0x44, 0x46, 0x38, 0x43
                     ])
    _aesCipher = AES.new(_aes_key, IV=_aes_iv, mode=AES.MODE_CBC)
    if encrypt:
        return _aesCipher.encrypt(cryptoData)
    else:
        return _aesCipher.decrypt(cryptoData)


class WBXTraceDefine:
    ENCRYPT_NONE = b'\x00'
    ENCRYPT_SIMPLE = b'\x01'
    ENCRYPT_AES256 = b'\x02'
    ENCRYPT_AES128 = b'\x03'
    ENCRYPT_AES256B = b'\x04'

    ENCODE_AUTO = b'\00'
    ENCODE_ANSI = b'\01'
    ENCODE_UTF16_LE = b'\02'
    ENCODE_UTF16_BE = b'\03'
    ENCODE_UTF8 = b'\04'
    getEncodeStr = {
        ENCODE_AUTO: "ascii",
        ENCODE_ANSI: "ascii",
        ENCODE_UTF16_LE: "utf-16-le",
        ENCODE_UTF16_BE: "utf-16-be",
        ENCODE_UTF8: "utf-8",
    }


class _WBXTraceBomHeader(StructPointer):
    def __init__(self, data: memoryview, offset: int):
        super().__init__("4s2s", data, offset)
        self.mSignature = self._nextData()  # A 4-byte signature "WBXT"
        self.mBom = self._nextData()  # byte order mark, oxff 0xfe = little endian/pc, oxfe 0xff = big endian/unix mac
        if self.mBom == b'\xfe\xff':
            self._mEndian = ">"
        else:
            self._mEndian = "<"


class WBXTraceHeaderV3(StructPointer):
    def __init__(self, data: memoryview, offset: int):
        bomHeader = _WBXTraceBomHeader(data, offset)
        offset += 6
        self._mEndian = bomHeader.getEndian()
        super().__init__("ssHHIIIIIIIII", data, offset)
        self.mVersion = self._nextData()  # version = WBXTRA_VERSION_HEADER_V3
        self.mOS = self._nextData()  # operator system, WBXTRA_OS_WIN/WBXTRA_OS_MAC...
        self.mHeaderSize = self._nextData()  # the size of file header, in bytes
        self.mFlag = self._nextData()  # flag
        # WBXTRA_FLAG_SERIAL: serial file(mac/unix), total/number/free/border/write has no mean
        # WBXTRA_FLAG_ADDONS: addons is available, offset = this->border
        self.mTotalSize = self._nextData()  # total size of trace file
        self.mTraceCount = self._nextData()  # number of traceItem
        self.mFree = self._nextData()  # free space of circular buffer
        self.mBorder = self._nextData()  # border of circular buffer
        self.mRead = self._nextData()  # read offset
        self.mWrite = self._nextData()  # write offset
        self.mID = self._nextData()  # id
        self.mTick = self._nextData()  # tick
        self.mReserved = self._nextData()  # reserved
        return

    def size(self):
        return self.mHeaderSize


class WBXTraceItemV3(StructPointer):
    gFormatStr = "HssHssIIIIiHHHHIiI"

    indexSize = 0  # the size of this item, in bytes
    indexVersion = 1  # version = WBXTRA_VERSION_ITEM_V3
    indexReserved1 = 2  # reserved, source
    indexFlag = 3  # flag
    # WBXTRA_FLAG_ITEM_DELTA : deltaLow/deltaHigh is available
    indexEncode = 4  # dll/exe name/hint/trace msg string encode
    # WBXTRA_ENCODE_ANSI/WBXTRA_ENCODE_UTF16_LE
    indexEncrypt = 5  # dll/exe name/hint/trace msg string encrypt
    indexLevel = 6  # level, WBXTRA_LEVEL_INFO...
    indexPID = 7  # process id
    indexTID = 8  # thread id
    indexID = 9  # id
    indexTime = 10  # time
    indexMSecond = 11  # millisecond
    indexNameOffset = 12  # name offset, dll/exe name = (char*)this + this->nameOffset
    indexInstanceOffset = 13  # Instance offset, Instance = (char*)this + this->instanceOffset
    indexMessageOffset = 14  # msg offset, trace msg = (char*)this + this->msgOffset
    indexDeltaLow = 15  # accurate delta time low part
    indexDeltaHigh = 16  # accurate delta time high part
    indexReserved2 = 17  # reserved, session id/ip address

    @staticmethod
    def readItemSize(data: memoryview, endian="<", offset=0):
        data = StructPointer._readByFormat(endian + WBXTraceItemV3.gFormatStr, data, offset)
        return data[WBXTraceItemV3.indexSize]

    def __init__(self, data: memoryview, posInFile: int, index: int, endian="<"):
        self._mEndian = endian
        self.mIndex = index
        self.mPosInFile = posInFile
        super().__init__(WBXTraceItemV3.gFormatStr, data, 0)
        self.mSize = self._mStructData[self.indexSize]
        ts = self._mStructData[self.indexTime] * 1000 + self._mStructData[self.indexMSecond]
        self.mDateTime = datetime.fromtimestamp(ts / 1000)
        self.mPID = self._mStructData[self.indexPID]
        self.mTID = self._mStructData[self.indexTID]
        self.mLevel = self._mStructData[self.indexLevel]

        self.mNameOffset = self._mStructData[self.indexNameOffset]  # self.mSize
        self.mInstanceOffset = self._mStructData[self.indexInstanceOffset]
        self.mMsgOffset = self._mStructData[self.indexMessageOffset]
        self.mEncrypt = self._mStructData[self.indexEncrypt]
        self.mName = ""
        self.mInstance = ""
        self.mMessage = ""

        self._decryptData(data)
        return

    def _decryptData(self, data: memoryview):
        cryptoData = data[self.mNameOffset: self.mSize]
        logData = self._getCryptoData(cryptoData)

        # decode message
        decType = WBXTraceDefine.getEncodeStr.get(self._mStructData[self.indexEncode])
        if decType is None:
            decType = WBXTraceDefine.getEncodeStr.get(WBXTraceDefine.ENCODE_AUTO)
        nameLen = self.mInstanceOffset - self.mNameOffset
        instanceLen = self.mMsgOffset - self.mInstanceOffset
        try:
            self.mName = logData[0:nameLen].decode(decType)
            self.mInstance = logData[nameLen:instanceLen].decode(decType)
            # msgEnd = self.mSize - nameLen + instanceLen  # logData.find(b"\x00", nameLen + instanceLen)
            msgEnd = logData.find(b"\x00", nameLen + instanceLen)
            self.mMessage = logData[nameLen + instanceLen:msgEnd].decode(decType, "ignore")
        except UnicodeDecodeError as e:
            self.mMessage = f"Unknown string:{e}"
        return

    def _getCryptoData(self, cryptoData: memoryview):
        if self.mEncrypt == WBXTraceDefine.ENCRYPT_NONE:
            return cryptoData.tobytes()
        elif self.mEncrypt == WBXTraceDefine.ENCRYPT_SIMPLE:
            return cryptoSimple(cryptoData)
        elif self.mEncrypt == WBXTraceDefine.ENCRYPT_AES128:
            return cryptoAES128(cryptoData, False)
        elif self.mEncrypt == WBXTraceDefine.ENCRYPT_AES256:
            return cryptoAES256B(cryptoData, False)
        elif self.mEncrypt == WBXTraceDefine.ENCRYPT_AES256B:
            return cryptoAES256B(cryptoData, False)
        else:
            return cryptoData

    def size(self):
        return self.mSize


class WBXTracerFile:

    def __init__(self, pathOrData, isPath=True):
        self._mFileContent = None
        self._mContentLen = 0
        self._mHeader = None
        if isPath:
            self._openByPath(pathOrData)
        else:
            self._openByData(pathOrData)
        return

    def __del__(self):
        return

    def _openByPath(self, filePath):
        file = open(filePath, mode="rb")
        file.seek(0, 2)
        fileLen = file.tell()
        file.seek(0, 0)
        self._openByData(file.read(fileLen))
        file.close()
        return

    def _openByData(self, fileContent: bytes):
        # self._mFileContent = fileContent
        if len(fileContent) < 1024:
            return

        self._mFileContent = memoryview(fileContent)
        self._mHeader = self._readHeader(self._mFileContent)
        self._mContentLen = self._mHeader.mTotalSize - self._mHeader.mFree
        return

    @staticmethod
    def _calTraceCount(header: WBXTraceHeaderV3, contentData: memoryview):
        Logger.d(appModel.getAppTag(), "begin")
        itemCount = 0
        endian = header.getEndian()
        procTime = DateTimeHelper.ProcessTime()
        itemData = contentData[header.size():]
        totalSize = 0
        while len(itemData) > 0:
            itemSize = WBXTraceItemV3.readItemSize(itemData, endian)
            if itemSize <= 0:
                break
            itemData = itemData[itemSize:]
            itemCount += 1
            totalSize += itemSize
        Logger.d(appModel.getAppTag(), f"end total {itemCount} rows, size {totalSize} "
                                       f"in {procTime.getMicroseconds()} seconds ")
        return itemCount, totalSize

    def _readHeader(self, fileContent: memoryview):
        header = WBXTraceHeaderV3(fileContent, 0)
        totalSize = 0
        if header.mTraceCount == 0:
            header.mTraceCount, totalSize = self._calTraceCount(header, fileContent)
        if header.mTotalSize == 0:
            header.mTotalSize = totalSize
        return header

    def readTraces(self, onTrace, param: [any]) -> bool:
        if self._mHeader is None:
            return False
        return self.readTracesRange(onTrace, param, 0, self._mHeader.mTraceCount)

    def getHeader(self):
        return self._mHeader

    def _getItemDataByIndex(self, index: int):
        if index >= self._mHeader.mTraceCount:
            Logger.e(appModel.getAppTag(), f"index should be in (0,{self._mHeader.mTraceCount})")
            return -1, None

        Logger.d(appModel.getAppTag(), f"begin with index={index}")
        itemCount = 0
        endian = self._mHeader.getEndian()
        procTime = DateTimeHelper.ProcessTime()
        posInData = self._mHeader.size()
        itemData = self._mFileContent[posInData:]
        while len(itemData) > 0:
            if index == itemCount:
                break
            itemSize = WBXTraceItemV3.readItemSize(itemData, endian)
            if itemSize <= 0:
                break
            itemData = itemData[itemSize:]
            itemCount += 1
            posInData += itemSize
        Logger.d(appModel.getAppTag(), f"end total {itemCount} rows, posInData {posInData} "
                                       f"in {procTime.getMicroseconds()} seconds ")
        return posInData, itemData

    def readTracesRange(self, onTrace, param: [any], startIndex: int = 0, endIndex: int = -1) -> bool:
        if endIndex < 0:
            endIndex = self._mHeader.mTraceCount
        if startIndex < 0:
            startIndex = 0
        if endIndex <= startIndex:
            Logger.e(appModel.getAppTag(), f"endIndex({endIndex}) should > startIndex({startIndex}) ")
            return False

        Logger.d(appModel.getAppTag(), "begin")
        if self._mFileContent is None:
            return False
        itemCount = startIndex
        endian = self._mHeader.getEndian()
        procTime = DateTimeHelper.ProcessTime()
        curPosInData, itemData = self._getItemDataByIndex(startIndex)
        try:
            while len(itemData) > 0:
                item = WBXTraceItemV3(itemData, curPosInData, itemCount, endian)
                if item.size() <= 0:
                    break
                if onTrace is not None:
                    if not onTrace(item, param):
                        break
                itemData = itemData[item.size():]
                curPosInData += item.size()
                itemCount += 1
                if itemCount >= endIndex:
                    break
            Logger.d(appModel.getAppTag(), f"end read {itemCount - startIndex} rows "
                                           f"in {procTime.getMicroseconds()} seconds ")
            return True
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"end read {itemCount - startIndex} rows "
                                           f"in {procTime.getMicroseconds()} seconds "
                                           f"exception: {e}")
            return False

    def readForFind(self, onTrace, param: [any]) -> bool:
        Logger.d(appModel.getAppTag(), "begin")
        if self._mFileContent is None:
            return False
        itemCount = 0
        endian = self._mHeader.getEndian()
        procTime = DateTimeHelper.ProcessTime()
        curPosInData = 0
        itemData = self._mFileContent[self._mHeader.size():]
        curPosInData += self._mHeader.size()
        try:
            while len(itemData) > 0:
                item = WBXTraceItemV3(itemData, curPosInData, itemCount, endian)
                if item.size() <= 0:
                    break
                if onTrace is not None:
                    if not onTrace(item, param):
                        break
                itemData = itemData[item.size():]
                curPosInData += item.size()
                itemCount += 1
            Logger.d(appModel.getAppTag(), f"end read {itemCount} rows "
                                           f"in {procTime.getMicroseconds()} seconds ")
            return True
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"end read {itemCount} rows "
                                           f"in {procTime.getMicroseconds()} seconds "
                                           f"exception: {e}")
            return False
