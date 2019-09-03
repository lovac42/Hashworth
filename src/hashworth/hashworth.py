# -*- coding: utf-8 -*-
# Copyright: (C) 2019 Lovac42
# Support: https://github.com/lovac42/Hashworth
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import re
from aqt import mw
from aqt.qt import *
from aqt.utils import getFile, showInfo
from anki.lang import _

from .utils import fieldNamesForNotes, updatePTimer
from .hash import HashProcessor
from .const import *
from .error import *

if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


class Hashworth():
    proc=HashProcessor()

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
        if ANKI21:
            self.browser.editor.saveNow(self.hideEditor)
        else:
            self.browser.editor.saveNow()
            self.hideEditor()

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

        fieldLayout=QtWidgets.QHBoxLayout()
        dups=self.proc.dupCount
        self.lbl_total=QtWidgets.QLabel(_("    Total Duplicate(s) Found: %d\n"%dups))
        fieldLayout.addWidget(self.lbl_total)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        r+=1
        fieldLayout=QtWidgets.QHBoxLayout()
        label=QtWidgets.QLabel("Search Field:")
        fieldLayout.addWidget(label)

        idx=self.conf.get("match_field",0)
        self.matchField=QComboBox()
        self.matchField.setMinimumWidth(250)
        self.matchField.addItems(fields)
        self.matchField.setCurrentIndex(idx)
        self.matchField.currentIndexChanged.connect(self.onFieldChanged)
        fieldLayout.addWidget(self.matchField)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        self.btn_add=QPushButton('Add Field')
        self.btn_add.clicked.connect(self.onAdd)
        gridLayout.addWidget(self.btn_add,r,1,1,1)

        r+=1
        fieldLayout=QtWidgets.QHBoxLayout()
        cbs=self.conf.get("strip_html",0)
        self.cb_rm_html=QtWidgets.QCheckBox()
        self.cb_rm_html.setCheckState(cbs)
        self.cb_rm_html.clicked.connect(self.onChangedCB)
        self.cb_rm_html.setText(_('No HTML'))
        self.cb_rm_html.setToolTip(_('Strip HTML during search'))
        fieldLayout.addWidget(self.cb_rm_html)

        cbs=self.conf.get("strip_space",0)
        self.cb_rm_space=QtWidgets.QCheckBox()
        self.cb_rm_space.setCheckState(cbs)
        self.cb_rm_space.clicked.connect(self.onChangedCB)
        self.cb_rm_space.setText(_('No Space'))
        self.cb_rm_space.setToolTip(_('Strip space during search'))
        fieldLayout.addWidget(self.cb_rm_space)

        cbs=self.conf.get("strip_chars",0)
        self.cb_chars=QtWidgets.QCheckBox()
        self.cb_chars.setCheckState(cbs)
        self.cb_chars.clicked.connect(self.onChangedCB)
        self.cb_chars.setText(_('No Punctuation'))
        self.cb_chars.setToolTip(_('Strip non-printable chars during search'))
        fieldLayout.addWidget(self.cb_chars)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        self.btn_clear=QPushButton('Clear Dict')
        self.btn_clear.clicked.connect(self.onClear)
        gridLayout.addWidget(self.btn_clear,r,1,1,1)

        r+=1
        fieldLayout=QtWidgets.QHBoxLayout()
        cbs=self.conf.get("strip_cloze",0)
        self.cb_cloze=QtWidgets.QCheckBox()
        self.cb_cloze.setCheckState(cbs)
        self.cb_cloze.clicked.connect(self.onChangedCB)
        self.cb_cloze.setText(_('No Cloze'))
        self.cb_cloze.setToolTip(_('Strip cloze tags during search'))
        fieldLayout.addWidget(self.cb_cloze)

        cbs=self.conf.get("strip_media",0)
        self.cb_rm_media=QtWidgets.QCheckBox()
        self.cb_rm_media.setCheckState(cbs)
        self.cb_rm_media.clicked.connect(self.onChangedCB)
        self.cb_rm_media.setText(_('No Sound'))
        self.cb_rm_media.setToolTip(_('Strip [Sound] tags during search'))
        fieldLayout.addWidget(self.cb_rm_media)

        cbs=self.conf.get("strip_pronouns",0)
        self.cb_pronouns=QtWidgets.QCheckBox()
        self.cb_pronouns.setCheckState(cbs)
        self.cb_pronouns.clicked.connect(self.onChangedCB)
        self.cb_pronouns.setText(_('No Pronouns'))
        self.cb_pronouns.setToolTip(_('Strip pronouns during search'))
        fieldLayout.addWidget(self.cb_pronouns)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        r+=1
        cbs=self.conf.get("case_sensitive",0)
        self.cb_casesense=QtWidgets.QCheckBox()
        self.cb_casesense.setCheckState(cbs)
        self.cb_casesense.clicked.connect(self.onChangedCB)
        self.cb_casesense.setText(_('Case Sensitive'))
        self.cb_casesense.setToolTip(_('Case sensitive search'))
        # fieldLayout.addWidget(self.cb_casesense)
        gridLayout.addWidget(self.cb_casesense, r, 0, 1, 1)

        r+=1
        cbs=self.conf.get("use_stemmer",0)
        self.cb_normalize=QtWidgets.QCheckBox()
        self.cb_normalize.setCheckState(cbs)
        self.cb_normalize.clicked.connect(self.onChangedCB)
        self.cb_normalize.setText(_('Apply English stemmer? (GIYF)'))
        self.cb_normalize.setToolTip(_('Strips suffix -s, -ed, -es, -ing, -tion, -sion, ...'))
        gridLayout.addWidget(self.cb_normalize, r, 0, 1, 1)

        self.btn_tag=QPushButton('Tag Dups')
        self.btn_tag.clicked.connect(self.onTag)
        gridLayout.addWidget(self.btn_tag,r,1,1,1)

        diag=QDialog(self.browser)
        diag.setLayout(layout)
        diag.setWindowTitle(TITLE)
        diag.exec_()


    def onChangedCB(self):
        cs=self.cb_casesense.checkState()
        sp=self.cb_rm_space.checkState()
        htm=self.cb_rm_html.checkState()
        m=self.cb_rm_media.checkState()
        p=self.cb_pronouns.checkState()
        ch=self.cb_chars.checkState()
        cz=self.cb_cloze.checkState()
        stem=self.cb_normalize.checkState()
        self.conf.set("case_sensitive",cs)
        self.conf.set("strip_html",htm)
        self.conf.set("strip_space",sp)
        self.conf.set("strip_media",m)
        self.conf.set("strip_pronouns",p)
        self.conf.set("strip_chars",ch)
        self.conf.set("strip_cloze",cz)
        self.conf.set("use_stemmer",stem)


    def onFieldChanged(self):
        idx=self.matchField.currentIndex()
        self.conf.set("match_field",idx)


    def onClear(self):
        self.proc.reset()
        self.lbl_total.setText(_("    Total Duplicate(s) Found: 0"))


    def onAdd(self):
        mw.progress.start(immediate=True)
        mw.progress.update(_("Processing Notes..."))

        mf=self.matchField.currentText()
        cs=self.cb_casesense.checkState()
        sp=self.cb_rm_space.checkState()
        htm=self.cb_rm_html.checkState()
        noMedia=self.cb_rm_media.checkState()

        cloze=self.cb_cloze.checkState()
        chars=self.cb_chars.checkState()
        pronouns=self.cb_pronouns.checkState()
        norm=self.cb_normalize.checkState()

        self.proc.setFields(mf)
        self.proc.setProperties(cs,sp,htm,noMedia,cloze,chars,pronouns,norm)
        try:
            cnt=self.proc.process(self.notes)
        except NoListError as err:
            showInfo(str(err))
        finally:
            mw.progress.finish()
        self.lbl_total.setText(_("    Total Duplicate(s) Found: %d"%cnt))

    def onTag(self):
        mw.progress.start(immediate=True)
        mw.progress.update(_("Processing Notes..."))

        startTime=0
        for hash,nids in self.proc.duplicate.items():
            if len(nids)<2: continue
            for nid in nids:
                note=mw.col.getNote(nid)
                note.addTag("Hashworth::%s"%hash)
                note.flush()
            startTime=updatePTimer(startTime,hash)
        mw.progress.finish()

