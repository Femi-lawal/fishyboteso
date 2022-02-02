import logging
import traceback
import typing
from threading import Thread
from typing import Callable

import cv2
from playsound import playsound

from fishy.engine.common.window import WindowClient
from fishy.gui.funcs import GUIFuncsMock
from fishy.helper import helper
from fishy.helper.helper import print_exc

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class IEngine:

    def __init__(self, gui_ref: 'Callable[[], GUI]'):
        self.get_gui = gui_ref
        # 0 - off, 1 - running, 2 - quitting
        self.state = 0
        self.window = None
        self.thread: Thread = None

    @property
    def gui(self):
        if self.get_gui is None:
            return GUIFuncsMock()

        return self.get_gui().funcs

    @property
    def start(self):
        return self.state == 1

    def toggle_start(self):
        if self.state == 0:
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        self.state = 1
        self.thread = Thread(target=self._crash_safe)
        self.thread.start()

    def join(self):
        if self.thread:
            self.thread.join()

    def turn_off(self):
        """
        this method only signals the thread to close using start flag,
        its the responsibility of the thread to shut turn itself off
        """
        if self.state == 1:
            logging.info("turning off...")
            self.state = 2
        else:
            logging.error("engine already signaled to turn off")
            # todo: implement force turn off on repeated calls

    # noinspection PyBroadException
    def _crash_safe(self):
        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="fishy debug")
        self.gui.bot_started(True)
        try:
            self.run()
        except Exception:
            print_exc()
        self.state = 0
        self.gui.bot_started(False)
        self.window.destroy()

    def run(self):
        raise NotImplementedError
