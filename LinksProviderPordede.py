#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyvirtualdisplay import Display
from selenium import webdriver
from LinksProvider import LinksProvider
import requests
import time

from Parser import Parser
from Tools import isValidHost

from Season import Link

from threading import Thread
#from Queue import Queue

class LinksProviderPordede(LinksProvider):

    def __init__ (self):
        super(LinksProviderPordede, self).__init__('pordede', 'http://pordede.com/')

    def getMainPageLink (self, serieName, q):

        if serieName.lower() == 'daredevil':
            serieName = "marvel's daredevil"
	elif serieName.lower() =='gambling apocalypse kaiji':
	    serieName = 'kaiji'

        url = self._URL + 'site/login'

        display = Display (visible=0, size=(800, 600))
        display.start ()

        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.get(self._URL)

        tries = 10
        found = False

        while not found and tries > 0:
            try:
                driver.find_element_by_id ('LoginForm_username').send_keys('gunkyProject')
                driver.find_element_by_id ('LoginForm_password').send_keys('123456')
                found = True
            except Exception as e:
                time.sleep (1)
                tries -= 1
                if tries == 0:
                    driver.quit()
                    display.stop()
                    return
                    #raise Exception ('  -> Can\'t enter to SeriesPordede')

        driver.find_element_by_xpath("//form[@id='login-form']/button[1]").submit ()

        tries = 5
        found = False

        while not found and tries > 0:
            try:
                driver.find_element_by_class_name ('rounded1').send_keys(serieName)
                found = True
            except Exception as e:
                time.sleep (1)
                tries -= 1
                if tries == 0:
                    driver.quit()
                    display.stop()
                    raise Exception ('  -> Can\'t enter to SeriesPordede')

        tries = 5
        found = False

        while not found and tries > 0:
            try:
                elem = driver.find_element_by_class_name ('selected').find_element_by_class_name ('defaultLink').get_attribute ('href')
                driver.quit()
                display.stop()
                q.put((self._name, elem))
                found = True
            except Exception as e:
                time.sleep (1)
                tries = tries - 1
                if tries == 0:
                    driver.quit()
                    display.stop()
                    raise Exception ('  -> Serie not found in SeriesPordede')

    def getLinkInfo (self, chapterLink, cookies, q):
        childs = chapterLink.get_childs()[0].get_childs()
        host = str(childs[0].get_childs()[0].attrs['src'][0].split ('_')[1].split('.')[0])

        _parser = Parser ()

        try:
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

                r = requests.get (url, cookies = cookies)
                data = _parser.feed (r.text)
                url = data.get_by (clazz = 'episodeText')[0].attrs['href'][0]

                r =  requests.get (self._URL[:-1] + url, cookies = cookies)
                l.setURL (r.url)

                q.put((self._name, l))
        except Exception as e:
            pass

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):
        #print '  -> Searching in ' + str (self._name) + '...'

        r = requests.post (self._URL + 'site/login',  \
            headers = {'Accept' : '*/*', \
                     'Accept-Encoding' : 'gzip, deflate', \
                     'Connection' : 'keep-alive', \
                     'Content-Length' : '104', \
                     'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8', \
                     'Host' : 'www.pordede.com', \
                     'Referer' : 'http://www.pordede.com/', \
                     'User-Agent' : 'Mozilla/5.0' },  \
            data = {'LoginForm[username]': 'gunkyProject', \
                     'LoginForm[password]': '123456', \
                     'popup' : '1', \
                     'sesscheck' : 'ne09kk9c0ua7mgdjmcn6qs9fq1'})

        cookies = r.cookies
        r = requests.get (serieUrl, cookies = cookies)

        _parser = Parser ()
        data = _parser.feed (r.text)

        seasons = data.get_by (clazz = 'episodes')

        linkToChapter = ''
        for s in seasons:
            if 'episodes-' + str(seasonNumber) in s.attrs['id'][0]:
                chapters = s.get_by (clazz = 'info')
                for c in chapters:
                    for n in c.get_by (clazz = 'number'):
                        if n.attrs['data'][0] in str(chapterNumber):
                            linkToChapter = self._URL[:-1] + c.get_childs()[0].attrs['href'][0]


        r = requests.get (linkToChapter, cookies = cookies)

        data = _parser.feed (r.text.encode('utf-8'))

        onlineLinks = data.get_by (clazz = 'linksPopup')[0].get_childs()[4]
        chapterLinks = onlineLinks.get_by (clazz = 'a aporteLink done')

        i = 0

        numThreads = len (chapterLinks) // 4

        while (i < len (chapterLinks)):

            threads = []

            for j in range (0, numThreads):
                if i >= len (chapterLinks):
                    break

                threads.append (Thread (target=self.getLinkInfo, args= (chapterLinks[i], cookies, q)))
                i += 1

            for thread in threads: thread.start()
            for thread in threads: thread.join (5)

        #print '  -> Search finished in ' + str (self._name) + '...'
