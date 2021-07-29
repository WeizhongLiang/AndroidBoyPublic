# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoyPublic/src/Layout/dialogMailDetail.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1024, 768)
        Dialog.setMinimumSize(QtCore.QSize(1024, 768))
        Dialog.setMaximumSize(QtCore.QSize(4096, 2160))
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cbType = QtWidgets.QComboBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbType.sizePolicy().hasHeightForWidth())
        self.cbType.setSizePolicy(sizePolicy)
        self.cbType.setMinimumSize(QtCore.QSize(120, 24))
        self.cbType.setMaximumSize(QtCore.QSize(120, 24))
        self.cbType.setEditable(True)
        self.cbType.setObjectName("cbType")
        self.horizontalLayout.addWidget(self.cbType)
        self.cbSummary = QtWidgets.QComboBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbSummary.sizePolicy().hasHeightForWidth())
        self.cbSummary.setSizePolicy(sizePolicy)
        self.cbSummary.setMinimumSize(QtCore.QSize(360, 24))
        self.cbSummary.setMaximumSize(QtCore.QSize(360, 24))
        self.cbSummary.setEditable(True)
        self.cbSummary.setObjectName("cbSummary")
        self.horizontalLayout.addWidget(self.cbSummary)
        self.cbAddition = QtWidgets.QComboBox(Dialog)
        self.cbAddition.setMinimumSize(QtCore.QSize(0, 24))
        self.cbAddition.setMaximumSize(QtCore.QSize(16777215, 24))
        self.cbAddition.setEditable(True)
        self.cbAddition.setObjectName("cbAddition")
        self.horizontalLayout.addWidget(self.cbAddition)
        self.btPrevMail = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btPrevMail.sizePolicy().hasHeightForWidth())
        self.btPrevMail.setSizePolicy(sizePolicy)
        self.btPrevMail.setMinimumSize(QtCore.QSize(28, 24))
        self.btPrevMail.setMaximumSize(QtCore.QSize(28, 24))
        self.btPrevMail.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icons/arrow_left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btPrevMail.setIcon(icon)
        self.btPrevMail.setAutoDefault(False)
        self.btPrevMail.setObjectName("btPrevMail")
        self.horizontalLayout.addWidget(self.btPrevMail)
        self.btNextMail = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btNextMail.sizePolicy().hasHeightForWidth())
        self.btNextMail.setSizePolicy(sizePolicy)
        self.btNextMail.setMinimumSize(QtCore.QSize(28, 24))
        self.btNextMail.setMaximumSize(QtCore.QSize(28, 24))
        self.btNextMail.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icons/arrow_right.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btNextMail.setIcon(icon1)
        self.btNextMail.setAutoDefault(False)
        self.btNextMail.setDefault(False)
        self.btNextMail.setObjectName("btNextMail")
        self.horizontalLayout.addWidget(self.btNextMail)
        self.btFolder = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btFolder.sizePolicy().hasHeightForWidth())
        self.btFolder.setSizePolicy(sizePolicy)
        self.btFolder.setMinimumSize(QtCore.QSize(28, 24))
        self.btFolder.setMaximumSize(QtCore.QSize(28, 24))
        self.btFolder.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/icons/folder.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btFolder.setIcon(icon2)
        self.btFolder.setAutoDefault(False)
        self.btFolder.setObjectName("btFolder")
        self.horizontalLayout.addWidget(self.btFolder)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.layoutMail = QtWidgets.QVBoxLayout()
        self.layoutMail.setContentsMargins(0, 0, 0, 0)
        self.layoutMail.setObjectName("layoutMail")
        self.editTitle = QtWidgets.QLineEdit(Dialog)
        self.editTitle.setReadOnly(True)
        self.editTitle.setObjectName("editTitle")
        self.layoutMail.addWidget(self.editTitle)
        self.editSender = QtWidgets.QLineEdit(Dialog)
        self.editSender.setReadOnly(True)
        self.editSender.setObjectName("editSender")
        self.layoutMail.addWidget(self.editSender)
        self.layoutContent = QtWidgets.QHBoxLayout()
        self.layoutContent.setObjectName("layoutContent")
        self.editContent = QtWidgets.QTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editContent.sizePolicy().hasHeightForWidth())
        self.editContent.setSizePolicy(sizePolicy)
        self.editContent.setMinimumSize(QtCore.QSize(0, 200))
        self.editContent.setMaximumSize(QtCore.QSize(16777215, 200))
        self.editContent.setReadOnly(True)
        self.editContent.setObjectName("editContent")
        self.layoutContent.addWidget(self.editContent)
        self.ltErrors = QtWidgets.QListWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ltErrors.sizePolicy().hasHeightForWidth())
        self.ltErrors.setSizePolicy(sizePolicy)
        self.ltErrors.setMinimumSize(QtCore.QSize(300, 200))
        self.ltErrors.setMaximumSize(QtCore.QSize(300, 200))
        self.ltErrors.setObjectName("ltErrors")
        self.layoutContent.addWidget(self.ltErrors)
        self.layoutMail.addLayout(self.layoutContent)
        self.tabAttachments = QtWidgets.QTabWidget(Dialog)
        self.tabAttachments.setObjectName("tabAttachments")
        self.layoutMail.addWidget(self.tabAttachments)
        self.gridLayout.addLayout(self.layoutMail, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabAttachments.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "dialogMailDetail"))
import AndroidBoy_rc