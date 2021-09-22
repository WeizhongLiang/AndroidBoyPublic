import json
import os
import xml.dom.minidom
import base64

from PyQt5.QtGui import QSyntaxHighlighter
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox

from src.Common import JavaMappingHelper, NativeTraceParseHelper
from src.Common.Logger import Logger
from src.Model.AppModel import appModel
from src.Layout.jsonFormatView import Ui_Form

SELECT_DIR_JAVA = "parserSelectDirJava"
SELECT_DIR_NATIVE = "parserSelectDirNative"
SELECT_DIR_TYPE = "parserSelectType"


class ViewJsonFormat(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ViewJsonFormat, self).__init__(parent)
        self.setupUi(self)
        # self.sourceTxt.textChanged.connect(self.onTextChanged)
        self.pushButton.clicked.connect(self.onParseBtnClicked)
        self.rbJson.setChecked(True)


    def onParseBtnClicked(self):
        if self.rbJson.isChecked():
            self.jsonFormat()
        elif self.rbXml.isChecked():
            self.xmlFormat()
        else:
            self.base64Decode()

    def onTextChanged(self):
        pass

    def jsonFormat(self):
        context = self.sourceTxt.toPlainText()
        if not context:
            return
        try:
            load = json.loads(context)
        except Exception as e:
            box = QMessageBox()
            box.information(self, 'Invalid format', 'This string is invalid!')
            return
        dump = json.dumps(load, indent=4)
        self.resultTxt.setPlainText(dump)

    def xmlFormat(self):
        context = self.sourceTxt.toPlainText()
        if not context:
            return
        try:
            load = xml.dom.minidom.parseString(context)
        except Exception as e:
            box = QMessageBox()
            box.information(self, 'Invalid format', 'This string is invalid!')
            return
        dump = load.toprettyxml(indent='  ')
        dump = os.linesep.join([s for s in dump.splitlines() if s.strip()])
        self.resultTxt.setPlainText(dump)

    def base64Decode(self):
        context = self.sourceTxt.toPlainText()
        if not context:
            return
        try:
            encode = context.encode('utf-8')
            load = base64.b64decode(encode)
            dump = load.decode('utf-8')
        except Exception as e:
            box = QMessageBox()
            box.information(self, 'Invalid format', 'This string is invalid!')
            return
        self.resultTxt.setPlainText(dump)