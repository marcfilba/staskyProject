#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plexapi.myplex import MyPlexAccount
from Domain import Domain

d = Domain ()

account = MyPlexAccount.signin (d.getPlexUsername (), d.getPlexPassword ())
plex = account.resource (d.getPlexServerName ()).connect()



import requests
from Parser import Parser

def main ():
    imdbTvMeter = 'http://www.imdb.com/chart/tvmeter'
    r = requests.get (imdbTvMeter)

    if r.status_code != 200:
        return

    _parser = Parser ()
    data = _parser.feed (r.text)

    clazz = data.get_by (clazz = 'lister-list')

    if len (clazz) == 0:
        print 'mierda'
        return

    for e in clazz [0].get_childs () [:25]:
        serieName = e.get_childs ()[1].get_childs ()[0].data [0]

        found = False
        plexSeries = plex.library.section (title = 'Series de TV')

        for plexSerie in plexSeries.all ():
            if serieName == plexSerie.title:
                found = True

        if not found:
            d.addToDownloadQueue (serieName, 1, 1)


main ()
