#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyvirtualdisplay import Display
from selenium import webdriver
from LinksProvider import LinksProvider
import requests
#import time

from Parser import Parser
from Season import Link

class LinksProviderSeriesFlv(LinksProvider):

    def __init__ (self):
        super(LinksProviderSeriesFlv, self).__init__('seriesflv', 'http://www.seriesflv.net/api/')

    def getMainPageLink (self, serieName, q):
        if serieName == 'house m.d.':
            serieName = 'house, m.d.'

        elif serieName == 'sons of anarchy':
            serieName = 'hijos de la anarquia'

        display = Display (visible=0, size=(800, 600))
        display.start ()

        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.get(self._URL)

        #r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })

        #print r.status_code
        #if r.status_code != 200:
        #    raise Exception ('  -> error getting serie from SeriesFlv')
        html = driver.page_source

        if 'is currently offline' in html:
            driver.quit()
            display.stop()
            raise Exception (' -> web SeriesFlv offline')

        _parser = Parser ()
        data = _parser.feed (html)

        if len (data.get_by (tag = 'a')) < 1:
            driver.quit()
            display.stop()
            raise Exception ('  -> serie "' + serieName + '" not found in SeriesFlv')

        driver.quit()
        display.stop()
        q.put((self._name, data.get_by (tag = 'a')[0].attrs['href'][0]))

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):

        #r = requests.get (serieUrl, headers={ "user-agent": "Mozilla/5.0" })

        #if r.status_code != 200:
        #    raise Exception ('  -> error getting serie from SeriesFlv')

        display = Display (visible=0, size=(800, 600))
        display.start ()

        driver = webdriver.Firefox()
        driver.set_page_load_timeout(60)

        _parser = Parser ()
        driver.get(serieUrl)
        html = driver.page_source

        data = _parser.feed (html)
        td = data.get_by (tag = 'td', clazz = 'sape')

        cNumber = ''
        found = False
        if chapterNumber < 10:
            cNumber = '0'
        cNumber += str(chapterNumber)

        chapterUrlArray = []
        for t in td:
            print chapterUrlArray
            if not found and ' ' + str(seasonNumber) + 'x' + cNumber in str(t.get_childs()[1].attrs['data'][0].encode('utf-8')):
                found = True
                url = str(t.get_childs()[1].attrs['href'][0])
                driver.get(url)
                html = driver.page_source
                data = _parser.feed (html)

                tbody = data.get_by (tag = 'tbody')[0]
                for tr in tbody.get_childs ():
                    l = Link ()

                    l.setProviderName (self._name)

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

                    host = str (tr.get_childs ()[2].get_childs()[0].data[0]).lower ()
                    url = str (tr.get_childs ()[3].get_childs()[0].attrs['href'][0])

                    l.setHost (host)

                    r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                    data = _parser.feed (html)
                    l.setURL (str(data.get_by (tag = 'meta')[0].attrs['content'][0].split('=')[1]))

                    itemFound = False
                    for item in chapterUrlArray:
                        if str(item.getURL ()) == str(l.getURL ()):
                            itemFound = True

                    if not itemFound:
                        chapterUrlArray.append (l)

        for elem in chapterUrlArray:
            q.put((self._name, elem))
