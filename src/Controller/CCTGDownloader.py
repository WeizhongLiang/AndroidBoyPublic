import os
import re
from typing import Tuple

import requests
from requests import Response

from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Model.AppModel import appModel

startURL = "https://cctg-cirepo.cisco.com/cirepo/"
androidURL = startURL + "webex_artifacts/mobile/cctg-android/"


class RequestState(IntEnum):
    idle = 0
    succeed = 1
    failed = 2
    needAuthorization = 3
    progress = 4
    httpCode = 5


class CCTGDownloader:
    def __init__(self, onRequestState, saveDir: str, tokenName: str):
        # def onRequestState(cctg: CCTGDownloader, state: RequestState, response: Response) -> bool:
        self._mState: RequestState = RequestState.idle
        self._mOnRequestState = onRequestState
        self._mSaveDir = saveDir
        self._mTokenName = tokenName
        self._mToken = appModel.readConfig(self.__class__.__name__, self._mTokenName, "")
        self._mAuthorization = None
        self._mReqHeaders = {
            "Authorization": f"{self._mToken}",
            "Cache-Control": "max-age=0",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self._mDownloadUrl = ""
        self._mLocalPath = ""
        self._mProgress = 0
        self._mTotalLen = 0
        return

    def _setState(self, state: RequestState, response: Response) -> bool:
        self._mState = state
        if self._mOnRequestState is not None:
            return self._mOnRequestState(self, state, response)
        return False

    def _updateToken(self, token):
        if token != self._mToken:
            appModel.saveConfig(self.__class__.__name__, self._mTokenName, token)
            self._mToken = token
            Logger.d(appModel.getAppTag(), f"update self._mToken={self._mToken}")
            self._mReqHeaders = {
                "Authorization": f"{self._mToken}",
                "Cache-Control": "max-age=0",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9"
            }
        return

    def setAuth(self, auth):
        self._mAuthorization = auth
        return

    def getCurrentTask(self) -> Tuple[str, str]:
        return self._mDownloadUrl, self._mLocalPath

    def getCurrentProgress(self) -> Tuple[int, int]:
        return self._mProgress, self._mTotalLen

    @staticmethod
    def _versionToSuffix(version: str) -> Tuple[str, int, str]:
        # return main, build, suffix
        search = re.search(r"\d+\.\d+\.\d+\.\d+", version)
        if search:
            keys = search.group(0).split(".")
            mainVersion = f"{int(keys[0]):02d}.{int(keys[1]):02d}.{int(keys[2])}"
            main2 = f"{int(keys[0]):02d}{int(keys[1]):02d}{int(keys[2])}"
            main2Index = keys[3].find(main2, 0)
            if main2Index >= 0:
                buildNumber = int(keys[3][main2Index + len(main2):])
            else:
                buildNumber = int(keys[3])
            suffix = f"{mainVersion}.{buildNumber}"
            return mainVersion, buildNumber, suffix
        return "", 0, ""

    @staticmethod
    def _getMasterURL(version: str) -> Tuple[str, str]:
        # return url, suffix
        # version sample: "41.6.0.241060494"
        # url: androidURL + 41.06.0/cctg-android-41.06.0.494/
        main, build, suffix = CCTGDownloader._versionToSuffix(version)
        if len(suffix) > 0:
            url = f"{androidURL}{main}/cctg-android-{suffix}/"
            return url, suffix
        else:
            return "", ""

    @staticmethod
    def _getBranchURL(version: str, branch: str) -> Tuple[str, str]:
        # return url, suffix
        if branch is None or len(branch) == 0:
            return "", ""
        main, build, suffix = CCTGDownloader._versionToSuffix(version)
        if len(suffix) > 0:
            url = f"{androidURL}{main}.{branch}/cctg-android-{suffix}/"
            return url, suffix
        else:
            return "", ""

    def _download(self, targetUrl: str, localPath: str):
        self._mDownloadUrl = targetUrl
        self._mLocalPath = localPath
        try:
            response: Response = requests.get(targetUrl, headers=self._mReqHeaders, stream=True)
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"request failed: exception = {e}")
            self._setState(RequestState.failed, Response())
            return False
        while response.status_code == 401:
            if not self._setState(RequestState.needAuthorization, response):
                Logger.e(appModel.getAppTag(), f"authorization failed: status_code={response.status_code}")
                return False
            else:
                response = requests.get(targetUrl, headers=self._mReqHeaders, auth=self._mAuthorization, stream=True)
                if response.status_code != 401:
                    # update token
                    self._updateToken(response.request.headers.get("Authorization"))
        if not self._setState(RequestState.httpCode, response):
            Logger.i(appModel.getAppTag(), f"user cancel for http code: {response.status_code}")
            return False
        if response.status_code not in range(200, 300):
            Logger.e(appModel.getAppTag(), f"request failed: status_code={response.status_code}")
            self._setState(RequestState.failed, response)
            return False

        # get total len
        totalLength = response.headers.get("content-length")
        if totalLength is None:
            totalLength = -1
        else:
            totalLength = int(totalLength)
        self._mProgress = 0
        self._mTotalLen = totalLength
        if not self._setState(RequestState.progress, response):
            Logger.i(appModel.getAppTag(), f"request canceled: downloaded=0/{totalLength}")
            return False

        # start download
        downloaded = 0
        fSave = open(localPath, "wb")
        for data in response.iter_content(chunk_size=40960):
            fSave.write(data)
            downloaded += len(data)
            self._mProgress = downloaded
            if not self._setState(RequestState.progress, response):
                Logger.i(appModel.getAppTag(), f"request canceled: downloaded={downloaded}/{totalLength}")
                return False

        # finish
        self._setState(RequestState.succeed, response)
        return True

    def _downloadAPK(self, urlBase: str, suffix: str, release: str, localPath: str) -> bool:
        fileName = f"mc-{release}-{suffix}.apk"
        targetUrl = f"{urlBase}{fileName}"
        if localPath is None or len(localPath) == 0:
            localPath = os.path.join(self._mSaveDir, fileName)
        Logger.i(appModel.getAppTag(), f"start save {targetUrl} to {localPath}")
        return self._download(targetUrl, localPath)

    def _downloadSymbol(self, urlBase: str, suffix: str, release: str, localPath: str) -> bool:
        fileName = f"symbol-{release}-{suffix}.tar"
        targetUrl = f"{urlBase}{fileName}"
        if localPath is None or len(localPath) == 0:
            localPath = os.path.join(self._mSaveDir, fileName)
        Logger.i(appModel.getAppTag(), f"start save {targetUrl} to {localPath}")
        return self._download(targetUrl, localPath)

    def _downloadMapping(self, urlBase: str, suffix: str, release: str, localPath: str) -> bool:
        mappingSuffix = '-'.join(suffix.rsplit('.', 1))
        fileName = f"mapping-{release}-{mappingSuffix}.tar"
        targetUrl = f"{urlBase}{fileName}"
        if localPath is None or len(localPath) == 0:
            localPath = os.path.join(self._mSaveDir, fileName)
        Logger.i(appModel.getAppTag(), f"start save {targetUrl} to {localPath}")
        return self._download(targetUrl, localPath)

    def getMasterAPK(self, version: str, isRelease: bool, localPath: str) -> bool:
        urlDir, suffix = self._getMasterURL(version)
        if len(urlDir) == 0:
            Logger.e(appModel.getAppTag(), f"version={version}: failed to get url")
            return False
        Logger.i(appModel.getAppTag(), f"start download version: {version} apk...")
        if isRelease:
            return self._downloadAPK(urlDir, suffix, "release", localPath)
        else:
            return self._downloadAPK(urlDir, suffix, "debug", localPath)

    def getMasterSymbol(self, version: str, isRelease: bool, localPath: str) -> bool:
        urlDir, suffix = self._getMasterURL(version)
        if len(urlDir) == 0:
            Logger.e(appModel.getAppTag(), f"version={version}: failed to get url")
            return False
        Logger.i(appModel.getAppTag(), f"start download version: {version} symbol...")
        if isRelease:
            return self._downloadSymbol(urlDir, suffix, "pureRelease", localPath)
        else:
            return self._downloadSymbol(urlDir, suffix, "pureDebug", localPath)

    def getMasterMapping(self, version: str, isRelease: bool, localPath: str) -> bool:
        urlDir, suffix = self._getMasterURL(version)
        if len(urlDir) == 0:
            Logger.e(appModel.getAppTag(), f"version={version}: failed to get url")
            return False
        Logger.i(appModel.getAppTag(), f"start download version: {version} mapping...")
        if isRelease:
            return self._downloadMapping(urlDir, suffix, "release", localPath)
        else:
            return self._downloadMapping(urlDir, suffix, "debug", localPath)

    def getBranchAPK(self, version: str, branch: str, isRelease: bool, localPath: str) -> bool:
        urlDir, suffix = self._getBranchURL(version, branch)
        if len(urlDir) == 0:
            Logger.e(appModel.getAppTag(), f"version={version}: failed to get url")
            return False
        Logger.i(appModel.getAppTag(), f"start download version: {version} apk...")
        if isRelease:
            return self._downloadAPK(urlDir, suffix, "release", localPath)
        else:
            return self._downloadAPK(urlDir, suffix, "debug", localPath)

    def getBranchSymbol(self, version: str, branch: str, isRelease: bool, localPath: str) -> bool:
        urlDir, suffix = self._getBranchURL(version, branch)
        if len(urlDir) == 0:
            Logger.e(appModel.getAppTag(), f"version={version}: failed to get url")
            return False
        Logger.i(appModel.getAppTag(), f"start download version: {version} symbol...")
        if isRelease:
            return self._downloadSymbol(urlDir, suffix, "pureRelease", localPath)
        else:
            return self._downloadSymbol(urlDir, suffix, "pureDebug", localPath)

    def getBranchMapping(self, version: str, branch: str, isRelease: bool, localPath: str) -> bool:
        urlDir, suffix = self._getBranchURL(version, branch)
        if len(urlDir) == 0:
            Logger.e(appModel.getAppTag(), f"version={version}: failed to get url")
            return False
        Logger.i(appModel.getAppTag(), f"start download version: {version} mapping...")
        if isRelease:
            return self._downloadMapping(urlDir, suffix, "release", localPath)
        else:
            return self._downloadMapping(urlDir, suffix, "debug", localPath)
