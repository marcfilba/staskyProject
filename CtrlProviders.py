#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DownloadStreamCloud import DownloadStreamCloud
from DownloadNowVideo import DownloadNowVideo
from DownloadStreamin import DownloadStreamin
from DownloadStreamPlay import DownloadStreamPlay

#from InfoProviderImdb import InfoProviderImdb
from InfoProviderTvmaze import InfoProviderTvmaze

#from LinksProviderSeriesFlv import LinksProviderSeriesFlv
from LinksProviderSeriesPepito import LinksProviderSeriesPepito
from LinksProviderSeriesAdicto import LinksProviderSeriesAdicto
from LinksProviderPordede import LinksProviderPordede

from Season import Link
from Tools import isNumber

from threading import Thread
import time
from Queue import Queue

class CtrlProviders():

    def __init__ (self, tmpPath):

        self.TMP_PATH = tmpPath
        #self._infoProviderImdb = InfoProviderImdb ()
        self._infoProviderTvmaze =  InfoProviderTvmaze ()

        #self._linkProviders = [LinksProviderPordede(), LinksProviderSeriesAdicto(), LinksProviderSeriesFlv(), LinksProviderSeriesPepito()]
        #self._linkProviders = [LinksProviderPordede(), LinksProviderSeriesAdicto(), LinksProviderSeriesPepito()]
        self._linkProviders = [LinksProviderPordede()]

    def downloadVideo (self, url, host, name):
        if 'streamcloud' in host.lower():
            d = DownloadStreamCloud ()
            downloadErr = d.downloadVideo (url, self.TMP_PATH + name)
        elif 'nowvideo' in host.lower():
            d = DownloadNowVideo ()
            downloadErr = d.downloadVideo (url, self.TMP_PATH + name)
        #elif 'streamplay' in host.lower():
        #    d =  DownloadStreamPlay ()
        #    downloadErr = d.downloadVideo (url, self.TMP_PATH + name)
        #elif 'streamin' in host.lower() or 'streaminto' in host.lower():
        ##    d =  DownloadStreamin ()
        #    downloadErr = d.downloadVideo (url, self.TMP_PATH + name)

    def loadSerie (self, serieName):
        #data = self._infoProviderImdb.loadSerie (serieName)
        data = self._infoProviderTvmaze.loadSerie (serieName)
        #if data == None:
			#data = self._infoProviderAnime.loadSerie (serieName)
			#if data == None:
				#...
            #raise Exception ('Serie "' + serieName + '" not found')
        return data

    def getSuggerencies (self):
        #return self._infoProviderImdb.getSuggerencies ()
        return self._infoProviderTvmaze.getSuggerencies ()

    def getMainInfo (self, serieName):
        q = Queue()

        threads = []

        for linkProvider in self._linkProviders:
            threads.append(Thread(target=linkProvider.getMainPageLink, args=(serieName, q)))

        for thread in threads: thread.start()
        for thread in threads: thread.join()

        mainPages = []

        while q.qsize() > 0:
            mainPages.append(q.get())

        return mainPages

    def getChapterUrls (self, mainPagesLinks, seasonNumber, chapterNumber, languages):
        q = Queue()

        threads = []
        for mainPage, linkProvider in [(x[1], y) for x in mainPagesLinks for y in self._linkProviders if x[0] == y._name]:
            threads.append(Thread(target=linkProvider.getChapterUrls, args=(mainPage, seasonNumber, chapterNumber, q)))

        for thread in threads: thread.start()
        for thread in threads: thread.join()

        dataTmp = []
        data = []

        while q.qsize() > 0:
            dataTmp.append(q.get()[1])

        itLang = 0

        while itLang < len (languages ['languages']):
            itList = 0
            while itList < len (dataTmp):
                if languages ['languages'] [itLang].lower () in dataTmp [itList].getLanguage ().lower () and languages ['subtitles'] [itLang].lower () in dataTmp [itList].getSubtitles ().lower ():
                    data.append (dataTmp [itList])

                itList = itList + 1
            itLang = itLang + 1

        if len (data) == 0:
            return 0

        return data
