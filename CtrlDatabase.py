#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from os import path, chmod, makedirs
from shutil import move
from pymongo import MongoClient

from Season import Season, Chapter, Link
from Serie import Serie

SERVER_IP   = '192.168.1.3'
SERVER_PORT = 27017

DATABASE_NAME = 'stasky'

class CtrlDatabase ():
    def __init__ (self):
        client = MongoClient (SERVER_IP, SERVER_PORT)
        self.db = client [DATABASE_NAME]
        try:
            confCollection = self.db.config
            doc = confCollection.find_one()
        except:
            print 'Collection "config" not found.'

        try:
            self.SERIE_PATH = doc ['seriePath']
            self.TMP_PATH   = doc ['tmpPath']
        except:
            print 'Not documents found in collection or seriePath / tmpPath not specified.'

    def getSeriePath (self):
        return self.SERIE_PATH

    def getTmpPath (self):
        return self.TMP_PATH

    def storeSerie (self, serie):
        toStore = {}
        toStore ['name'] = serie.getName ()
        toStore ['keyName'] = serie.getName ().lower ()
        toStore ['description'] = serie.getDescription ()
        toStore ['mainPageLinks'] = serie.getMainPageLinks ()
        toStore ['languages'] = serie.getLanguages ()
        toStore ['seasons'] = []
        for s in serie.getSeasons ():
            seasonTemp  = []
            for c in s.getChapters ():
                chapterTemp = {}
                chapterTemp ['name'] = c.getName ()
                chapterTemp ['releaseDate'] = c.getReleaseDate ()
                chapterTemp ['linkArray'] = []
                for l in c.getLinkArray ():
                    linkTemp = {}
                    linkTemp ['url'] = l.getURL ()
                    linkTemp ['host'] = l.getHost ()
                    linkTemp ['language'] = l.getLanguage ()
                    linkTemp ['subtitles'] = l.getSubtitles ()
                    linkTemp ['providerName'] = l.getProviderName ()

                    chapterTemp ['linkArray'].append (linkTemp)
                seasonTemp.append (chapterTemp)
            toStore ['seasons'].append (seasonTemp)

        if self.serieInDb (serie.getName ().lower ()):
            self.db ['series'].replace_one ({'name' : serie.getName ()}, toStore)
        else:
            self.db ['series'].insert_one (toStore)

    def getSerie (self, serieName):
        toReturn = self.db ['series'].find_one ({"keyName" : serieName.lower ()})

        serie = Serie ()
        serie.setName (toReturn ['name'])
        serie.setDescription (toReturn ['description'])
        serie.setLanguages (toReturn ['languages'])
        serie.setMainPageLinks (toReturn ['mainPageLinks'])

        for s in toReturn ['seasons']:
            se = Season ()
            for c in s :
                ch = Chapter ()
                ch.setName (c ['name'])
                ch.setReleaseDate (c ['releaseDate'])
                for l in c ['linkArray'] :
                    li = Link ()
                    li.setURL (l ['url'])
                    li.setHost (l ['host'])
                    li.setLanguage (l ['language'])
                    li.setSubtitles (l ['subtitles'])
                    li.setProviderName (l ['providerName'])

                    ch.addLink (li)
                se.addChapter (ch)
            serie.addSeason (se)
        return serie

    def serieInDb (self, keyName):
        toReturn = self.db ['series'].find ({"keyName" : keyName}).count ()
        if toReturn > 0:
            return True

        return False
