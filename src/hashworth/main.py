# -*- coding: utf-8 -*-
# Copyright: (C) 2019-2020 Lovac42
# Support: https://github.com/lovac42/Hashworth
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from aqt.qt import *
from anki.hooks import addHook

from .config import Config
from .hashworth import Hashworth
from .const import *


conf=Config(ADDONNAME)

def setupMenu(bws):
    act=QAction(TITLE, bws)

    key=conf.get("hotkey","Ctrl+Shift+H")
    if key:
        act.setShortcut(QKeySequence(key))

    act.triggered.connect(lambda:Hashworth(bws,conf))
    bws.form.menuEdit.addSeparator()
    bws.form.menuEdit.addAction(act)

addHook("browser.setupMenus", setupMenu)
