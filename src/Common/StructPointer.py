import struct


class StructPointer:
    _mEndian = "="
    _mFormat = ""
    _mLen = 0
    _mCurIndex = -1
    _mStructData = []

    @staticmethod
    def _readByFormat(formatStr: str, data: memoryview, offset: int):
        return struct.unpack_from(formatStr, data, offset)

    def __init__(self, formatStr: str, data: memoryview, offset: int):
        self._mFormat = self._mEndian + formatStr
        self._mLen = struct.calcsize(self._mFormat)
        self._mCurIndex = -1
        self._mStructData = struct.unpack_from(self._mFormat, data, offset)
        return

    def _nextData(self):
        self._mCurIndex += 1
        return self._mStructData[self._mCurIndex]

    def size(self):
        return self._mLen

    def __len__(self):
        return self.size()

    def getEndian(self):
        return self._mEndian

    def getRawData(self, index: int):
        return self._mStructData[index]
