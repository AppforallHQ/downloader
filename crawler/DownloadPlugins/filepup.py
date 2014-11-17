from .DownloadPlugin import DownloadPlugin
import logging,os,requests,re,json

class FilePup(DownloadPlugin):
    def __init__(self):
        super(DownloadPlugin,self).__init__()
        self.logger = logging.getLogger(__name__)
        self.username = os.environ.get("FILEPUP_USER","PROJECT")
        self.password = os.environ.get("FILEPUP_PASS","")
        self.apikey = os.environ.get("FILEPUP_API","M1RB7pwYMpSS1b3Y36qGXVKQgYmERatt")
        self.cookies = {}

    def canDownload(self,link):
        return link.find("filepup.net") != -1


    def login(self,dlmanager):
        url = "http://www.filepup.net/loginaa.php"
        try:
            r = requests.post(url,data = {
                "user" : self.username,
                "pass" : self.password,
                "task" : "dologin",
                "return" : "./members/myfiles.php"
            },allow_redirects=False)
            if r.status_code == 302:
                dlmanager.SetCookie("PHPSESSID",r.cookies['PHPSESSID'])
                self.cookies["PHPSESSID"] = r.cookies['PHPSESSID']
                return True
        except Exception as e:
            self.logger.error("Error in Login : %s" % e)
        return False

    def HandleDownload(self,link,wd,dlmanager):

        rtext_out = None
        try:
            file_id = [m.groupdict() for m in re.finditer(r"(http://)?(www\.)?filepup\.net/(files/)?(get/)?(?P<file_id>[^\./]+)(\.html)?(/)?(.*)?",link)][0]["file_id"]
            api_url = "http://www.filepup.net/api/info.php?api_key=%s&file_id=%s" % (self.apikey,file_id)
            r = requests.get(api_url)
            rtext_out=r.text
            file_name = [m.groupdict() for m in re.finditer(r"\[file_name\][\s]?=>[\s]?(?P<file_name>[^\[]+)",r.text)][0]["file_name"]
            if file_name:
                self.logger.info("FileName : %s" % file_name)
        except Exception as e:
            self.logger.error("Couldn't Download Link %s" % link)
            if rtext_out:
                self.logger.error("Filepup API Output : %s" % rtext_out)
            self.logger.error("Error : %s" % e)
            return None


        if self.login(dlmanager):
            self.logger.info("Filepup Login Successful")
        else:
            return None
        r = requests.get(link,cookies=self.cookies)
        if r.status_code != 200:
            return None
        mt = re.findall("window\\.location(\\s*)=(\\s*)\"([^\"]*)\"",r.text)
        if len(mt) < 1:
            return None
        try:
            finalurl = mt[0][2]
            dlmanager.SetLink(finalurl)
            dlmanager.PostData("task","download")
        except:
            return None
        try:
            if dlmanager.StartDownload(wd) == 0:
                return os.listdir(wd)[0]
            else:
                return None
        except:
            return None
