#! /usr/bin/python

from pyvirtualdisplay import Display
from selenium import webdriver
from Download import Download
import time

class DownloadStreamPlay (Download):

    def getVideoLink (self, totalLines):
        for line in totalLines:
            if 'eval(function(' in line:

                splitted = line.split('|')

                ip = splitted[29] + '.' + splitted[28] + '.' + splitted[27] + '.' + splitted[26]
                hash = splitted[48]
                format = splitted[47]

                return 'http://' + ip + '/' + hash + '/v.' + format

    def waitForLink (self, elem):
        print '  -> waiting for the page load'
        while elem.get_attribute('disabled') == 'true':
            time.sleep(1)

    def downloadVideo (self, link, name):

        display = Display(visible=0, size=(800, 600))
        display.start()

        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)

        try:
            print '  -> going to ' + link

            driver.get(link)
            elem = driver.find_element_by_id ('btn_download')

            self.waitForLink (elem)
            elem.submit ()

            videoLink = self.getVideoLink (driver.page_source.split ('\n'))
            self.downloadVideoFile (videoLink, name)

        except Exception as e:
            raise Exception (str(e))

        finally:
            driver.quit()
            display.stop ()
