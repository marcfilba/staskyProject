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
from datetime import datetime

import os
import signal

app = Flask ("StaskyProject")
d = Domain ()

account = MyPlexAccount.signin (d.getPlexUsername (), d.getPlexPassword ())
plex = account.resource (d.getPlexServerName ()).connect()

threads = []

@app.route ("/addChapterToDownloadQueue")
def addSerieToDownloadQueue ():
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

    d.addToDownloadQueue (serieName.replace ('_', ' '), int (seasonNumber), int (chapterNumber), 0)

    return '{"err" : 0, "message" : "chapter added to the download queue"}'

@app.route ("/threadsRunning")
def threadsRunning ():
    if len (threads) == 4:
        ret = '{"err" : 0, "message" : {'
        for t in threads:
            ret = ret + '"' + t.getName () + '" : '
            if t.is_alive:
                ret = ret + 'true, '
            else:
                ret = ret + 'false, '
        return ret [: -2] + '}}'

    return '{"err" : 0, "message" : "testing mode"}'


def downloadNext (serie, seasonNumber, chapterNumber):
    try:
        now = datetime.now().date ()
        if serie.chapterNumberExists (seasonNumber, chapterNumber + 1):
            releaseDateSt = serie.getSeason (seasonNumber -1).getChapters () [chapterNumber].getReleaseDate ()
            releaseDate = datetime.strptime(releaseDateSt, '%Y-%m-%d').date()

            if releaseDate <= now:
                d.addToDownloadQueue (serie.getName (), seasonNumber, chapterNumber + 1, 0)
                #print 'downloading ' + str(seasonNumber) + "x" + str (chapterNumber + 1)
        elif serie.seasonExists (seasonNumber + 1):
                if serie.chapterNumberExists (seasonNumber + 1, 1):
                    releaseDateSt = serie.getSeason (seasonNumber).getChapters () [0].getReleaseDate ()
                    releaseDate = datetime.strptime(releaseDateSt, '%Y-%m-%d').date()

                    if releaseDate <= now:
                        d.addToDownloadQueue (serie.getName (), seasonNumber + 1, 1, 0)
                        #print 'downloading ' + str(seasonNumber + 1) + "x" + str (1)

    except Exception as e:
        pass
        #print str (e)


def checkDownloads ():
    while True:
        plexSeries = plex.library.section (title = 'Series de TV')
        print str (len (plexSeries.all ())) + " series found"
        for i, plexSerie in enumerate (plexSeries.all ()):
            try:
                print " " + str (i + 1) + " - " + plexSerie.title
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
                        print " -> error checking " + str (e)
                        #d.simpleLog (plexSerie.title, 'error checking (' + str (e) + ')')

            except Exception as e:
                print " -> not found " + str (e)
                #d.simpleLog (plexSerie.title, 'not found (' + str(e) + ')')

        sleep (1800) # 30 minutes


def updateSeriesInfo ():
    while True:
        plexSeries = plex.library.section (title = 'Series de TV')
        print str (len (plexSeries.all ())) + " series found"
        for i, plexSerie in enumerate (plexSeries.all ()):
            print " " + str (i + 1) + " - " + plexSerie.title
            try:
                dbSerie = d._getSerie (plexSerie.title.encode('utf-8', 'ignore'))
                #dbSerie = d._getSerie ( str(unicodedata.normalize('NFKD', unicode (plexSerie.title, 'utf-8')).encode('ASCII', 'ignore')))
                d.updateExistingSerie (dbSerie)
            except Exception as e:
                print ' -> ' + str (e)
                #d.simpleLog (plexSerie.title, 'error updating serieInfo (' + str (e) + ')')
                pass
        sleep (12 * 3600)

def chapterDownloadedSuccessful (serie, seasonNumber, chapterNumber):
    plexSeries = plex.library.section (title = 'Series de TV')
    for i, plexSerie in enumerate (plexSeries.all ()):
        if serie == plexSerie.title.lower ():
            for s in plexSerie.seasons ():
                if int(s.seasonNumber) == seasonNumber:
                    for e in s.episodes ():
                        if int (e.index) == chapterNumber:
                            return True
    return False

