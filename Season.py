#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Link ():
    def __init__ (self):
        self._URL = ''
        self._host = ''
        self._language = ''
        self._subtitles = ''
        self._providerName = ''
        self._valid = True

    def getURL (self):
        return self._URL

    def setURL (self, url):
        self._URL = url

    def getLanguage (self):
        return self._language

    def getSubtitles (self):
        return self._subtitles

    def getHost (self):
        return self._host

    def getProviderName (self):
        return self._providerName

    def setURL (self, url):
        self._URL = url

    def setHost (self, host):
        self._host = host

    def setLanguage (self, language):
        self._language = language

    def setSubtitles (self, subtitles):
        self._subtitles = subtitles

    def setProviderName (self, providerName):
        self._providerName = providerName

    def printLink (self):
        if self._subtitles == '':
            print self._host + ' (' + self._language + ') ' + self._providerName
        else:
            print self._host + ' (' + self._language + ') [Sub. ' + self._subtitles + '] '


class Chapter ():

    def __init__ (self):
        self._name = ''
        self._linkArray = []
        self._releaseDate = ''

    def getName (self):
        return self._name

    def getLinkArray (self):
        return self._linkArray

    def getReleaseDate (self):
        return self._releaseDate

    def setName (self, name):
        self._name = name

    def addLink (self, link):
        self._linkArray.append(link)

    def appendLinkArray (self, linkArray):
        self._linkArray += linkArray

    def setLinkArray (self, linkArray):
        self._linkArray = linkArray

    def setReleaseDate (self, releaseDate):
        self._releaseDate = releaseDate

    def printChapter (self):
        print '  -> name: ' + self._name
        print '  -> release Date: ' + str(self._releaseDate)
        #print 'LinkPage: ' + self._name
        #print 'LinkArray: ' + self._name


class Season ():

    def __init__ (self):
        self._chapters = []

    def getChapters (self):
        return self._chapters

    def addChapter (self, chapter):
        self._chapters.append(chapter)
