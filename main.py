#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Domain import Domain
from sys import stdin, stdout
from Tools import isNumber, readString, readInt

def showInfo ():
    print ''
    print ' -> view [serieName]'
    print ' -> update [serieName]'
    print ' -> download [serieName] [seasonNumber] [chapterNumber]'
    print ' -> download-next [serieName]'
    print ' -> download-season [serieName] [seasonNumber]'
    print ' -> help (show help)'
    print ' -> quit (exit)\n'
    stdout.write('  <- ')

def main ():

    domain = Domain ()
    showInfo ()
    read = readString('')

    while read != 'quit':

        if read == 'help':
            showInfo ()
        elif read == 'view':
            serieName = readString ('serie name')
            domain.viewSerie (serieName)

        elif read == 'update':
            serieName = readString ('serie name')
            domain.updateSerie (serieName)

        elif read == 'download':
            serieName = readString ('serie name')
            seasonNumber = readInt ('season')
            chapterNumber = readInt ('chapter number')
            domain.downloadChapter (serieName, seasonNumber, chapterNumber)

        elif read == 'download-next':
            serieName = readString ('serie name')
            domain.downloadNext (serieName)

        elif read == 'download-season':
            serieName = readString('serie name')
            seasonNumber = readInt('season')
            domain.downloadSeason (serieName, seasonNumber)

        else:
            print ' -> option "' + read + '" doesn\'t exist'

        stdout.write ('  <- ')
        read = readString ('')

main ()
