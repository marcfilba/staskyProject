import cfscrape
from Parser import Parser

def test ():

    headers = {
        'Accept' : '*/*',
        'Accept-Encoding' : 'gzip, deflate',
        'Connection' : 'keep-alive',
        'Content-Length' : '104',
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host' : 'www.pordede.com',
        'Referer' : 'http://www.pordede.com/',
        'User-Agent' : 'Mozilla/5.0'
    }

    data = {
        'LoginForm[username]': 'gunkyProject',
        'LoginForm[password]': '123456',
        'popup' : '1',
        'sesscheck' : 'ne09kk9c0ua7mgdjmcn6qs9fq1'
    }

    URL = 'http://www.pordede.com/'

    scraper = cfscrape.create_scraper()
    s = scraper.post (URL + 'site/login', headers = headers, data = data)
    s = scraper.post ('http://www.pordede.com/search/autocomplete?popup=1', headers = headers, data={"query" : "daredevil"}, cookies = s.cookies)

    _parser = Parser ()
    data = _parser.feed (s.content)

    films = data.get_by (clazz = 'info')

    for f in films:
        if "Serie" in f.childs[1].attrs['data'][0]:
            #q.put((self._name, URL + f.childs[0].attrs['href'][0][1:]))
            break


def main ():
    from LinksProviderPordede import LinksProviderPordede
    from Queue import Queue

    pd = LinksProviderPordede()
    q = Queue()
    #pd.getMainPageLink ("how i met your mother", q)
    pd.getChapterUrls ('http://pordede.com/serie/how-i-met-your-mother', 1, 1, q)

    while q.qsize() > 0:
        print q.get ()


main ()
