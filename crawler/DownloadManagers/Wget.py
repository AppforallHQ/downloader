from .DownloadManager import DownloadManager
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, path, remove
import logging,re


class Wget(DownloadManager):
    def __init__(self):
        super(DownloadManager,self).__init__()
        self.procparam = ["wget"]
        self.cookies={}
        self.postdata={}
        self.link = ""
        self.logger = logging.getLogger(__name__)

    def SetParameter(self,lst):
        for param in lst:
            self.procparam.append(param)

    def SetCookie(self,key,value):
        self.cookies[key] = value

    def PostData(self,key,value):
        self.postdata[key]=value

    def SetLink(self,link):
        self.link = link

    def StartDownload(self,wd):
        cookies = "Cookie: "
        postdata = ""
        for cookie in self.cookies:
            cookies += cookie+"="+self.cookies[cookie]+"&"
        if len(cookies) > 0:
            cookies=cookies[:-1]
        for pd in self.postdata:
            postdata += pd+"="+self.postdata[pd]+"&"
        if len(postdata) > 0:
            postdata=postdata[:-1]

        if len(cookies)>0:
            self.SetParameter(["--no-cookies --header",cookies])
        if len(postdata)>0:
            self.SetParameter(["--post-data",postdata])
        self.procparam.append(self.link)
        print(self.procparam)
