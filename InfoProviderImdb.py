#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import imdb
import json

from InfoProvider import InfoProvider

class InfoProviderImdb (InfoProvider):

    def __init__ (self):
        self._imdb = imdb.IMDb ()
        self._imdbAPIurl = 'http://www.omdbapi.com/?'
        self._suggerencies = []
        InfoProvider.__init__ (self, 'IMDB')

    def _getSerie (self, imdbID):
        r = requests.get(self._imdbAPIurl + 'type=serie' + '&i=tt' + imdbID)
        return r.text

    def _getEpisodes (self, imdbID):
        season = 1
        data = '['
        r = requests.get(self._imdbAPIurl + 'i=tt' + imdbID + '&Season=' + str (season))
        while json.loads(r.text) ['Response'] == "True":
            data += r.text + ', '
            season += 1
            r = requests.get(self._imdbAPIurl + 'i=tt' + imdbID + '&Season=' + str (season))
        return data [:-2] + ']'

    def loadSerie (self, serieName):
        res = self._imdb.search_movie(serieName)
        self._suggerencies = []
        data = ''

        for r in res:
            if r ['kind'] == 'tv series':
                self._suggerencies.append (str (r))
                if serieName.lower () == str (r).lower ():
                    serie = self._getSerie (r.movieID)
                    data = self._getEpisodes (r.movieID)

                    return '{ "serie" : ' + serie +', "seasons" : ' + data + '}'

    def getSuggerencies (self):
        return self._suggerencies

#imdb = InfoProviderImdb ()
#print imdb.loadSerie ('bones')
