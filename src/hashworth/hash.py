# -*- coding: utf-8 -*-
# Copyright: (C) 2019-2020 Lovac42
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

from .lib.porter2stemmer import Porter2Stemmer
from .utils import updatePTimer
from .clean import Cleaner
from .error import *
from .const import *


RE_SPACE=re.compile(r'\s+')

RE_NOMEDIA=re.compile(r"\[sound:[^]]+\]")

RE_NOCLOZE=re.compile(r"\{\{c\d+::(.*?)(\:\:.*?)?\}\}")

RE_NOSCHAR=re.compile(r"[’\x00-\1F\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+")

RE_PRONOUNS=re.compile(r"^(?:is|in|as|was|were|am|are|a|an|how|too?|not|I|me|mine|my(self)?|we|us|our(s|selves)?|your?s?|yoursel(f|ves)|he|hi[ms]|himself|she|her(s|self)?|it(s|self)?|the(n|[ym]|irs?)?|themsel(f|ves)|th(is|ese|at|ose)|who(m|se)?|wh(at|ich)|one(s|self)|if|else|of|for|does|be|with|lets?|and)$", re.I)


class HashProcessor:
    duplicate={}
    htmlCleaner=Cleaner()
    stemmer=Porter2Stemmer()
    startTime=0
    dupCount=0

    # def __init__(self):

    def setFields(self, match_field):
        self.match_field=match_field

    def setProperties(self, case_sensitive, no_space, no_html,
    no_media, no_cloze, no_schars, no_pronouns, norm):
        self.case_sensitive=case_sensitive
        self.no_space=no_space
        self.no_html=no_html
        self.no_media=no_media
        self.no_cloze=no_cloze
        self.no_schars=no_schars
        self.no_pronouns=no_pronouns
        self.op_normalize=norm


    def reset(self):
        self.duplicate={}
        self.dupCount=0

    def process(self, nids):
        if not nids:
            raise NoNoteError

        mw.checkpoint(ADDONNAME)
        self.startTime=time.time()

        for nid in nids:
            note=mw.col.getNote(nid)
            if self.match_field not in note or \
               not note[self.match_field]:
                continue
            h=self.getHash(note)
            if not h:
                continue
            if not self.duplicate.get(h):
                self.duplicate[h]=set()
            self.duplicate[h].add(nid)

        self.setDupCount()
        return self.dupCount


    def setDupCount(self):
        self.dupCount=0
        for hash,nids in self.duplicate.items():
            if len(nids)>1:
                self.dupCount+=1
        return self.dupCount


    def getHash(self, note):
        "write hash to field"
        wd=note[self.match_field]
        wd=self.cleanWord(wd)
        wd=self.normalize(wd,type=1)
        # print(wd)
        if wd:
            self.startTime=updatePTimer(self.startTime,wd)
            m=hashlib.md5()
            m.update(wd.encode('utf-8'))
            return m.hexdigest()


    def cleanWord(self, wd):
        if not self.case_sensitive:
            wd=wd.lower()

        if self.no_media:
            wd=RE_NOMEDIA.sub("",wd)

        if self.no_html:
            self.htmlCleaner.reset()
            self.htmlCleaner.feed(wd)
            wd=self.htmlCleaner.toString()

        if self.no_cloze:
            wd=RE_NOCLOZE.sub("\g<1>",wd)

        if self.no_schars:
            wd=RE_NOSCHAR.sub("",wd)

        if self.no_pronouns:
            arr=[]
            for w in RE_SPACE.split(wd):
                if w and not RE_PRONOUNS.search(w):
                    arr.append(w)
            if self.no_space:
                return "".join(arr)
            return " ".join(arr)

        if self.no_space: #space between words
            return RE_SPACE.sub("",wd)
        return wd.strip() #leading & trailing space


    def normalize(self, wd, type):
        #TODO: extend to other languages
        if self.op_normalize:
            arr=[]
            for w in wd.split():
                wd=self.stemmer.stem(wd)
                arr.append(wd)
            return "".join(wd)
        return wd
