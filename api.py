#!/usr/bin/python
# -*- coding: utf-8 -*-

from Domain import Domain
from Tools import isNumber

from daemonize import Daemonize
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
    try:
        if serie.chapterNumberExists (seasonNumber, chapterNumber + 1):
            d.addToDownloadQueue (serie.getName (), seasonNumber, chapterNumber + 1)
            #print 'downloading ' + str(seasonNumber) + "x" + str (chapterNumber + 1)
        elif serie.seasonExists (seasonNumber + 1):
                if serie.chapterNumberExists (seasonNumber + 1, 1):
                    d.addToDownloadQueue (serie.getName (), seasonNumber + 1, 1)
                    #print 'downloading ' + str(seasonNumber + 1) + "x" + str (1)

    except Exception as e:
        pass
        #print str (e)


def checkDownloads (plexSeries):
    while True:
        for plexSerie in plexSeries.all ():
            try:
                #print plexSerie.title
                if len (plexSerie.unwatched ()) < 5:
                    dbSerie = d._getSerie (plexSerie.title.encode('utf-8'))
                    try:
                        if len (plexSerie.unwatched ()) > 0:
                            unwatched = len (plexSerie.unwatched ())
                            lastChapterUnwatched = plexSerie.unwatched () [unwatched - 1]

                            seasonNumber = int (lastChapterUnwatched.seasonNumber)
                            chapterNumber = int(lastChapterUnwatched.index)

                            while unwatched < 5:
                                downloadNext (dbSerie, seasonNumber, chapterNumber)

                                if dbSerie.chapterNumberExists (seasonNumber, chapterNumber + 1):
                                    chapterNumber = chapterNumber + 1
                                elif dbSerie.seasonExists (seasonNumber + 1):
                                    seasonNumber = seasonNumber + 1
                                    chapterNumber = 1
                                else:
                                    unwatched = 5
                                unwatched = unwatched + 1
                        else:
                            unwatched = 0
                            lastChapterWatched = plexSerie.watched () [len (plexSerie.watched ()) - 1]

                            seasonNumber = int (lastChapterWatched.seasonNumber)
                            chapterNumber = int(lastChapterWatched.index)

                            while unwatched < 5:
                                downloadNext (dbSerie, seasonNumber, chapterNumber)

                                if dbSerie.chapterNumberExists (seasonNumber, chapterNumber + 1):
                                    chapterNumber = chapterNumber + 1
                                elif dbSerie.seasonExists (seasonNumber + 1):
                                    seasonNumber = seasonNumber + 1
                                    chapterNumber = 1
                                else:
                                    unwatched = 5
                                unwatched = unwatched + 1

                    except Exception as e:
                        #print str (e)
                        d.simpleLog (plexSerie.title, 'error checking ' + str (e))

            except Exception as e:
                #print str (e)
                d.simpleLog (plexSerie.title, 'not found ' + str(e))

        sleep (3 * 3600)


def updateSeriesInfo (plexSeries):
    while True:
        for plexSerie in plexSeries.all ():
            try:
                if len (plexSerie.unwatched ()) < 5:
                    dbSerie = d._getSerie (plexSerie.title.encode('utf-8'))
                    d.updateExistingSerie (dbSerie)
            except Exception as e:
                print str (e)
                d.simpleLog (plexSerie.title, 'error updating serieInfo (' + str (e) + ')')
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
            #print 'processing ' + queue [0] ['serieName']
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


def flask (app, pid):
    try:
        app.run (port = 10927, host = '0.0.0.0')
    except:
        os.kill (pid, signal.SIGKILL)


def main ():
    threads = []
    threads.append (Thread (target = checkDownloads,   args = (plexSeries,)))
    threads.append (Thread (target = updateSeriesInfo, args = (plexSeries,)))
    threads.append (Thread (target = processDownloadQueue))
    threads.append (Thread (target = flask,            args = (app, os.getpid (),)))
    for t in threads: t.start ()

if __name__ == '__main__':
    daemon = Daemonize (app = 'stasky', pid = '/tmp/staskyPid', action = main)
    daemon.start()
    #main ()
