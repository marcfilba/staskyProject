
import requests

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

r = requests.post (URL + 'site/login', headers = headers, data = data)
r1 = requests.post ('http://www.pordede.com/search/autocomplete?popup=1', headers = headers, data={"query" : "av"}, cookies = r.cookies)
print r1.text
