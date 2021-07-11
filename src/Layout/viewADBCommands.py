# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoy/src/Layout/viewADBCommands.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self._editorOutput = QtWidgets.QTextEdit(Form)
        self._editorOutput.setReadOnly(True)
        self._editorOutput.setObjectName("_editorOutput")
        self.verticalLayout.addWidget(self._editorOutput)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 5, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self._editorCmd = QtWidgets.QLineEdit(Form)
        self._editorCmd.setObjectName("_editorCmd")
        self.horizontalLayout.addWidget(self._editorCmd)
        self._btOpen = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._btOpen.sizePolicy().hasHeightForWidth())
        self._btOpen.setSizePolicy(sizePolicy)
        self._btOpen.setMinimumSize(QtCore.QSize(28, 24))
        self._btOpen.setMaximumSize(QtCore.QSize(28, 24))
        self._btOpen.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icons/bt_start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._btOpen.setIcon(icon)
        self._btOpen.setObjectName("_btOpen")
        self.horizontalLayout.addWidget(self._btOpen)
        self._btStop = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._btStop.sizePolicy().hasHeightForWidth())
        self._btStop.setSizePolicy(sizePolicy)
        self._btStop.setMinimumSize(QtCore.QSize(28, 24))
        self._btStop.setMaximumSize(QtCore.QSize(28, 24))
        self._btStop.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icons/bt_stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._btStop.setIcon(icon1)
        self._btStop.setIconSize(QtCore.QSize(16, 16))
        self._btStop.setObjectName("_btStop")
        self.horizontalLayout.addWidget(self._btStop)
        self._btCommit = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._btCommit.sizePolicy().hasHeightForWidth())
        self._btCommit.setSizePolicy(sizePolicy)
        self._btCommit.setMinimumSize(QtCore.QSize(28, 24))
        self._btCommit.setMaximumSize(QtCore.QSize(28, 24))
        self._btCommit.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/icons/bt_prev_marked.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._btCommit.setIcon(icon2)
        self._btCommit.setObjectName("_btCommit")
        self.horizontalLayout.addWidget(self._btCommit)
        self._btSave = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._btSave.sizePolicy().hasHeightForWidth())
        self._btSave.setSizePolicy(sizePolicy)
        self._btSave.setMinimumSize(QtCore.QSize(28, 24))
        self._btSave.setMaximumSize(QtCore.QSize(28, 24))
        self._btSave.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/icons/bt_save.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._btSave.setIcon(icon3)
        self._btSave.setObjectName("_btSave")
        self.horizontalLayout.addWidget(self._btSave)
        self._btClear = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._btClear.sizePolicy().hasHeightForWidth())
        self._btClear.setSizePolicy(sizePolicy)
        self._btClear.setMinimumSize(QtCore.QSize(28, 24))
        self._btClear.setMaximumSize(QtCore.QSize(28, 24))
        self._btClear.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icon/icons/bt_clear.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._btClear.setIcon(icon4)
        self._btClear.setObjectName("_btClear")
        self.horizontalLayout.addWidget(self._btClear)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self._btStop.setToolTip(_translate("Form", "Stop"))
        self._btCommit.setToolTip(_translate("Form", "Commit command"))
        self._btSave.setToolTip(_translate("Form", "Save output"))
import AndroidBoy_rc
