#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from os import path, chmod, makedirs
from shutil import move
from pymongo import MongoClient

from Season import Season, Chapter, Link
from Serie import Serie
from time import time
from datetime import datetime

SERVER_IP   = 'localhost'
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
            self._SERIE_PATH      = doc ['paths'] ['seriePath']
            self._TMP_PATH        = doc ['paths'] ['tmpPath']
            self._PLEX_USERNAME   = doc ['plex'] ['username']
            self._PLEX_PASSWORD   = doc ['plex'] ['password']
            self._PLEX_SERVERNAME = doc ['plex'] ['serverName']
        except:
            print 'Not documents found in collection, seriePath / tmpPath or plex user / password not specified .'

    def getSeriePath (self):
        return self._SERIE_PATH

    def getTmpPath (self):
        return self._TMP_PATH

    def getPlexUsername (self):
        return self._PLEX_USERNAME

    def getPlexPassword (self):
        return self._PLEX_PASSWORD

    def getPlexServerName (self):
        return self._PLEX_SERVERNAME

    def storeSerie (self, serie):
        toStore = {}
        toStore ['name'] = serie.getName ()
        toStore ['keyNames'] = serie.getKeyNames ()
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
        toReturn = self.db ['series'].find_one ({'keyNames' : {'$in' : [serieName.lower ()]}})

        serie = Serie ()
        serie.setName (toReturn ['name'])
        serie.setKeyNames (toReturn ['keyNames'])
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
        toReturn = self.db ['series'].find_one ({'keyNames' : {'$in' : [keyName.lower ()]}})
        if toReturn > 0:
            return True
        return False

    def addToDownloadQueue (self, serieName, seasonNumber, chapterNumber):
        toStore = {'serieName' : serieName, 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber, 'pending' : True}
        self.db ['downloadQueue'].insert_one (toStore)

    def getDownloadQueue (self):
        return self.db ['downloadQueue'].find ()

    def getPendingQueue (self):
        return self.db ['downloadQueue'].find ({'pending' : True})

    def downloadedFromDownloadQueue (self, serieName, seasonNumber, chapterNumber):
        self.db ['downloadQueue'].delete_one ({'serieName' : serieName.lower (), 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber})

    def inDownloadQueue (self, serieName, seasonNumber, chapterNumber):
        toReturn = self.db ['downloadQueue'].find ({"serieName" : serieName, 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber}).count ()

        if toReturn > 0:
            return True
        return False

    def markDownloadQueueAsPending (self):
        queue = self.getDownloadQueue ()
        for q in queue:
            toStore = {'serieName' : q ['serieName'],'seasonNumber' : q ['seasonNumber'], 'chapterNumber' : q ['chapterNumber'], 'pending' : True}
            self.db ['downloadQueue'].update_one ({'_id' : q ['_id']}, {"$set" : toStore })

    def markItemAsNotPending (self, serieName, seasonNumber, chapterNumber):
        toStore = {'serieName' : serieName.lower (), 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber, 'pending' : False}
        self.db ['downloadQueue'].update_one ({'serieName' : serieName.lower (), 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber}, {'$set' : toStore})

    def log (self, serieName, seasonNumber, chapterNumber, dataToLog):
        #data = self.db ['log'].find_one ({'chapterId' : chapterId})
        data = self.db ['log'].find_one ({'serieName' : serieName, 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber})
        toStore = {}
        if data is None:
            toStore ['log'] = []
            toStore ['serieName'] = serieName
            toStore ['seasonNumber'] = seasonNumber
            toStore ['chapterNumber'] = chapterNumber
            toStore ['log'].append ({'log' : dataToLog, 'datetime' : str (datetime.fromtimestamp (int (time ())))})
            self.db ['log'].insert_one (toStore)
        else:
            toStore ['serieName'] = data ['serieName']
            toStore ['seasonNumber'] = data ['seasonNumber']
            toStore ['chapterNumber'] = data ['chapterNumber']
            toStore ['log'] = data ['log']
            toStore ['log'].append ({'log' : dataToLog, 'datetime' : str (datetime.fromtimestamp (int (time ())))})
            self.db ['log'].update_one ({'serieName' : serieName, 'seasonNumber' : seasonNumber, 'chapterNumber' : chapterNumber}, {'$set' : toStore})

    def simpleLog (self, serieName, dataToLog):
        toStore = {}
        toStore ['serieName'] = serieName
        toStore ['timestamp'] = int (time ())
        toStore ['log'] = dataToLog
        self.db ['errors'].insert_one (toStore)
