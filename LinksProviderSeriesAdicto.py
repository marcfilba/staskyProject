#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from LinksProvider import LinksProvider

from Parser import Parser
from Tools import isValidHost

from Season import Link

from Queue import Queue

class LinksProviderSeriesAdicto(LinksProvider):

    def __init__ (self):
        super(LinksProviderSeriesAdicto, self).__init__('seriesadicto', 'http://seriesadicto.com/')

    def getMainPageLink (self, serieName, q):
        try:
            if serieName == 'house m.d.':
                serieName = 'house, m.d.'

            url = self._URL + 'buscar/' + serieName.replace(' ', '%20')
            r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })

            if r.status_code != 200:
                #raise Exception ('  -> error getting serie from SeriesAdicto')
                return

            _parser = Parser ()
            data = _parser.feed (r.text)

            clazz = data.get_by (clazz = 'col-xs-6 col-sm-4 col-md-2')
            if len (clazz) == 0:
                #raise Exception ('  -> serie "' + serieName + '" not found in SeriesAdicto')
                return

            q.put((self._name, self._URL[:-1] + str(clazz[0].get_childs()[0].attrs['href'][0])))
        except Exception as e:
            print str (e)
            pass

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):
        #print '  -> Searching in ' + str (self._name) + '...'

        r = requests.get (serieUrl, headers={ "user-agent": "Mozilla/5.0" })

        if r.status_code != 200:
            #raise Exception ('  -> error getting serie from SeriesAdicto')
            return

        _parser = Parser ()
        data = _parser.feed (r.text)
        td = data.get_by (tag = 'td', clazz = 'sape')

        cNumber = ''
        found = False

        chapterUrlArray = []
        for t in td:
            try:
                if not found and len (t.get_childs()) > 1 and '/' + str(seasonNumber) + '/' + str(chapterNumber) in str(t.get_childs()[1].attrs['href'][0]):
                    found = True
                    url = self._URL + str(t.get_childs()[1].attrs['href'][0])

                    r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                    data = _parser.feed (r.text)

                    tbody = data.get_by (tag = 'tbody')[0]
                    for tr in tbody.get_childs ():
                        try:

                            host = str (tr.get_childs ()[1].data[0]).lower ()

                            if isValidHost (host):
                                url = str (tr.get_childs ()[2].get_childs()[0].attrs['href'][0])

                                langFlagUrl = str (tr.get_childs ()[0].get_childs()[0].attrs['src'][0])
                                langFlagImg = langFlagUrl.split ('/') [len (langFlagUrl.split ('/')) -1]

                                l = Link ()

                                if '1.' in langFlagImg:
                                    l.setLanguage ('Spanish')
                                elif '2.' in langFlagImg:
                                    l.setLanguage ('Latin')
                                elif '3.' in langFlagImg:
                                    l.setLanguage ('English')
                                    l.setSubtitles ('Spanish')
                                elif '4.' in langFlagImg:
                                    l.setLanguage ('English')

                                l.setProviderName (self._name)

                                l.setHost (host)
                                l.setURL (url)

                                itemFound = False
                                for item in chapterUrlArray:
                                    if str(item.getURL ()) == str(l.getURL ()):
                                        itemFound = True

                                if not itemFound:
                                    chapterUrlArray.append (l)

                        except Exception as e:
                            print str (e)
                            pass
            except Exception as e:
                print str (e)
                pass

        for elem in chapterUrlArray:
            q.put((self._name, elem))
