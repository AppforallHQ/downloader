import analytics
import logging,time,subprocess
from bson.objectid import ObjectId
from os import listdir,environ,makedirs,path
import sys,time
from pymongo import Connection

analytics.write_key = ''

analytics.identify('downloader', traits={
	'email': '+downloader@PROJECT..com',
})

class Downloader:
    def __init__(self,db=None):
        self.db = db
        logging.basicConfig(filename=("log/downloader-%s.log" % int(time.time())),level=logging.INFO)
        self.logger = logging.getLogger(__name__)


        ########DOWNLOAD MANAGERS
        modo = [name.split(".py")[0] for name in listdir("DownloadManagers") if name.endswith(".py")]
        modules = {}
        for modu in modo:
            modu = "DownloadManagers."+modu
            modules[modu] = __import__(modu)
        baseclass = modules["DownloadManagers.DownloadManager"].DownloadManager.DownloadManager
        self.managers = {}
        for cls in baseclass.__subclasses__():
            self.managers[cls.__name__] = cls


        #########DOWNLOAD PLUGINS
        modo = [name.split(".py")[0] for name in listdir("DownloadPlugins") if name.endswith(".py")]
        modules = {}
        for modu in modo:
            modu = "DownloadPlugins."+modu
            modules[modu] = __import__(modu)
        baseclass = modules["DownloadPlugins.DownloadPlugin"].DownloadPlugin.DownloadPlugin
        self.downloaders = {}
        for cls in baseclass.__subclasses__():
            self.downloaders[cls.__name__] = cls()

        self.config = {
            'dldir' : environ.get("DOWNLOAD_DIRECTORY","./tmp/"),
            'impdir' : environ.get("IMPORTER_DIRECTORY","./apprepo/"),
            'downloadmanager' : environ.get("DOWNLOAD_MANAGER","Axel")
        }
        if not path.exists(path.abspath(self.config['dldir'])):
            makedirs(path.abspath(self.config['dldir']))
            self.logger.info("Download Directory Created!")

    def downloadItem(self,item):
        flag = False
        for link in item['links']:
            self.logger.info("Trying To Download %s..." % link[0])
            for plugin in self.downloaders:
                if not flag and self.downloaders[plugin].canDownload(link[0]):
                    if not link[1]:
                        self.logger.warning("Going To Download Unverified Link %s" % link[0])
                    from urllib import parse
                    final = link[0]
                    if not parse.urlparse(link[0]).scheme:
                        final = "http://"+final
                    try:
                        flag = flag or self.downloaders[plugin].Download(item['_id'],final,data = item['data'],managers=self.managers,config =self.config)
                    except Exception as ex:
                        self.logger.error("Error Occurred Downloading %s : %s" % (final,ex))
        return flag

    def downloadOne(self):
        item = self.db.download.find_one({"canDownload":1})
        if not item:
            self.logger.info("No Download Request.. Sleeping For Two Minutes")
            time.sleep(120)
            return

        flag = self.downloadItem(item)
        if not flag:
            self.logger.warning("Couldn't Download App with DB ID %s" % item['applinkid'])
            self.db.download.update({"_id":ObjectId(item['_id'])},{"$set":{"canDownload":0}})
        else:
            self.logger.info("Download Successful. Removing %s From Download Queue" % item['_id'])
            self.db.download.remove({"_id":ObjectId(item['_id'])})

    def getDriveStatistics(self,dir):
        df = subprocess.Popen(["df", dir], stdout=subprocess.PIPE)
        output = df.communicate()[0].decode("utf-8")
        self.logger.info("Drive Details: "+output.split("\n")[1])
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        return available


    def start(self):
        self.logger.info("Downloader Thread Started")

        while True:
            availableDiskSpace = self.getDriveStatistics(self.config['dldir'])
            if int(availableDiskSpace) < 10*1000*1000:
                self.logger.error("Insufficient Disk Space %s GB!" % (availableDiskSpace/1024./1024))
                #Send Analytics Mail
                return
            self.downloadOne()

def send_download_status(app, status, extra=None):
	analytics.track('downloader', 'download_status', {
		'title': app,
		'message': status,
		'extra': extra,
	})

if __name__ == "__main__" and "--restart" in sys.argv:
    conn = Connection(environ.get("MONGO_URI", "mongodb://localhost/requests"))
    db = conn.requests
    db.download.update({},{"canDownload":1})

if __name__ == "__main__" and "--download" in sys.argv:
    try:
        link = sys.argv[sys.argv.index("--download")+1]
        data = sys.argv[sys.argv.index("--download")+2]
        downloader = Downloader().downloadItem({
            "_id" : str(ObjectId()),
            "links" : [(link,True)],
            "data" : data
        })
        
        send_download_status(link, downloader)
        analytics.flush()

    except Exception as e:
        print("Invalid Data : %s" % e)
        print("Usage : downloader --download link jsondata")

if __name__ == "__main__" and "--startdownloader" in sys.argv:
    conn = Connection(environ.get("MONGO_URI", "mongodb://localhost/requests"))
    db = conn.requests
    Downloader(db=db).start()
