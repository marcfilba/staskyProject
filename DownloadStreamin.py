#! /usr/bin/python

from Download import Download
from urlparse import urlparse
import requests
import time

class DownloadStreamin (Download):

    def getVideoLink (self, totalLines):
        data = {
            'host' : 'streamin.to',
            'user-agent': 'Mozilla/5.0',
            'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'accept-encoding' : 'gzip, deflate',
            'accept-language' : "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            'referer' : "http://streamin.to/m4ysy97oord3",
            'connection' :'keep-alive',
            'content-type' : 'application/x-www-form-urlencoded',
            'content-length' : '150',
            'cookie' : "__cfduid=de7551c16e2f90497c135311caf0d07881486249864; __utma=30906109.308262776.1486249865.1486249865.1486249865.1; __utmb=30906109.4.10.1486249865; __utmc=30906109; __utmz=30906109.1486249865.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __test; file_id=5780852; aff=54857; tm_imp_9cc5bc5f=3; tm_imp_9cc5bc5f_expireDate=Sun, 05 Feb 2017 23:11:16 GMT; adk2_catfish=3%7CSun,%2005%20Feb%202017%2000:11:16%20GMT; ref_url=http%3A%2F%2Fstreamin.to%2Fm4ysy97oord3; tm_imp_6af67d=1; tm_imp_6af67d_expireDate=Sun, 05 Feb 2017 23:11:42 GMT; FastPopSessionRequestNumber=1"
        }
        for line in totalLines:
            if '{file:' in line:
                return line.split ('\'')[1]


    def downloadVideo (self, link, name):
        videoLink = self.getVideoLink (link)
        self.downloadVideoFile (videoLink, name)
