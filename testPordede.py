from LinksSeriesAdicto import LinksSeriesAdicto
from Queue import Queue

def main ():
    pd = LinksProviderSeriesAdicto()
    q = Queue()

    pd.getMainPageLink ("how to get away with murder", q)
    pd.getChapterUrls (q.get ()[1], 1, 1, q)

    while q.qsize() > 0:
        q.get ()[1].printLink ()

main ()
