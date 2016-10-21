
class LinksProvider(object):

    def __init__ (self, name, url=None):
        self._URL = url
        self._name = name

    def getMainPageLink (self, serieName, q):
        raise NotImplementedError()

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):
        raise NotImplementedError()
