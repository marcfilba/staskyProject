#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import imdb
import json

from time import sleep

from InfoProvider import InfoProvider
from sys import exit

class InfoProviderTvmaze (InfoProvider):

    def __init__ (self):
        self._imdb = imdb.IMDb ()
        self._tvmazeAPIurl = 'http://api.tvmaze.com'
        self._suggerencies = []
        InfoProvider.__init__ (self, 'TVMAZE')

    def _getSerie (self, serieName):

        r = requests.get(self._tvmazeAPIurl + '/singlesearch/shows?' + 'q=' + serieName)
        while r.status_code == 429:
            sleep (1)
            r = requests.get(self._tvmazeAPIurl + '/singlesearch/shows?' + 'q=' + serieName)

        serieData = json.loads (r.text)
        ret = {}
        ret ['title'] = serieData ['name']
        ret ['id'] = serieData ['id']
        ret ['schedule'] = serieData ['schedule']
        ret ['genres'] = serieData ['genres']
        ret ['summary'] = serieData ['summary']
        ret ['status'] = serieData ['status']
        ret ['rating'] = serieData ['rating']

        return json.dumps (ret)

    def _getEpisodes (self, serieId):
        season = 1
        data = '['
        r = requests.get (self._tvmazeAPIurl + '/shows/' + str(serieId) + '/episodes')
        while r.status_code == 429:
            sleep (1)
            r = requests.get (self._tvmazeAPIurl + '/shows/' + str(serieId) + '/episodes')

        tvmazeEpisodes = json.loads (r.text)
        seasonNumber = 1
        seasons = []
        season = {}
        episodes = []
        for e in tvmazeEpisodes:

            if seasonNumber != e ['season']:
                season ['season'] = seasonNumber
                season ['episodes'] = episodes
                seasons.append (season)
                season = {}
                episodes = []
                seasonNumber = seasonNumber + 1

            episode = {}
            episode ['id'] = e ['id']
            episode ['title'] = e ['name']
            episode ['url'] = e ['url']
            episode ['airDate'] = e ['airdate']
            episode ['number'] = e ['number']
            episodes.append (episode)

        season ['season'] = seasonNumber
        season ['episodes'] = episodes
        seasons.append (season)

        return json.dumps(seasons)


    def loadSerie (self, serieName):
        res = self._imdb.search_movie(serieName)
        self._suggerencies = []
        data = ''

        for r in res:
            if r ['kind'] == 'tv series':
                self._suggerencies.append (str (r))
                if serieName.lower () == str (r).lower ():
                    serie = self._getSerie (serieName.lower ())
                    data = self._getEpisodes (json.loads (serie) ['id'])

                    return '{ "serie" : ' + serie +', "seasons" : ' + data + '}'

    def getSuggerencies (self):
        return self._suggerencies

#tvmaze = InfoProviderTvmaze ()
#print tvmaze.loadSerie ("daredevil")
#print tvmaze.loadSerie ("grey's anatomy")
