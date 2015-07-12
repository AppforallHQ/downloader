from .DownloadPlugin import DownloadPlugin
import logging, os, requests
from bs4 import BeautifulSoup as Soup
import settings

class TurboBit(DownloadPlugin):
    def __init__(self):
        super(DownloadPlugin,self).__init__()
        self.logger = logging.getLogger(__name__)
        self.cookies = {}
        self.time = 0

    def canDownload(self,link):
        return link.find("fileshack.net") != -1

    def HandleDownload(self,link,wd,dlmanager):
        try:
            download_id = link.split("/")[-1]
            post_params = "op=download2&id="+download_id
            filename = None
            try:
                req = requests.get(link, cookies=self.cookies)
                soup = Soup(req.text)
                filename = soup.find("span", {"class": "dfilename"}).text
            except Exception as err:
                self.logger.error("Error fetching file name : %s" % err)
                pass
            if filename:
                dlmanager.SetParameter(["-o", filename])
            if post_params:
                dlmanager.SetParameter(["--post-data", post_params])
            for item in req.cookies.items():
                dlmanager.SetCookie(item[0],item[1])
            dlmanager.SetLink(link)

            if dlmanager.StartDownload(wd) == 0:
                return os.listdir(wd)[0]
            else:
                return None
        except Exception as e:
            self.logger.error("Error Downloading : %s" % e)
        return None
