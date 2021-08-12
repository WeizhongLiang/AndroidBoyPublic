from datetime import datetime


class ProcessTime:
    def __init__(self):
        self._mStartTime = datetime.now()

    def getSeconds(self, reset=False):
        procTime = datetime.now() - self._mStartTime
        seconds = procTime.seconds
        if reset:
            self.reset()
        return seconds

    def getMicroseconds(self, reset=False):
        procTime = datetime.now() - self._mStartTime
        microseconds = procTime.seconds + procTime.microseconds / 1000000
        if reset:
            self.reset()
        return microseconds

    def reset(self):
        self._mStartTime = datetime.now()
        return


def getNowString(fmt: any) -> str:
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.now().strftime(fmt)


def getTimestampString(timestamp: float, fmt: any) -> str:
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S.%f'
    return str(datetime.fromtimestamp(timestamp).strftime(fmt))


def getDateFromStr(timeStr: str, fmt: any) -> datetime:
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(timeStr, fmt)
