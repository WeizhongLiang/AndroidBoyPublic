import os
import string


LineSepBytes = bytes(os.linesep, encoding="utf-8")
LineSep = os.linesep
LineSepUnix = '\n'
LineSepWindows = '\r\n'


def splitBySpace(text, delete="") -> [string]:
    """Returns text with multiple whitespace reduced to single spaces
    Any characters in delete are excluded from the resultant string.
    """
    result = []
    word = []
    for char in text:
        if char in delete:
            continue
        elif char.isspace():
            if word:
                result.append("".join(word))
                word = []
        else:
            word.append(char)
    if word:
        result.append("".join(word))
    return result
