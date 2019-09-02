# -*- coding: utf-8 -*-
# Copyright: (C) 2019 Lovac42
# Support: https://github.com/lovac42/Hashworth
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import re
from aqt import mw
from aqt.qt import *
from aqt.utils import getFile, showInfo
from anki.lang import _

from .utils import fieldNamesForNotes
from .hash import HashProcessor
from .const import *
from .error import *

if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


class Hashworth():

    def __init__(self, browser, conf):
        self.browser=browser
        self.conf=conf

        #Must have some notes selected in browser
        try:
            self.setNotes()
        except NoNoteError as err:
            showInfo(str(err))
            return

        #Note in editor must be removed to update templates.
        if CCBC or ANKI20:
            self.browser.editor.saveNow()
            self.hideEditor()
        else:
            self.browser.editor.saveNow(self.hideEditor)

        self.showDialog()


    def setNotes(self):
        self.notes=self.browser.selectedNotes()
        if not self.notes:
            raise NoNoteError


    def hideEditor(self):
        self.browser.editor.setNote(None)
        self.browser.singleCard=False


    def showDialog(self):
        fields=fieldNamesForNotes(self.notes)

        r=0
        gridLayout=QtWidgets.QGridLayout()
        layout=QtWidgets.QVBoxLayout()
        layout.addLayout(gridLayout)

        r+=1
        fieldLayout=QtWidgets.QHBoxLayout()
        label=QtWidgets.QLabel("Search Note Field:")
        fieldLayout.addWidget(label)

        idx=self.conf.get("match_field",0)
        self.matchField=QComboBox()
        self.matchField.setMinimumWidth(250)
        self.matchField.addItems(fields)
        self.matchField.setCurrentIndex(idx)
        self.matchField.currentIndexChanged.connect(self.checkWritable)
        fieldLayout.addWidget(self.matchField)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        cbs=self.conf.get("strip_html",0)
        self.cb_rm_html=QtWidgets.QCheckBox()
        self.cb_rm_html.setCheckState(cbs)
        self.cb_rm_html.clicked.connect(self.onChangedCB)
        self.cb_rm_html.setText(_('No HTML'))
        self.cb_rm_html.setToolTip(_('Strip HTML during search'))
        gridLayout.addWidget(self.cb_rm_html, r, 1, 1, 1)

        r+=1

        cbs=self.conf.get("strip_space",0)
        self.cb_rm_space=QtWidgets.QCheckBox()
        self.cb_rm_space.setCheckState(cbs)
        self.cb_rm_space.clicked.connect(self.onChangedCB)
        self.cb_rm_space.setText(_('No Space'))
        self.cb_rm_space.setToolTip(_('Strip space during search'))
        gridLayout.addWidget(self.cb_rm_space, r, 1, 1, 1)

        r+=1
        self.cb_normalize=QtWidgets.QCheckBox()
        self.cb_normalize.setText(_('Apply English stemmer? (GIYF)'))
        self.cb_normalize.setToolTip(_('Strips suffix -s, -ed, -es, -ing, -tion, -sion, ...'))
        gridLayout.addWidget(self.cb_normalize, r, 0, 1, 1)


        cbs=self.conf.get("case_sensitive",0)
        self.cb_casesense=QtWidgets.QCheckBox()
        self.cb_casesense.setCheckState(cbs)
        self.cb_casesense.clicked.connect(self.onChangedCB)
        self.cb_casesense.setText(_('Case Sen..'))
        self.cb_casesense.setToolTip(_('Case Sensitive Match'))
        gridLayout.addWidget(self.cb_casesense, r, 1, 1, 1)

        r+=1
        self.btn_save=QPushButton('Field to Hash to Tag')
        self.btn_save.clicked.connect(self.onWrite)
        gridLayout.addWidget(self.btn_save,r,0,1,1)

        diag=QDialog(self.browser)
        diag.setLayout(layout)
        diag.setWindowTitle(TITLE)
        diag.exec_()


    def onChangedCB(self):
        cs=self.cb_casesense.checkState()
        sp=self.cb_rm_space.checkState()
        htm=self.cb_rm_html.checkState()
        self.conf.set("case_sensitive",cs)
        self.conf.set("strip_html",htm)
        self.conf.set("strip_space",sp)


    def checkWritable(self):
        idx=self.matchField.currentIndex()
        self.conf.set("match_field",idx)


    def onWrite(self):
        if self.btn_save.isEnabled():
            mw.progress.start(immediate=True)
            mw.progress.update(_("Processing Cards..."))

            mf=self.matchField.currentText()
            cs=self.cb_casesense.checkState()
            sp=self.cb_rm_space.checkState()
            htm=self.cb_rm_html.checkState()
            norm=self.cb_normalize.checkState()

            self.proc=HashProcessor()
            self.proc.setFields(mf)
            self.proc.setProperties(cs,sp,htm,norm)
            try:
                self.proc.process(self.notes)
            except NoListError as err:
                showInfo(str(err))
            finally:
                mw.progress.finish()
            showInfo("Done!")

