#!/usr/bin/env python
# -*- coding: utf-8 -*-

from LinksProvider import LinksProvider

import cfscrape
from Parser import Parser
from Tools import isValidHost

from Season import Link
from threading import Thread

class LinksProviderPordede(LinksProvider):

    def __init__ (self):
        super(LinksProviderPordede, self).__init__('pordede', 'http://pordede.com/')

        self.headers = {
            'Accept' : '*/*',
            'Accept-Encoding' : 'gzip, deflate',
            'Connection' : 'keep-alive',
            'Content-Length' : '104',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host' : 'www.pordede.com',
            'Referer' : 'http://www.pordede.com/',
            'User-Agent' : 'Mozilla/5.0'
        }

        self.data = {
            'LoginForm[username]': 'gunkyProject',
            'LoginForm[password]': '123456',
            'popup' : '1',
            'sesscheck' : 'ne09kk9c0ua7mgdjmcn6qs9fq1'
        }

    def getMainPageLink (self, serieName, q):

        if serieName.lower() == 'daredevil':
            serieName = "marvel's daredevil"
        elif serieName.lower() =='gambling apocalypse kaiji':
            serieName = 'kaiji'

        scraper = cfscrape.create_scraper()
        s = scraper.post (self._URL + 'site/login', headers = self.headers, data = self.data)
        s = scraper.post (self._URL + 'search/autocomplete?popup=1', headers = self.headers, data = {"query" : serieName.lower ()})

        _parser = Parser ()
        data = _parser.feed (s.content)

        films = data.get_by (clazz = 'info')

        for f in films:
            if "Serie" in f.childs[1].attrs['data'][0]:
                q.put((self._name, self._URL + f.childs[0].attrs['href'][0][1:]))
                break
        return

    def getLinkInfo (self, chapterLink, scraper, q):
        try:
            childs = chapterLink.get_childs()[0].get_childs()
            host = str(childs[0].get_childs()[0].attrs['src'][0].split ('_')[1].split('.')[0])

            _parser = Parser ()

            if isValidHost (host):
                flags = childs[1].get_by (tag = 'div')

                l = Link ()

                l.setProviderName (self._name)
                if 'spanish' in flags[0].attrs['class'][0]:
                    if 'LAT' in flags[0].attrs['data'][0]:
                        l.setLanguage ("Latin")
                    else:
                        l.setLanguage ("Spanish")
                elif 'english' in flags[0].attrs['class'][0]:
                    l.setLanguage ('English')

                if (len (flags) == 2):
                    if 'spanish' in flags[1].attrs['class'][0]:
                        l.setSubtitles ('Spanish')
                    else:
                        l.setSubtitles ('English')

                l.setHost (host)

                url = str(self._URL[:-1] + chapterLink.attrs['href'][0])

                s = scraper.post (url, headers = self.headers)
                data = _parser.feed (s.content)
                url = data.get_by (clazz = 'episodeText')[0].attrs['href'][0]

                s =  scraper.post (self._URL[:-1] + url, headers = self.headers)

                l.setURL (s.url)

                q.put((self._name, l))

        except Exception as e:
            #print str (e)
            pass

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):
        try:
            scraper = cfscrape.create_scraper()

            s = scraper.post (self._URL + 'site/login', headers = self.headers, data = self.data)
            s = scraper.post (serieUrl, headers = self.headers)

            _parser = Parser ()
            data = _parser.feed (s.content)

            seasons = data.get_by (clazz = 'episodes')

            linkToChapter = ''
            for s in seasons:
                if 'episodes-' + str(seasonNumber) in s.attrs['id'][0]:
                    chapters = s.get_by (clazz = 'info')
                    for c in chapters:
                        for n in c.get_by (clazz = 'number'):
                            if n.attrs['data'][0] in str(chapterNumber):
                                linkToChapter = self._URL[:-1] + c.get_childs()[0].attrs['href'][0]

            s = scraper.post (linkToChapter, headers = self.headers)

            data = _parser.feed (s.content)

            onlineLinks = data.get_by (clazz = 'linksPopup')[0].get_childs()[3]
            chapterLinks = onlineLinks.get_by (clazz = 'a aporteLink done')

            for e in chapterLinks:
                self.getLinkInfo (e, scraper, q)

        except Exception as e:
            #print str (e)
            pass
