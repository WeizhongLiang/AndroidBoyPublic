from threading import Thread, Event

from src.Common.Logger import Logger
from src.Model.AppModel import appModel


class RepeatTimer(Thread):
    def __init__(self, interval, function, args=None, kwargs=None):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        Logger.i(appModel.getAppTag(), "")
        self.finished.set()

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
