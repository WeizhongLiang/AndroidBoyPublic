# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'traceParser.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(950, 669)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.comboBox_type = QtWidgets.QComboBox(Form)
        self.comboBox_type.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox_type.setObjectName("comboBox_type")
        self.horizontalLayout.addWidget(self.comboBox_type)
        self.comboBox_paths = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_paths.sizePolicy().hasHeightForWidth())
        self.comboBox_paths.setSizePolicy(sizePolicy)
        self.comboBox_paths.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox_paths.setEditable(True)
        self.comboBox_paths.setInsertPolicy(QtWidgets.QComboBox.InsertAtTop)
        self.comboBox_paths.setObjectName("comboBox_paths")
        self.horizontalLayout.addWidget(self.comboBox_paths)
        self.pushButton_browser = QtWidgets.QPushButton(Form)
        self.pushButton_browser.setMinimumSize(QtCore.QSize(0, 30))
        self.pushButton_browser.setObjectName("pushButton_browser")
        self.horizontalLayout.addWidget(self.pushButton_browser)
        self.pushButton_parse = QtWidgets.QPushButton(Form)
        self.pushButton_parse.setMinimumSize(QtCore.QSize(0, 30))
        self.pushButton_parse.setObjectName("pushButton_parse")
        self.horizontalLayout.addWidget(self.pushButton_parse)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.plainTextEdit_trace = QtWidgets.QPlainTextEdit(Form)
        self.plainTextEdit_trace.setObjectName("plainTextEdit_trace")
        self.verticalLayout.addWidget(self.plainTextEdit_trace)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.textBrowser_result = QtWidgets.QTextBrowser(Form)
        self.textBrowser_result.setObjectName("textBrowser_result")
        self.verticalLayout.addWidget(self.textBrowser_result)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_3.setText(_translate("Form", "Select parser type"))
        self.pushButton_browser.setText(_translate("Form", "Browser..."))
        self.pushButton_parse.setText(_translate("Form", "Parse"))
        self.label.setText(_translate("Form", "Native/Java crash trace"))
        self.label_2.setText(_translate("Form", "Parse result"))
