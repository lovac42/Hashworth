# -*- coding: utf-8 -*-
# Copyright: (C) 2019 Lovac42
# Support: https://github.com/lovac42/Hashworth
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


# enable for anki 2.0 if needed
# from __future__ import unicode_literals

import os, re
import time
import hashlib
from aqt import mw
from aqt.utils import showInfo
from anki.lang import _
from codecs import open

from .clean import Cleaner
from .error import *
from .const import *
from .lib.porter2stemmer import Porter2Stemmer


RE_NOSPACE=re.compile(r'\s')


class HashProcessor:
    htmlCleaner=Cleaner()
    stemmer=Porter2Stemmer()
    startTime=0
    stat={}

    # def __init__(self):

    def setFields(self, match_field):
        self.match_field=match_field

    def setProperties(self, case_sensitive, no_space, no_html, norm):
        self.case_sensitive=case_sensitive
        self.no_space=no_space
        self.no_html=no_html
        self.op_normalize=norm


    def process(self, nids):
        if not nids:
            raise NoNoteError

        mw.checkpoint("Hashworth")
        self.startTime=time.time()

        for nid in nids:
            note=mw.col.getNote(nid)
            if self.match_field not in note or \
               not note[self.match_field]:
                continue
            h=self.getHash(note)
            note.addTag("Hashworth::%s"%h)
            note.flush()


    def getHash(self, note):
        "write hash to field"
        wd=note[self.match_field]
        wd=self.cleanWord(wd)
        wd=self.normalize(wd,type=1)
        self.updatePTimer(wd)
        m=hashlib.md5()
        m.update(wd.encode('utf-8'))
        return m.hexdigest()


    def cleanWord(self, wd):
        if not self.case_sensitive:
            wd=wd.lower()

        if self.no_html:
            self.htmlCleaner.reset()
            self.htmlCleaner.feed(wd)
            wd=self.htmlCleaner.toString()

        if self.no_space: #space between words
            return RE_NOSPACE.sub("",wd)
        return wd.strip() #leading & trailing space


    def normalize(self, wd, type):
        #TODO: extend to other languages
        if self.op_normalize:
            arr=[]
            for w in wd.split():
                wd=self.stemmer.stem(wd)
                arr.append(wd)
            return " ".join(wd)
        return wd


    def updatePTimer(self, labelText):
        now = time.time()
        if now-self.startTime >= 0.5:
            self.startTime=now
            mw.progress.update(_("%s"%labelText))
