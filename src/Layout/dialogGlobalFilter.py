# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoy/src/Layout/dialogGlobalFilter.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(592, 51)
        self.editFilter = QtWidgets.QLineEdit(Dialog)
        self.editFilter.setGeometry(QtCore.QRect(126, 10, 411, 24))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editFilter.sizePolicy().hasHeightForWidth())
        self.editFilter.setSizePolicy(sizePolicy)
        self.editFilter.setMinimumSize(QtCore.QSize(200, 24))
        self.editFilter.setObjectName("editFilter")
        self.btFilter = QtWidgets.QPushButton(Dialog)
        self.btFilter.setGeometry(QtCore.QRect(540, 12, 28, 24))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btFilter.sizePolicy().hasHeightForWidth())
        self.btFilter.setSizePolicy(sizePolicy)
        self.btFilter.setMinimumSize(QtCore.QSize(28, 24))
        self.btFilter.setMaximumSize(QtCore.QSize(28, 24))
        self.btFilter.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icons/bt_fliter.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btFilter.setIcon(icon)
        self.btFilter.setObjectName("btFilter")
        self.cbLogLevel = QtWidgets.QComboBox(Dialog)
        self.cbLogLevel.setGeometry(QtCore.QRect(20, 10, 104, 26))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbLogLevel.sizePolicy().hasHeightForWidth())
        self.cbLogLevel.setSizePolicy(sizePolicy)
        self.cbLogLevel.setMinimumSize(QtCore.QSize(100, 24))
        self.cbLogLevel.setObjectName("cbLogLevel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Set gobal filter"))
        self.btFilter.setToolTip(_translate("Dialog", "Filter content"))
import AndroidBoy_rc
