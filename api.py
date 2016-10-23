#!/usr/bin/python
# -*- coding: utf-8 -*-

from Domain import Domain
from Tools import isNumber

from plexapi.myplex import MyPlexAccount
from threading import Thread
from flask import Flask, request
from sys import exit
from time import sleep

import os
import signal

app = Flask ("StaskyProject")
d = Domain ()

account = MyPlexAccount.signin (d.getPlexUsername (), d.getPlexPassword ())
plex = account.resource (d.getPlexServerName ()).connect()

plexSeries = plex.library.section (title = 'Series de TV')

@app.route ("/addChapterToDownloadQueue")
def addSerieToDownloadQueue():
    serieName = request.args.get ('serieName')
    seasonNumber = request.args.get ('seasonNumber')
    chapterNumber = request.args.get ('chapterNumber')

    if serieName is None:
        return '{"err" : 1, "message" : "serieName not specified"}'
    elif seasonNumber is None:
        return '{"err" : 1, "message" : "seasonNumber not specified"}'
    elif chapterNumber is None:
        return '{"err" : 1, "message" : "chapterNumber not specified"}'
    elif not isNumber (seasonNumber):
        return '{"err" : 1, "message" : "seasonNumber is not a number"}'
    elif not isNumber (chapterNumber):
        return '{"err" : 1, "message" : "chapterNumber is not a number"}'

    d.addToDownloadQueue (serieName.replace ('_', ' '), seasonNumber, chapterNumber)

    return '{"err" : 0, "message" : "chapter added to the download queue"}'


def downloadNext (serie, seasonNumber, chapterNumber):
    if serie.chapterNumberExists (seasonNumber, chapterNumber + 1):
        d.addToDownloadQueue (serie.getName (), seasonNumber, chapterNumber + 1)
    else:
        if serie.seasonExists (seasonNumber + 1):
            if serie.chapterNumberExists (seasonNumber + 1, 1):
                d.addToDownloadQueue (serie.getName (), seasonNumber + 1, 1)


def checkDownloads (plexSeries):
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
                d.simpleLog (dbSerie.getName (), 'error checking downloads (' + str (e) + ')')
                pass
        sleep (3 * 3600)


def updateSeriesInfo (plexSeries):
    while True:
        for plexSerie in plexSeries.all ():
            try:
                if len (plexSerie.unwatched ()) < 5:
                    dbSerie = d._getSerie (plexSerie.title.encode('utf-8'))
                    d.updateExistingSerie (dbSerie)
            except Exception as e:
                d.simpleLog (dbSerie.getName (), 'error updating serieInfo (' + str (e) + ')')
                pass
        sleep (24 * 3600)


def processDownloadQueue ():
    maxWorkerThreads    = 3
    actualWorkerThreads = 0
    threads             = []
    chapterIds          = []

    while True:
        sleep (5)
        queue = d.getPendingQueue ()
        if (queue.count () > 0 and actualWorkerThreads < maxWorkerThreads):
            actualWorkerThreads = actualWorkerThreads + 1

            d.log (queue [0] ['serieName'], int (queue [0] ['seasonNumber']), int(queue [0] ['chapterNumber']), 'processing')
            chapterIds.append ({'serieName' : queue [0] ['serieName'], 'seasonNumber' : queue [0] ['seasonNumber'], 'chapterNumber' : queue [0] ['chapterNumber']})
            threads.append (Thread (target = d.processSingleDownload, args = (queue [0] ['serieName'], queue [0] ['seasonNumber'], queue [0] ['chapterNumber'])))

            d.markItemAsNotPending (queue [0] ['serieName'], queue [0] ['seasonNumber'], queue [0] ['chapterNumber'])
            threads [len (threads) -1].start ()

        it = 0
        while it < len (threads):
            if not threads [it].is_alive ():
                threads [it].join ()
                d.downloadedFromDownloadQueue (chapterIds [it] ['serieName'], chapterIds [it] ['seasonNumber'], chapterIds [it] ['chapterNumber'])
                actualWorkerThreads = actualWorkerThreads - 1
                threads.pop (it)
                chapterIds.pop (it)
            it = it + 1

def flask (app):
    app.run (port = 10926, host = '0.0.0.0')

if __name__ == '__main__':

    if os.fork() != 0:
        exit(0)

    threads = []
    threads.append (Thread (target = checkDownloads,   args = (plexSeries,)))
    threads.append (Thread (target = updateSeriesInfo, args = (plexSeries,)))
    threads.append (Thread (target = processDownloadQueue))
    threads.append (Thread (target = flask,            args = (app,)))

    #pid = os.getpid ()
    #print "PID: " + str(pid)
    for t in threads: t.start ()
