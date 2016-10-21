#! /usr/bin/python

from pyvirtualdisplay import Display
from selenium import webdriver
from Download import Download
import time

class DownloadStreamin (Download):

    def getVideoLink (self, totalLines):
        for line in totalLines:
            if '{file:' in line:
                return line.split ('\'')[1]

    def waitForLink (self, elem):
        print '  -> waiting for the page load'
        while 'disabled' in elem.get_attribute('innerHTML'):
            time.sleep(1)

    def downloadVideo (self, link, name):

        display = Display(visible=0, size=(800, 600))
        display.start()

        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)

        try:
            print '  -> going to ' + link

            driver.get(link)
            time.sleep (5)
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
