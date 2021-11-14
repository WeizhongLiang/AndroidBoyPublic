import re
import webbrowser
from typing import Tuple

import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from src.Layout.dialogCCTGTask import Ui_Dialog

from src.Common import Const, QTHelper
from src.Common.Logger import Logger
from src.Model.AppModel import appModel

_cctgPath = "https://cctg-cirepo.cisco.com/cirepo/webex_artifacts/mobile/cctg-android"
"""
https://cctg-cirepo.cisco.com/cirepo/webex_artifacts/mobile/cctg-android

master
{cctg}/41.12.0/cctg-android-41.12.0.149/mc-release-41.12.0.149.apk
apk:	{cctg}/{version}/cctg-android-{version}.{build}/mc-release-{version}.{build}.apk
mapping:{cctg}/{version}/cctg-android-{version}.{build}/mapping-release-{version}.{build}.tar
symbol:	{cctg}/{version}/cctg-android-{version}.{build}/symbol-pureRelease-{version}.{build}.tar

feature
{cctg}/41.12.0.usb_camera/cctg-android-41.12.0.147/mc-release-41.12.0.147.apk
apk:	{cctg}/{version}.{feature}/cctg-android-{version}.{build}/mc-release-{version}.{build}.apk
mapping:{cctg}/{version}.{feature}/cctg-android-{version}.{build}/mapping-release-{version}.{build}.tar
symbol:	{cctg}/{version}.{feature}/cctg-android-{version}.{build}/symbol-pureRelease-{version}.{build}.tar
"""


