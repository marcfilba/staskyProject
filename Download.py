#! /usr/bin/python

from sys import stdout
import requests

class Download ():

    def downloadVideoFile (self, videoLink, name):
        r = requests.get (videoLink, stream = True)
        totalLength = float (r.headers.get ('content-length'))

        if totalLength < 1024000:
            raise Exception ('  -> video with not enough length! ' + str( format (totalLength/1024, '.2f')) + ' KB')

        #stdout.write ('  -> downloading "' + name.split ('/') [len (name.split ('/'))-1] + '" (' + str( format (totalLength / 1024 / 1024, '.2f')) + ' MB) [')
        #stdout.flush ()
        #print 'downloading ' + name.split ('/') [len (name.split ('/'))-1].split ('.')[0]

        downloaded = float (0)
        progress = 1
        if r.status_code == 200:
            with open (name, 'wb') as f:
                for chunk in r:
                    f.write (chunk)
                    downloaded += len (chunk)

                    #if float (downloaded/totalLength)*10 > progress:
                        #progress += 1
                        #stdout.write ('#')
                        #stdout.flush ()

            #stdout.write (']\n')
            #stdout.flush ()

            if downloaded != totalLength:
                print 'error downloading ' + name.split ('/') [len (name.split ('/'))-1]
                raise Exception ('  -> error downloading ' + name)

            #print name.split ('/') [len (name.split ('/'))-1] + '" downloaded successfull'
        else:
            #stdout.write (']\n')
            #stdout.flush ()
            #print '  -> error downloading ' + name
            raise Exception ('  -> error downloading ' + name)

    def checkVideoLink (self, videoLink, name):
    	r = requests.get (videoLink, stream = True)
    	totalLength = float (r.headers.get ('content-length'))

    	if totalLength >= 1024000:
    		return True

    	return False
