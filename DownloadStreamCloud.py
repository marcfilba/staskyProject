#! /usr/bin/python

from Download import Download
from urlparse import urlparse
import requests
import time

class DownloadStreamCloud (Download):

    def getVideoLink (self, link):

        data = {
            'hash': '',
            'id': urlparse(link).path.split ('/')[1],
            'imhuman': 'Watch video now',
            'op': 'download1',
            'referer': '',
            'usr_login': ''
        }

        try:
            retry = 5
            while retry > 0:
                r = requests.get (link)
                time.sleep (10)
                r = requests.post (link, data = data)

                for line in r.content.encode('ascii','replace').split ('\n'):
                    if 'file:' in line:
                        return line.split ('"') [1]
                retry = retry - 1
                time.sleep (1)

        except: pass

    def downloadVideo (self, link, name):
        videoLink = self.getVideoLink (link)
        self.downloadVideoFile (videoLink, name)
