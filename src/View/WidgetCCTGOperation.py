from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from src.Common.Logger import Logger
from src.Model.AppModel import appModel

from src.Layout.widgetCCTGOperation import Ui_Form


class WidgetCCTGOperation(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(WidgetCCTGOperation, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        return
