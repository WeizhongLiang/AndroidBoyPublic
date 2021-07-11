# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/weizlian/Desktop/MyPrj/github-repos/Python/AndroidBoy/src/Layout/viewLogcat.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(913, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(500, 500))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.layoutView = QtWidgets.QVBoxLayout()
        self.layoutView.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layoutView.setSpacing(0)
        self.layoutView.setObjectName("layoutView")
        self.layoutDevices = QtWidgets.QHBoxLayout()
        self.layoutDevices.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layoutDevices.setContentsMargins(-1, 2, -1, 2)
        self.layoutDevices.setSpacing(0)
        self.layoutDevices.setObjectName("layoutDevices")
        self.cbDevices = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbDevices.sizePolicy().hasHeightForWidth())
        self.cbDevices.setSizePolicy(sizePolicy)
        self.cbDevices.setMinimumSize(QtCore.QSize(300, 24))
        self.cbDevices.setMaximumSize(QtCore.QSize(16777215, 24))
        self.cbDevices.setObjectName("cbDevices")
        self.layoutDevices.addWidget(self.cbDevices)
        spacerItem = QtWidgets.QSpacerItem(5, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layoutDevices.addItem(spacerItem)
        self.cbPackages = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbPackages.sizePolicy().hasHeightForWidth())
        self.cbPackages.setSizePolicy(sizePolicy)
        self.cbPackages.setMinimumSize(QtCore.QSize(300, 24))
        self.cbPackages.setMaximumSize(QtCore.QSize(16777215, 24))
        self.cbPackages.setObjectName("cbPackages")
        self.layoutDevices.addWidget(self.cbPackages)
        spacerItem1 = QtWidgets.QSpacerItem(3, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layoutDevices.addItem(spacerItem1)
        self.btInstallAPK = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btInstallAPK.sizePolicy().hasHeightForWidth())
        self.btInstallAPK.setSizePolicy(sizePolicy)
        self.btInstallAPK.setMinimumSize(QtCore.QSize(80, 24))
        self.btInstallAPK.setMaximumSize(QtCore.QSize(16777215, 24))
        self.btInstallAPK.setObjectName("btInstallAPK")
        self.layoutDevices.addWidget(self.btInstallAPK)
        self.btPushText = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btPushText.sizePolicy().hasHeightForWidth())
        self.btPushText.setSizePolicy(sizePolicy)
        self.btPushText.setMinimumSize(QtCore.QSize(0, 24))
        self.btPushText.setMaximumSize(QtCore.QSize(16777215, 24))
        self.btPushText.setObjectName("btPushText")
        self.layoutDevices.addWidget(self.btPushText)
        spacerItem2 = QtWidgets.QSpacerItem(40, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layoutDevices.addItem(spacerItem2)
        self.layoutView.addLayout(self.layoutDevices)
        self.layoutProcesses = QtWidgets.QHBoxLayout()
        self.layoutProcesses.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layoutProcesses.setContentsMargins(-1, 2, -1, 2)
        self.layoutProcesses.setSpacing(0)
        self.layoutProcesses.setObjectName("layoutProcesses")
        self.cbProcesses = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbProcesses.sizePolicy().hasHeightForWidth())
        self.cbProcesses.setSizePolicy(sizePolicy)
        self.cbProcesses.setMinimumSize(QtCore.QSize(300, 24))
        self.cbProcesses.setMaximumSize(QtCore.QSize(16777215, 24))
        self.cbProcesses.setObjectName("cbProcesses")
        self.layoutProcesses.addWidget(self.cbProcesses)
        spacerItem3 = QtWidgets.QSpacerItem(5, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layoutProcesses.addItem(spacerItem3)
        self.cbLogLevel = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbLogLevel.sizePolicy().hasHeightForWidth())
        self.cbLogLevel.setSizePolicy(sizePolicy)
        self.cbLogLevel.setMinimumSize(QtCore.QSize(100, 24))
        self.cbLogLevel.setMaximumSize(QtCore.QSize(16777215, 24))
        self.cbLogLevel.setObjectName("cbLogLevel")
        self.layoutProcesses.addWidget(self.cbLogLevel)
        spacerItem4 = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layoutProcesses.addItem(spacerItem4)
        self.editFilter = QtWidgets.QLineEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editFilter.sizePolicy().hasHeightForWidth())
        self.editFilter.setSizePolicy(sizePolicy)
        self.editFilter.setMinimumSize(QtCore.QSize(190, 24))
        self.editFilter.setMaximumSize(QtCore.QSize(16777215, 24))
        self.editFilter.setObjectName("editFilter")
        self.layoutProcesses.addWidget(self.editFilter)
        spacerItem5 = QtWidgets.QSpacerItem(3, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layoutProcesses.addItem(spacerItem5)
        self.btFilter = QtWidgets.QPushButton(Form)
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
        self.layoutProcesses.addWidget(self.btFilter)
        spacerItem6 = QtWidgets.QSpacerItem(40, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layoutProcesses.addItem(spacerItem6)
        self.layoutView.addLayout(self.layoutProcesses)
        self.layoutLogcat = QtWidgets.QHBoxLayout()
        self.layoutLogcat.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layoutLogcat.setContentsMargins(-1, 2, -1, 2)
        self.layoutLogcat.setSpacing(0)
        self.layoutLogcat.setObjectName("layoutLogcat")
        self.layoutLogcatOperations = QtWidgets.QVBoxLayout()
        self.layoutLogcatOperations.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layoutLogcatOperations.setContentsMargins(-1, 2, -1, 2)
        self.layoutLogcatOperations.setSpacing(0)
        self.layoutLogcatOperations.setObjectName("layoutLogcatOperations")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 2, -1, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btStop = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btStop.sizePolicy().hasHeightForWidth())
        self.btStop.setSizePolicy(sizePolicy)
        self.btStop.setMinimumSize(QtCore.QSize(28, 24))
        self.btStop.setMaximumSize(QtCore.QSize(28, 24))
        self.btStop.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icons/bt_stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btStop.setIcon(icon1)
        self.btStop.setObjectName("btStop")
        self.verticalLayout.addWidget(self.btStop)
        self.btStart = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btStart.sizePolicy().hasHeightForWidth())
        self.btStart.setSizePolicy(sizePolicy)
        self.btStart.setMinimumSize(QtCore.QSize(28, 24))
        self.btStart.setMaximumSize(QtCore.QSize(28, 24))
        self.btStart.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/icons/bt_start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btStart.setIcon(icon2)
        self.btStart.setObjectName("btStart")
        self.verticalLayout.addWidget(self.btStart)
        self.btSaveToFile = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btSaveToFile.sizePolicy().hasHeightForWidth())
        self.btSaveToFile.setSizePolicy(sizePolicy)
        self.btSaveToFile.setMinimumSize(QtCore.QSize(28, 24))
        self.btSaveToFile.setMaximumSize(QtCore.QSize(28, 24))
        self.btSaveToFile.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/icons/bt_save.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btSaveToFile.setIcon(icon3)
        self.btSaveToFile.setCheckable(True)
        self.btSaveToFile.setChecked(False)
        self.btSaveToFile.setObjectName("btSaveToFile")
        self.verticalLayout.addWidget(self.btSaveToFile)
        self.btAutoScroll = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btAutoScroll.sizePolicy().hasHeightForWidth())
        self.btAutoScroll.setSizePolicy(sizePolicy)
        self.btAutoScroll.setMinimumSize(QtCore.QSize(28, 24))
        self.btAutoScroll.setMaximumSize(QtCore.QSize(28, 24))
        self.btAutoScroll.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icon/icons/bt_auto_scroll.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btAutoScroll.setIcon(icon4)
        self.btAutoScroll.setObjectName("btAutoScroll")
        self.verticalLayout.addWidget(self.btAutoScroll)
        self.btClear = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btClear.sizePolicy().hasHeightForWidth())
        self.btClear.setSizePolicy(sizePolicy)
        self.btClear.setMinimumSize(QtCore.QSize(28, 24))
        self.btClear.setMaximumSize(QtCore.QSize(28, 24))
        self.btClear.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icon/icons/bt_clear.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btClear.setIcon(icon5)
        self.btClear.setObjectName("btClear")
        self.verticalLayout.addWidget(self.btClear)
        self.btSetting = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btSetting.sizePolicy().hasHeightForWidth())
        self.btSetting.setSizePolicy(sizePolicy)
        self.btSetting.setMinimumSize(QtCore.QSize(28, 24))
        self.btSetting.setMaximumSize(QtCore.QSize(28, 24))
        self.btSetting.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icon/icons/bt_settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btSetting.setIcon(icon6)
        self.btSetting.setObjectName("btSetting")
        self.verticalLayout.addWidget(self.btSetting)
        self.btMark = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btMark.sizePolicy().hasHeightForWidth())
        self.btMark.setSizePolicy(sizePolicy)
        self.btMark.setMinimumSize(QtCore.QSize(28, 24))
        self.btMark.setMaximumSize(QtCore.QSize(28, 24))
        self.btMark.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icon/icons/mark.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btMark.setIcon(icon7)
        self.btMark.setObjectName("btMark")
        self.verticalLayout.addWidget(self.btMark)
        self.btPrevMark = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btPrevMark.sizePolicy().hasHeightForWidth())
        self.btPrevMark.setSizePolicy(sizePolicy)
        self.btPrevMark.setMinimumSize(QtCore.QSize(28, 24))
        self.btPrevMark.setMaximumSize(QtCore.QSize(28, 24))
        self.btPrevMark.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icon/icons/bt_prev_marked.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btPrevMark.setIcon(icon8)
        self.btPrevMark.setObjectName("btPrevMark")
        self.verticalLayout.addWidget(self.btPrevMark)
        self.btNextMark = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btNextMark.sizePolicy().hasHeightForWidth())
        self.btNextMark.setSizePolicy(sizePolicy)
        self.btNextMark.setMinimumSize(QtCore.QSize(28, 24))
        self.btNextMark.setMaximumSize(QtCore.QSize(28, 24))
        self.btNextMark.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icon/icons/bt_next_marked.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btNextMark.setIcon(icon9)
        self.btNextMark.setObjectName("btNextMark")
        self.verticalLayout.addWidget(self.btNextMark)
        self.layoutLogcatOperations.addLayout(self.verticalLayout)
        spacerItem7 = QtWidgets.QSpacerItem(0, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layoutLogcatOperations.addItem(spacerItem7)
        self.layoutLogcat.addLayout(self.layoutLogcatOperations)
        self.layoutTracer = QtWidgets.QHBoxLayout()
        self.layoutTracer.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.layoutTracer.setContentsMargins(2, 2, -1, -1)
        self.layoutTracer.setSpacing(0)
        self.layoutTracer.setObjectName("layoutTracer")
        self.layoutLogcat.addLayout(self.layoutTracer)
        self.layoutView.addLayout(self.layoutLogcat)
        self.gridLayout.addLayout(self.layoutView, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btInstallAPK.setText(_translate("Form", "Install APK"))
        self.btPushText.setText(_translate("Form", "Push text"))
        self.btFilter.setToolTip(_translate("Form", "Filter content"))
        self.btStop.setToolTip(_translate("Form", "Stop logcat"))
        self.btStart.setToolTip(_translate("Form", "Start logcat"))
        self.btSaveToFile.setToolTip(_translate("Form", "Save to file"))
        self.btAutoScroll.setToolTip(_translate("Form", "Auto scroll to bottom"))
        self.btClear.setToolTip(_translate("Form", "Clear"))
        self.btSetting.setToolTip(_translate("Form", "Setting"))
        self.btMark.setToolTip(_translate("Form", "Mark the log"))
        self.btPrevMark.setToolTip(_translate("Form", "Prev marked"))
        self.btNextMark.setToolTip(_translate("Form", "Next marked"))
import AndroidBoy_rc