def processDownloadQueue ():
    maxWorkerThreads    = 3
    actualWorkerThreads = 0
    threads             = []
    chapterIds          = []

    while True:
        sleep (3)
        queue = d.getPendingQueue ()
        if (queue.count () > 0) and (actualWorkerThreads < maxWorkerThreads):
                try:
                    if (queue [0] ['retries'] <= 0):
                        print "Poso " + queue [0] ['serieName'] + ' ' + str(queue [0] ['seasonNumber']) + 'x' + str(queue [0] ['chapterNumber']) + ' a la cua'
                        chapterIds.append ({'serieName' : queue [0] ['serieName'], 'seasonNumber' : queue [0] ['seasonNumber'], 'chapterNumber' : queue [0] ['chapterNumber'], 'retries' : queue [0] ['retries']})

                        threads.append (Thread (target = d.processSingleDownload, args = (queue [0] ['serieName'], queue [0] ['seasonNumber'], queue [0] ['chapterNumber'])))
                        d.markItemAsNotPending (queue [0] ['serieName'], queue [0] ['seasonNumber'], queue [0] ['chapterNumber'])

                        threads [len (threads) -1].start ()
                        actualWorkerThreads = actualWorkerThreads + 1
                    else:
                        print 'retries ' + queue [0] ['serieName'] + ' ' + str(queue [0] ['seasonNumber']) + 'x' + str(queue [0] ['chapterNumber']) + '-> ' + str (queue [0] ['retries'])

                        serieName = queue [0] ['serieName']
                        seasonNumber = queue [0] ['seasonNumber']
                        chapterNumber = queue [0] ['chapterNumber']
                        retries = queue [0] ['retries'] - queue.count ()

                        d.downloadedFromDownloadQueue (queue [0] ['serieName'], queue [0] ['seasonNumber'], queue [0] ['chapterNumber'])
                        d.addToDownloadQueue (serieName, seasonNumber, chapterNumber, retries)

                except Exception as e:
                    print str (e)
                    d.simpleLog (queue [0] ['serieName'], str (e))

        it = 0
        while it < len (threads):
            if not threads [it].is_alive ():
                threads [it].join ()
                d.downloadedFromDownloadQueue (chapterIds [it] ['serieName'], chapterIds [it] ['seasonNumber'], chapterIds [it] ['chapterNumber'])
                if  (not chapterDownloadedSuccessful (chapterIds [it] ['serieName'], chapterIds [it] ['seasonNumber'], chapterIds [it] ['chapterNumber'])):
                    chapterIds [it] ['retries'] = 7200
                    d.addToDownloadQueue (chapterIds [it] ['serieName'], chapterIds [it] ['seasonNumber'], chapterIds [it] ['chapterNumber'], chapterIds [it] ['retries'])

                actualWorkerThreads = actualWorkerThreads - 1
                threads.pop (it)
                chapterIds.pop (it)
            it = it + 1


def flask (pid):
    try:
        app.run (port = 10927, host = '0.0.0.0')
    except:
        print 'Error initiating Stasky'
        os.kill (pid, signal.SIGKILL)


def main ():
    threads.append (Thread (name = 'checkDownloads',       target = checkDownloads))
    threads.append (Thread (name = 'updateSeriesInfo',     target = updateSeriesInfo))
    threads.append (Thread (name = 'processDownloadQueue', target = processDownloadQueue))
    threads.append (Thread (name = 'flask',                target = flask, args = (os.getpid (),)))

    for t in threads: t.start ()

if __name__ == '__main__':
    #daemon = Daemonize (app = 'stasky', pid = '/tmp/staskyPid', action = main)
    #daemon.start()
    #main ()

    updateSeriesInfo ()
    #checkDownloads ()
    #processDownloadQueue ()
