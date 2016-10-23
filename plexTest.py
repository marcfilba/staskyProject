#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plexapi.myplex import MyPlexAccount
from Domain import Domain
from threading import Thread
from time import sleep

d = Domain ()

account = MyPlexAccount.signin (d.getPlexUsername (), d.getPlexPassword ())
plex = account.resource (d.getPlexServerName ()).connect()

plexSeries = plex.library.section (title = 'Series de TV')

def downloadNext (serie, seasonNumber, chapterNumber):
    if serie.chapterNumberExists (seasonNumber, chapterNumber + 1):
        d.addToDownloadQueue (serie.getName (), seasonNumber, chapterNumber + 1)
    else:
        if serie.seasonExists (seasonNumber + 1):
            if serie.chapterNumberExists (seasonNumber + 1, 1):
                d.addToDownloadQueue (serie.getName (), seasonNumber + 1, 1)


def checkDownloads (plexSeries):
    print 'checkDownloads'
    while True:
        for plexSerie in plexSeries.all ():
            try:
                if len (plexSerie.unwatched ()) < 5:
                    dbSerie = d._getSerie (plexSerie.title.encode('utf-8'))
                    if len (plexSerie.unwatched ()) > 0:
                        plexChapterToDownload = plexSerie.unwatched () [len (plexSerie.unwatched ()) - 1]
                        downloadNext (dbSerie, int (plexChapterToDownload.seasonNumber), int(plexChapterToDownload.index))
                    else:
                        lastChapterWatched = plexSerie.watched () [len (plexSerie.watched ()) - 1]
                        downloadNext (dbSerie, int (lastChapterWatched.seasonNumber), int (lastChapterWatched.index))
            except Exception as e:
                print str (e)
                pass
        sleep (3 * 3600)


def updateSeriesInfo (plexSeries):
    print 'updateSeriesInfo'
    while True:
        for plexSerie in plexSeries.all ():
            try:
                if len (plexSerie.unwatched ()) < 5:
                    dbSerie = d._getSerie (plexSerie.title.encode('utf-8'))
                    d.updateExistingSerie (dbSerie)
            except Exception as e:
                print str (e)
                pass
        sleep (24 * 3600)

threads = []
threads.append (Thread (target = checkDownloads,   args = (plexSeries,)))
threads.append (Thread (target = updateSeriesInfo, args = (plexSeries,)))

for t in threads: t.start ()
