#!/usr/bin/env python
# -*- coding: utf-8 -*-

from LinksProvider import LinksProvider

import cfscrape
from Parser import Parser
from Tools import isValidHost

from Season import Link

class LinksProviderSeriesFlv (LinksProvider):

    def __init__ (self):
        super (LinksProviderSeriesFlv, self).__init__('seriesflv', 'http://www.seriesflv.net/')

    def getMainPageLink (self, serieName, q):
        scraper = cfscrape.create_scraper()
        s = scraper.get (self._URL + 'api/search/?q=' + serieName.lower ())

        _parser = Parser ()
        data = _parser.feed (s.content.decode ('utf8'))

        series = data.get_by (clazz = 'on over')

        if len (series) > 0:
            #print 'found ' + str (series [0].attrs ['href'][0])
            q.put((self._name, str (series [0].attrs ['href'][0])))


    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):

        scraper = cfscrape.create_scraper()
        s = scraper.get (serieUrl)

        _parser = Parser ()
        data = _parser.feed (s.content.decode ('utf-8'))

        td = data.get_by (tag = 'td', clazz = 'sape')

        cNumber = ''
        found = False
        if chapterNumber < 10:
            cNumber = '0'
        cNumber += str(chapterNumber)

        chapterUrlArray = []
        for t in td:
            if not found and ' ' + str(seasonNumber) + 'x' + cNumber in str(t.get_childs()[1].attrs['data'][0].encode('utf-8')):
                found = True
                url = str(t.get_childs()[1].attrs['href'][0])
                s = scraper.get (url)
                data = _parser.feed (s.content.decode ('utf-8'))

                tbody = data.get_by (tag = 'tbody')[0]
                for tr in tbody.get_childs ():

                    host = str (tr.get_childs ()[2].get_childs()[0].data[0]).lower ()
                    if (isValidHost (host)):

                        l = Link ()

                        l.setHost (host)
                        l.setProviderName (self._name)

                        url = str (tr.get_childs ()[3].get_childs()[0].attrs['href'][0])
                        s = scraper.get (url)

                        data = _parser.feed (s.content.decode ('utf-8'))
                        l.setURL (str(data.get_by (tag = 'meta')[0].attrs['content'][0].split('=')[1]))

                        langFlagUrl = str (tr.get_childs ()[0].get_childs()[0].attrs['src'][0])
                        langFlagImg = langFlagUrl.split ('/') [len (langFlagUrl.split ('/')) -1]

                        if 'es.' in langFlagImg:
                            l.setLanguage ('Spanish')
                        elif 'la.' in langFlagImg:
                            l.setLanguage ('Latin')
                        elif 'sub.' in langFlagImg:
                            l.setLanguage ('English')
                            l.setSubtitles ('Spanish')
                        elif 'en.' in langFlagImg:
                            l.setLanguage ('English')
                        elif 'vosi.' in langFlagImg:
                            l.setLanguage ('English')
                            l.setSubtitles ('English')

                        itemFound = False
                        for item in chapterUrlArray:
                            if str(item.getURL ()) == str(l.getURL ()):
                                itemFound = True

                        if not itemFound:
                            chapterUrlArray.append (l)

        for elem in chapterUrlArray:
            q.put((self._name, elem))
