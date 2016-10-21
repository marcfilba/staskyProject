#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import os
import shutil
import ConfigParser
from sys import exit

from Languages import Languages
from Season import Season, Chapter
from Serie import Serie

class CtrlDisk ():

    def __init__ (self, seriePath, tmpPath):
        self.seriePath = seriePath
        self.tmpPath = tmpPath

        if not os.path.exists (self.tmpPath):
            os.makedirs (self.tmpPath)

    def moveFile (self, fromPath, toPath):
        if not os.path.exists (self.seriePath + toPath):
            os.makedirs (self.seriePath + toPath)

        print self.tmpPath + fromPath
        os.chmod (self.tmpPath + fromPath, 0755)
        shutil.move (self.tmpPath + fromPath, self.seriePath + toPath)

    def getLastChapter (self, serieName):
        if not os.path.exists (self.seriePath + serieName):
            os.makedirs (self.seriePath + serieName)

        data = os.listdir (self.seriePath + serieName)
        if len (data) == 0:
            return None
        return sorted (data) [len (data) -1]

    def getLastChapterBySeason (self, serieName, seasonNumber):
        if not os.path.exists (self.seriePath + serieName):
            os.makedirs (self.seriePath + serieName)

        data = os.listdir (self.seriePath + serieName)

        lastChapter = 0
        seasonNumberStr = str(seasonNumber)

        for d in sorted (data):
            if seasonNumberStr + 'x' in d:
                lastChapter = int (d [3:5])
        return lastChapter
