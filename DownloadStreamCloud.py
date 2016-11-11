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

        r = requests.post (link, data = data)

        for line in r.iter_lines():
            if '.mp4' in line:
                return line.split ('"') [1]


    def downloadVideo (self, link, name):
        videoLink = self.getVideoLink (link)
        self.downloadVideoFile (videoLink, name)
