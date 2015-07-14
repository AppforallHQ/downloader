from .DownloadManager import DownloadManager
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, path, remove
import logging,re



class Axel(DownloadManager):
    def __init__(self):
        super(DownloadManager,self).__init__()
        self.procparam = ["axel++"]
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
        
    def SetSpeedLimit(self,speed):
        self.SetParameter(['-s', str(speed)])    
    

    def StartDownload(self,wd):
        cookies = ""
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
            self.SetParameter(["-c",cookies])
        if len(postdata)>0:
            self.SetParameter(["-p",postdata])
        #self.SetParameter(["-n","14"])
        self.procparam.append(self.link)
        print(self.procparam)
        p = Popen(self.procparam,stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False,cwd= wd)
        flags = fcntl(p.stdout, F_GETFL)
        fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)
        sleep(0.1)
        outp,lastdl = "",""

        axelLogger = open(path.join(wd,"Download.log"),"w")
        self.logger.info("Download Started!")
        while True:
            try:
                data = read(p.stdout.fileno(), 4096).decode("utf-8")
                axelLogger.write(data)
                axelLogger.flush()
                outp += data
                lst = re.findall("(\\d+\\%)",outp)
                if len(lst) > 0 and lst[-1]!=lastdl:
                    self.logger.info("Downloaded %s" % lst[-1])
                    lastdl=lst[-1]
            except OSError:
                sleep(.1)
            if p.poll() is not None and p.poll() != -1:
                self.logger.info("Axel++ Exited With Code %s" % p.poll())
                break
        axelLogger.close()
        outp += p.communicate()[0].decode("utf-8")
        lst = re.findall("(\\d+\\%)",outp)
        if len(lst) > 0 and lst[-1]!=lastdl:
            self.logger.info("Downloaded %s" % lst[-1])
        if outp.find("Downloaded") != -1:
            remove(path.join(wd,"Download.log"))
            self.logger.info("Download Finished Successfully")
            return 0
        else:
            self.logger.error("Error Download File %s" % self.link)
            self.logger.warning("Axel Output: %s" % outp)
            return p.poll()