class DialogCCTGTask(QDialog, Ui_Dialog):
    def __init__(self, parent, title: str):
        super(DialogCCTGTask, self).__init__(parent)
        self.setupUi(self)
        QTHelper.switchMacUI(self)
        self._mTitle = title
        self.setWindowTitle(self._mTitle)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(True)
        self._mFolderURL = ""
        self._mAPKName = ""
        self._mSymbolName = ""
        self._mMappingName = ""
        self._tbBaseURL.setText(_cctgPath)
        self._tbFeature.setText("")
        self._tbVersion.setText("41.12.0")
        self._tbBuild.setText("149")
        QTHelper.setEditorReadOnly(self._tbBaseURL, True)

        self._bindEvent()

        self._ckAPK.setChecked(False)
        self._ckSymbol.setChecked(True)
        self._ckMapping.setChecked(True)
        self._onCheckAPK()
        self._onCheckSymbol()
        self._onCheckMapping()
        self._updateURL()
        return

    def _bindEvent(self):
        self._btOK.clicked.connect(self._onOK)
        self._btCancel.clicked.connect(self._onCancel)
        self._btBrowseCCTG.clicked.connect(self._onBrowseCCTG)
        self._btBrowseFolder.clicked.connect(self._onBrowseFolder)
        self._btCopyAPKURL.clicked.connect(self._onCopyAPKURL)
        self._btCopySymbolURL.clicked.connect(self._onCopySymbolURL)
        self._btCopyMappingURL.clicked.connect(self._onCopyMappingURL)
        self._ckAPK.clicked.connect(self._onCheckAPK)
        self._ckSymbol.clicked.connect(self._onCheckSymbol)
        self._ckMapping.clicked.connect(self._onCheckMapping)
        self._tbFeature.textChanged.connect(self._onEditorTextChanged)
        self._tbVersion.textChanged.connect(self._onEditorTextChanged)
        self._tbBuild.textChanged.connect(self._onEditorTextChanged)
        return

    def _onEditorTextChanged(self, newText):
        Logger.i(appModel.getAppTag(), f"{newText}")
        self._updateURL()
        return

    def _onOK(self):
        self.done(Const.EXIT_OK)
        return

    def _onCancel(self):
        self.done(Const.EXIT_CANCEL)
        return

    def _onBrowseCCTG(self):
        url = self._tbBaseURL.text()
        Logger.i(appModel.getAppTag(), f"{url}")
        webbrowser.open(url)
        return

    def _onBrowseFolder(self):
        url = f"{self._tbBaseURL.text()}/{self._mFolderURL}"
        Logger.i(appModel.getAppTag(), f"{url}")
        webbrowser.open(url)
        return

    def getVersionName(self) -> Tuple[bool, str]:
        version = self._tbVersion.text()        # "41.12.0"
        search = re.search(r"\d+\.\d+\.\d+", version)
        if search:
            keys = search.group(0).split(".")
            # "41.12.0.241120149"
            mainVersion = f"{version}"
            main2 = f"2{int(keys[0]):02d}{int(keys[1]):02d}{int(keys[2])}"
            main2Index = self._tbBuild.text()
            return True, f"{mainVersion}.{main2}{main2Index}"
        else:
            return False, f""

    def getAPKURL(self) -> Tuple[bool, str, str]:
        url = f"{self._tbBaseURL.text()}/{self._tbAPKURL.text()}"
        return self._ckAPK.isChecked(), self._mAPKName, url

    def getSymbolURL(self) -> Tuple[bool, str, str]:
        url = f"{self._tbBaseURL.text()}/{self._tbSymbolURL.text()}"
        return self._ckSymbol.isChecked(), self._mSymbolName, url

    def getMappingURL(self) -> Tuple[bool, str, str]:
        url = f"{self._tbBaseURL.text()}/{self._tbMappingURL.text()}"
        return self._ckMapping.isChecked(), self._mMappingName, url

    def _onCopyAPKURL(self):
        Logger.i(appModel.getAppTag(), "")
        _, _, url = self.getAPKURL()
        pyperclip.copy(url)
        return

    def _onCopySymbolURL(self):
        Logger.i(appModel.getAppTag(), "")
        _, _, url = self.getSymbolURL()
        pyperclip.copy(url)
        return

    def _onCopyMappingURL(self):
        Logger.i(appModel.getAppTag(), "")
        _, _, url = self.getMappingURL()
        pyperclip.copy(url)
        return

    def _onCheckAPK(self):
        Logger.i(appModel.getAppTag(), "")
        QTHelper.setEditorReadOnly(self._tbAPKURL, not self._ckAPK.isChecked())
        return

    def _onCheckSymbol(self):
        Logger.i(appModel.getAppTag(), "")
        QTHelper.setEditorReadOnly(self._tbSymbolURL, not self._ckSymbol.isChecked())
        return

    def _onCheckMapping(self):
        Logger.i(appModel.getAppTag(), "")
        QTHelper.setEditorReadOnly(self._tbMappingURL, not self._ckMapping.isChecked())
        return

    def _updateURL(self):
        """
        apk:	{cctg}/{version}.{feature}/cctg-android-{version}.{build}/mc-release-{version}.{build}.apk
        mapping:{cctg}/{version}.{feature}/cctg-android-{version}.{build}/mapping-release-{version}.{build}.tar
        symbol:	{cctg}/{version}.{feature}/cctg-android-{version}.{build}/symbol-pureRelease-{version}.{build}.tar
        """
        # cctg = self._tbBaseURL.text()
        version = self._tbVersion.text()
        feature = self._tbFeature.text()
        build = self._tbBuild.text()
        if len(feature) > 0:
            self._mFolderURL = f"{version}.{feature}/cctg-android-{version}.{build}"
        else:
            self._mFolderURL = f"{version}/cctg-android-{version}.{build}"
        self._mAPKName = f"mc-release-{version}.{build}.apk"
        self._mSymbolName = f"symbol-pureRelease-{version}.{build}.tar"
        self._mMappingName = f"mapping-release-{version}-{build}.tar"

        apkURL = f"{self._mFolderURL}/{self._mAPKName}"
        symbolURL = f"{self._mFolderURL}/{self._mSymbolName}"
        mappingURL = f"{self._mFolderURL}/{self._mMappingName}"
        self._tbAPKURL.setText(apkURL)
        self._tbSymbolURL.setText(symbolURL)
        self._tbMappingURL.setText(mappingURL)
