#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CtrlDatabase import CtrlDatabase
from CtrlDisk import CtrlDisk
from CtrlProviders import CtrlProviders
from Serie import Serie

from Tools import readInt, isNumber

from sys import exit, stdout
from random import randint
from threading import Thread
from time import sleep

import exceptions
import errno

class Domain ():

    def __init__ (self):
        self._ctrlDatabase = CtrlDatabase ()
        self._ctrlDisk = CtrlDisk (self._ctrlDatabase.getSeriePath (), self._ctrlDatabase.getTmpPath ())
        self._ctrlProviders = CtrlProviders (self._ctrlDatabase.getTmpPath())

        self._ctrlDatabase.markDownloadQueueAsPending ()
        self._seriesPending = []

    def _deleteSeriePending (self, serieName):
        for i, s in enumerate (self._seriesPending):
            if s == serieName.lower ():
                self._seriesPending.pop (i)

    def _addSeriePending (self, serieName):
        self._seriesPending.append (serieName.lower ())

    def _isSeriePending (self, serieName):
        for i, s in enumerate (self._seriesPending):
            if s == serieName.lower ():
                return True
        return False

    def updateExistingSerie (self, serie):

        serie.setSeasons ([])
        serieMainPages = []
        for keyName in serie.getKeyNames ():
            if len (serie.getSeasons ()) == 0:
                sDataTmp = self._ctrlProviders.loadSerie (keyName)
                sTmp = Serie ()
                sTmp.loadSerie (sDataTmp)
                serie.setSeasons (sTmp.getSeasons ())

            if len (serieMainPages) == 0:
                serieMainPages = self._ctrlProviders.getMainInfo (keyName)

        serie.setMainPageLinks (serieMainPages)

        self._ctrlDatabase.storeSerie (serie)

    def _updateSerie (self, serieName):
        serieNameOk = serieName.lower ()
        serieData = self._ctrlProviders.loadSerie (serieNameOk)
        if serieData == None:
            sugg = self._ctrlProviders.getSuggerencies ()
            if len (sugg) > 0:
                serieNameOk =  sugg [0].lower ()
                serieData = self._ctrlProviders.loadSerie (serieNameOk)
                if serieData == None:
                    raise Exception ('  -> serie "' + serieName + '" not found')

        serie = Serie ()
        serie.loadSerie (serieData)

        if (serieNameOk != serieName.lower ()) or (serieNameOk != serie.getName ().lower ()):
            serie.addKeyName (serieName.lower ())

        serieMainPages = []
        for keyName in serie.getKeyNames ():
            if len (serieMainPages) == 0:
                serieMainPages = self._ctrlProviders.getMainInfo (keyName)

        serie.setMainPageLinks (serieMainPages)

        self._ctrlDatabase.storeSerie (serie)

        return serie

    def _getSerie (self, serieName):
        serie = Serie ()
        if self._ctrlDatabase.serieInDb (serieName):
            serie = self._ctrlDatabase.getSerie (serieName)
        else:
            self._addSeriePending (serieName)
            serie = self._updateSerie (serieName)
            self._deleteSeriePending (serieName)

        return serie

    def _selectChapter (self, links, languages):
        it = 0
        possibleLinks = []

        while len (possibleLinks) == 0: # and it < len(self.languages.getLanguages()):

            for i, l in enumerate(links):
                if languages ['languages'] [it].lower () in l.getLanguage ().lower () and languages ['subtitles'] [it].lower () in l.getSubtitles ().lower ():
                    if 'streamcloud' in l.getHost ().lower () or \
    				   'nowvideo' in l.getHost ().lower ():
                       # or \
    				   #'streamin' in l.getHost ().lower () or \
    				   #'streamplay' in l.getHost ().lower ():
    					possibleLinks.append (l)
                if len (possibleLinks) == 0:
                    it = it + 1
                    if it >= len (languages ['languages']):
                        return None

            if len (possibleLinks) > 0:
                rand = randint (0, len(possibleLinks)-1)
                for j, l in enumerate(links):
                    if l.getURL () in possibleLinks [rand].getURL ():
                        return possibleLinks [rand]

    			return links [read - 1]

    def _buildName (self, serie, seasonNumber, chapterNumber, language, subtitules):
        name = str(seasonNumber) + 'x'

        if chapterNumber < 10:
            name += '0'
        name += str(chapterNumber) + ' - ' + \
        serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].getName () + '.' + language[0:2].upper ()

        if len(subtitules) >= 2:
            name += '-' + subtitules[0:2].upper ()

        return name.replace('\\', '-').replace('?','').replace('!','') + '.mp4'

    def getPlexServerName (self):
        return self._ctrlDatabase.getPlexServerName ()

    def getPlexUsername (self):
        return self._ctrlDatabase.getPlexUsername ()

    def getPlexPassword (self):
        return self._ctrlDatabase.getPlexPassword ()

    def downloadChapter (self, serieName, seasonNumber, chapterNumber):
        serie = Serie ()
        try:
            serie = self._getSerie (serieName)
        except Exception as e:
            self._deleteSeriePending (serieName)
            self.log (serieName, seasonNumber, chapterNumber, 'serie not found')
            return -5

        if serie.seasonExists (seasonNumber):
            if serie.chapterNumberExists (seasonNumber, chapterNumber):

                if len (serie.getMainPageLinks ()) == 0:
                    self.updateExistingSerie (serie)
                    if len (serie.getMainPageLinks ()) == 0:
                        self.log (serieName, seasonNumber, chapterNumber, 'no mainPageLink found')
                        raise Exception ('error, no mainPageLink found')


                if len (serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].getLinkArray ()) == 0:
                    chapterUrls = self._ctrlProviders.getChapterUrls(serie.getMainPageLinks (), seasonNumber, chapterNumber, serie.getLanguages ())
                    if isNumber (chapterUrls):
                        self.log (serieName, seasonNumber, chapterNumber, 'can\'t retrieve the chapter (Error ' + str(chapterUrls) + ')')
                        raise Exception ('error, can\'t retrieve the chapter')
                    serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].appendLinkArray (chapterUrls)
                    self._ctrlDatabase.storeSerie (serie)

                chapterUrls = serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].getLinkArray ()

                if len(chapterUrls) > 0:
                    downloadErr = True

                    self.log (serieName, seasonNumber, chapterNumber, str (len (chapterUrls)) + ' links found')
                    while downloadErr:
                        selectedChapter = self._selectChapter (chapterUrls, serie.getLanguages ())
                        if selectedChapter == None:
                            self.log (serieName, seasonNumber, chapterNumber, 'no links for download found')
                            return -2
                        name = self._buildName (serie, seasonNumber, chapterNumber, selectedChapter.getLanguage(), selectedChapter.getSubtitles())

                        try:
                            #selectedChapter.printLink ()
                            #print selectedChapter.getURL ()
                            self.log (serieName, seasonNumber, chapterNumber,'starting download ' + str (selectedChapter.getURL ()))
                            self._ctrlProviders.downloadVideo (selectedChapter.getURL (), selectedChapter.getHost (), name)
                            self.log (serieName, seasonNumber, chapterNumber, 'downloaded successfull')
                            serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].setLinkArray ([])
                            downloadErr = False

                            try:
                                self._ctrlDisk.moveFile (name, serie.getName ())
                                self.log (serieName, seasonNumber, chapterNumber, 'moved to serie folder')
                                return 0

                            except exceptions.NameError as e:
                                self.log (serieName, seasonNumber, chapterNumber, 'error moving chapter, (' + str (e) + '), deleting')
                                self._ctrlDisk.deleteFile (name, serieName.getName ())
                            except exceptions.OSError as e:
                                if e.errno == errno.EEXIST:
                                    self.log (serieName, seasonNumber, chapterNumber, 'error moving chapter, (' + str (e) + '), move it manually')

                            return -1

                        except Exception as e:
                            print str (e)
                            self.log (serieName, seasonNumber, chapterNumber,'failed download, trying another link')
                            iterator = 0
                            deleted = False
                            while iterator < len (chapterUrls) and not deleted:
                                if selectedChapter.getURL () is chapterUrls [iterator].getURL ():
                                    chapterUrls.pop (iterator)
                                    serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].setLinkArray (chapterUrls)
                                    self._ctrlDatabase.storeSerie (serie)
                                    deleted = True
                                iterator += 1

            else:
                self.log (serieName, seasonNumber, chapterNumber, 'chapter number doesn\'t exist')
                return -3
        else:
            self.log (serieName, seasonNumber, chapterNumber, 'season number doesn\'t exist')
            return -4

    def addToDownloadQueue (self, serieName, seasonNumber, chapterNumber):
        if not self._ctrlDatabase.inDownloadQueue (serieName.lower (), seasonNumber, chapterNumber):
            self._ctrlDatabase.addToDownloadQueue (serieName.lower (), seasonNumber, chapterNumber)

    def log (self, serieName, seasonNumber, chapterNumber, dataToLog):
        self._ctrlDatabase.log (serieName, seasonNumber, chapterNumber, dataToLog)

    def simpleLog (self, serieName, dataToLog):
        self._ctrlDatabase.simpleLog (serieName, dataToLog)

    def processSingleDownload (self, serieName, seasonNumber, chapterNumber):
        self.log (serieName, seasonNumber, chapterNumber, 'processing')
        if self._isSeriePending (serieName):
            self.log (serieName, seasonNumber, chapterNumber, 'waiting for serie data')
            while self._isSeriePending (serieName):
                sleep (3)

            self.log (serieName, seasonNumber, chapterNumber, 'resuming')

        if self.downloadChapter (serieName.lower (), seasonNumber, chapterNumber) == 0:
            self.downloadedFromDownloadQueue (serieName, seasonNumber, chapterNumber)
        #else:
        #    self._ctrlDatabase.markItemAsPending (serieName, seasonNumber, chapterNumber)

    def getPendingQueue (self):
        return self._ctrlDatabase.getPendingQueue ()

    def downloadedFromDownloadQueue (self, serieName, seasonNumber, chapterNumber):
        self._ctrlDatabase.downloadedFromDownloadQueue (serieName, seasonNumber, chapterNumber)

    def markItemAsNotPending (self, serieName, seasonNumber, chapterNumber):
        self._ctrlDatabase.markItemAsNotPending (serieName, seasonNumber, chapterNumber)
