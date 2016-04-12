from .DownloadPlugin import DownloadPlugin
import logging,os,requests,re,json,time
from bs4 import BeautifulSoup as Soup

class BillionUploads(DownloadPlugin):
    def __init__(self):
        super(DownloadPlugin,self).__init__()
        self.logger = logging.getLogger(__name__)
        self.cookies = {}
        self.time = 0

    def canDownload(self,link):
        return link.find("billionuploads.com") != -1


    def login(self,dlmanager):
        return True

    def HandleDownload(self,link,wd,dlmanager):
        return None
        try:
            r = requests.get(link,headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','User-agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36"})
            print(r.text)
        except Exception as e:
            self.logger.error("Error Downloading : %s" % e)
        return None
