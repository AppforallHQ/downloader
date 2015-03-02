from .DownloadPlugin import DownloadPlugin
import logging,os,requests,re,json
import time
import settings
import urllib

class DirectLink(DownloadPlugin):
    def __init__(self):
        super(DownloadPlugin,self).__init__()
        self.logger = logging.getLogger(__name__)
        self.user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        self.cookies = {}

    def canDownload(self,link):
        time.sleep(1)
        if link.find("filepup.net") != -1 and link.find("sp3.filepup.net") == -1:
            return False
        if link.find("turbobit.net") != -1:
            return False
        r = requests.head(link,headers={'User-Agent':self.user_agent})
        try:
            flag = (r.headers['content-type'] == "application/octet-stream")
        except:
            flag = False
        print(flag)
        time.sleep(1)
        return flag


    def login(self,dlmanager):
        return True

    def HandleDownload(self,link,wd,dlmanager):
        filename = None
        try:
            filereq = requests.head(link,allow_redirects=False,cookies=self.cookies)
            time.sleep(2)
            hdr = filereq.headers.get("content-disposition")
            filename = re.findall(r"filename=(\")?([^\"]+)(\")?",hdr)[0][1]
            if filename[0] == '"' and filename[-1] == '"':
                filename = filename[1:-1]
        except:
            pass
        if filename:
            filename = urllib.parse.unquote(filename)
            dlmanager.SetParameter(["-o",filename])
        try:
            dlmanager.SetLink(link)
            if dlmanager.StartDownload(wd) == 0:
                return os.listdir(wd)[0]
            else:
                return None
        except Exception as e:
            print(e)
            return None
