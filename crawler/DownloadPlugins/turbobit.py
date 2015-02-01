from .DownloadPlugin import DownloadPlugin
import logging,os,requests,re,json,time
from bs4 import BeautifulSoup as Soup
import settings

class TurboBit(DownloadPlugin):
    def __init__(self):
        super(DownloadPlugin,self).__init__()
        self.logger = logging.getLogger(__name__)
        self.username = settings.TURBOBIT_USER
        self.password = settings.TURBOBIT_PASS
        self.cookies = {}
        self.time = 0

    def canDownload(self,link):
        return link.find("turbobit.net") != -1


    def login(self,dlmanager):
        r = requests.get("http://turbobit.net/login")
        url = "http://turbobit.net/user/login"
        try:
            r = requests.post(url,data = {
                "user[login]" : self.username,
                "user[pass]" : self.password,
                "user[captcha_type]" : "",
                "user[captcha_subtype]" : "",
                "user[submit]" : "Sign in",
                "user[memory]" : "on"
            },allow_redirects=False,cookies=r.cookies)
            if r.status_code == 302:
                self.cookies["sid"] = r.cookies['sid']
                self.cookies["user_isloggedin"] = r.cookies['user_isloggedin']
                self.cookies["kohanasession"] = r.cookies['kohanasession']
                self.time = time.time()+20*3600
                return True
        except Exception as e:
            self.logger.error("Error in Login : %s" % e)
        return False

    def HandleDownload(self,link,wd,dlmanager):
        if not 'sid' in self.cookies or time.time()>=self.time:
            if not self.login(dlmanager):
                return None
        r = requests.get(link,cookies=self.cookies)
        if r.text.find(self.username) == -1:
            if not self.login(dlmanager):
                return None
        try:
            soup = Soup(r.text)
            url = soup.find("div",{"id":"premium-file-links"}).find("input").attrs["value"]
            dl = requests.head(url,allow_redirects=False,cookies=self.cookies)
            url = dl.headers["location"]
            dl = requests.head(url,allow_redirects=False,cookies=self.cookies)
            url = dl.headers["location"]

            filename = None
            try:
                filereq = requests.head(url,allow_redirects=False,cookies=self.cookies)
                hdr = filereq.headers.get("content-disposition")
                filename = re.findall(r"filename=(\")?([^\"]+)(\")?",hdr)[0][1]
                if filename[0] == '"' and filename[-1] == '"':
                    filename = filename[1:-1]
            except:
                pass
            if filename:
                dlmanager.SetParameter(["-o",filename])
            for item in dl.cookies.items():
                dlmanager.SetCookie(item[0],item[1])
            dlmanager.SetLink(url)

            if dlmanager.StartDownload(wd) == 0:
                return os.listdir(wd)[0]
            else:
                return None
        except Exception as e:
            self.logger.error("Error Downloading : %s" % e)
        return None
