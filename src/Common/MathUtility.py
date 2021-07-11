import numpy as np


def getAmplitude(prevValue, value):
    return (value - prevValue) / prevValue


def getDiffInLists(listBase, listNew):
    added = np.setdiff1d(listNew, listBase)
    removed = np.setdiff1d(listBase, listNew)
    return added, removed
