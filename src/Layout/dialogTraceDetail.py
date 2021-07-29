# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoyPublic/src/Layout/dialogTraceDetail.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(357, 344)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/png/pngs/android_boy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.btOK = QtWidgets.QPushButton(Dialog)
        self.btOK.setGeometry(QtCore.QRect(20, 310, 75, 30))
        self.btOK.setMinimumSize(QtCore.QSize(0, 30))
        self.btOK.setMaximumSize(QtCore.QSize(16777215, 30))
        self.btOK.setObjectName("btOK")
        self.btCopy = QtWidgets.QPushButton(Dialog)
        self.btCopy.setGeometry(QtCore.QRect(100, 310, 75, 30))
        self.btCopy.setMinimumSize(QtCore.QSize(0, 30))
        self.btCopy.setMaximumSize(QtCore.QSize(16777215, 30))
        self.btCopy.setObjectName("btCopy")
        self.splitter_5 = QtWidgets.QSplitter(Dialog)
        self.splitter_5.setGeometry(QtCore.QRect(20, 10, 321, 291))
        self.splitter_5.setOrientation(QtCore.Qt.Vertical)
        self.splitter_5.setObjectName("splitter_5")
        self.splitter = QtWidgets.QSplitter(self.splitter_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.lbTime = QtWidgets.QLabel(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbTime.sizePolicy().hasHeightForWidth())
        self.lbTime.setSizePolicy(sizePolicy)
        self.lbTime.setMinimumSize(QtCore.QSize(40, 0))
        self.lbTime.setMaximumSize(QtCore.QSize(40, 16777215))
        self.lbTime.setObjectName("lbTime")
        self.tbTime = QtWidgets.QLineEdit(self.splitter)
        self.tbTime.setObjectName("tbTime")
        self.splitter_2 = QtWidgets.QSplitter(self.splitter_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.lbPID = QtWidgets.QLabel(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbPID.sizePolicy().hasHeightForWidth())
        self.lbPID.setSizePolicy(sizePolicy)
        self.lbPID.setMinimumSize(QtCore.QSize(40, 0))
        self.lbPID.setMaximumSize(QtCore.QSize(40, 16777215))
        self.lbPID.setObjectName("lbPID")
        self.tbPID = QtWidgets.QLineEdit(self.splitter_2)
        self.tbPID.setObjectName("tbPID")
        self.lbTID = QtWidgets.QLabel(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbTID.sizePolicy().hasHeightForWidth())
        self.lbTID.setSizePolicy(sizePolicy)
        self.lbTID.setMinimumSize(QtCore.QSize(40, 0))
        self.lbTID.setMaximumSize(QtCore.QSize(40, 16777215))
        self.lbTID.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbTID.setObjectName("lbTID")
        self.tbTID = QtWidgets.QLineEdit(self.splitter_2)
        self.tbTID.setObjectName("tbTID")
        self.splitter_3 = QtWidgets.QSplitter(self.splitter_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_3.sizePolicy().hasHeightForWidth())
        self.splitter_3.setSizePolicy(sizePolicy)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.lbLevel = QtWidgets.QLabel(self.splitter_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbLevel.sizePolicy().hasHeightForWidth())
        self.lbLevel.setSizePolicy(sizePolicy)
        self.lbLevel.setMinimumSize(QtCore.QSize(40, 0))
        self.lbLevel.setMaximumSize(QtCore.QSize(40, 16777215))
        self.lbLevel.setObjectName("lbLevel")
        self.tbLevel = QtWidgets.QLineEdit(self.splitter_3)
        self.tbLevel.setObjectName("tbLevel")
        self.splitter_4 = QtWidgets.QSplitter(self.splitter_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_4.sizePolicy().hasHeightForWidth())
        self.splitter_4.setSizePolicy(sizePolicy)
        self.splitter_4.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_4.setObjectName("splitter_4")
        self.lbTag = QtWidgets.QLabel(self.splitter_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbTag.sizePolicy().hasHeightForWidth())
        self.lbTag.setSizePolicy(sizePolicy)
        self.lbTag.setMinimumSize(QtCore.QSize(40, 0))
        self.lbTag.setMaximumSize(QtCore.QSize(40, 16777215))
        self.lbTag.setObjectName("lbTag")
        self.tbTag = QtWidgets.QLineEdit(self.splitter_4)
        self.tbTag.setObjectName("tbTag")
        self.tbMessage = QtWidgets.QTextEdit(self.splitter_5)
        self.tbMessage.setReadOnly(True)
        self.tbMessage.setObjectName("tbMessage")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Trace detail"))
        self.btOK.setText(_translate("Dialog", "OK"))
        self.btCopy.setText(_translate("Dialog", "Copy"))
        self.lbTime.setText(_translate("Dialog", "Time"))
        self.lbPID.setText(_translate("Dialog", "PID"))
        self.lbTID.setText(_translate("Dialog", "TID"))
        self.lbLevel.setText(_translate("Dialog", "Level"))
        self.lbTag.setText(_translate("Dialog", "Tag"))
import AndroidBoy_rc