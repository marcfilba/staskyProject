#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Season import Season, Chapter
import imdb
import json
from sys import exit

class Serie ():

	def __init__ (self):
		self._name = ''
		self._description = ''
		self._mainPageLinks = []
		self._seasons = []
		self._keyNames = []
		self._languages = {"languages" : ["Spanish", "English"], "subtitles" : ["", "Spanish"]}
		self._substitles = ['', 'Spanish']
		self._imdb = imdb.IMDb()

	def getName (self):
		return self._name

	def getDescription (self):
		return self._description

	def getMainPageLinks (self):
		return self._mainPageLinks

	def getSeasons (self):
		return self._seasons

	def getSeason (self, i):
		return self._seasons [i]

	def getKeyNames (self):
		return self._keyNames

	def getChapter (self, season, chapterNumber):
		return self._seasons [season] [chapterNumber]

	def getLanguages (self):
		return self._languages

	def setKeyNames (self, keyNames):
		self._keyNames = keyNames

	def addKeyName (self, keyName):
		self._keyNames.append (keyName)

	def setLanguages (self, languages):
		self._languages = languages

	def setName (self, name):
		self._name = name

	def setDescription (self, description):
		self._description = description

	def setMainPageLinks (self, mainPageLinks):
		self._mainPageLinks = mainPageLinks

	def addSeason (self, season):
		self._seasons.append (season)

	def setSeasons (self, seasons):
		self._seasons = seasons

	def _loadChapter (self, episode):
		c = Chapter ()

		c.setName (episode ['Title'])
		c.setReleaseDate (episode ['Released'])

		return c


	def loadSerie (self, serieData):
		self.__init__ ()

		serieJson = json.loads(serieData)

		self._name = serieJson ['serie']['Title']
		self._keyNames.append (self._name.lower ())
		self._description = serieJson ['serie']['Plot']

		season = 0
		while season < len (serieJson['seasons']):
			s = Season ()
			chapter = 0
			try:
				while chapter < len(serieJson['seasons'][season]['Episodes']):
					c = Chapter ()

					episode = serieJson['seasons'][season]['Episodes'][chapter]
					c = self._loadChapter (episode)

					s.addChapter (c)
					chapter += 1

				self._seasons.append(s)

			except Exception as e:
				print e
				pass
			season += 1

	def seasonExists (self, seasonNumber):
		return len (self._seasons) >= seasonNumber


	def chapterNumberExists (self, seasonNumber, chapterNumber):
		return len (self._seasons [seasonNumber-1].getChapters ()) >= chapterNumber

	def printChapter (self, seasonNumber, chapterNumber):
		print '  -> number: ' + str (chapterNumber)
		self._seasons [seasonNumber-1].getChapters ()[chapterNumber-1].printChapter ()

	def toJson (self):
			d = {}
			d ['serieName'] = self._name
			d ['description'] = self._description
			d ['mainPageLinks'] = self._mainPageLinks
			d ['seasons'] = []

			for s in self._seasons:
				season = []
				for c in s._chapters:
					chap = {}
					chap ['chapterName'] = c.getName ()
					chap ['releaseDate'] = c.getReleaseDate ()
					chap ['links'] = []

					for l in c.getLinkArray ():
						link = {}
						link ['url'] = l.getURL ()
						link ['host'] = l.getHost ()
						link ['language'] = l.getLanguage ()
						link ['subtitles'] = l.getSubtitles ()
						link ['providerName'] = l.getProviderName ()

						chap['links'].append (link)
					season.append (chap)
				d ['seasons'].append (season)

			return d

	def printSerie (self):

		print ''
		print ' -> name: ' + self._name
		print ' -> description: ' + self._description
		print ' -> links [' + str(len(self._mainPageLinks)) + ']'
		for l in self._mainPageLinks:
			print '   -> (' + str(l [0]) + ')  \'' + str(l [1]) + '\''
		print ' -> seasons [' + str(len(self._seasons)) + ']'
		for n, s in enumerate (self._seasons):
			print '   -> season ' + str(n + 1) + ' [' + str (len(s.getChapters())) + ']'
		print ''
