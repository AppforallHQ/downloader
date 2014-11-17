import os,json,shutil

class DownloadPlugin:
    def __init__(self):
        pass
    def canDownload(self,link):
        return False

    def rmdir(self,top):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)

    def Download(self,_id,link,data,managers,config):
        if not 'dldir' in config:
            return False
        if not os.path.exists(config['dldir']):
            self.logger.error("Path Does Not Exists")
        _id = str(_id)
        wd = os.path.join(config['dldir'],_id)
        if not os.path.exists(wd):
            os.makedirs(wd)
        else:
            self.logger.warning("%s Already Existed! Deleted To Recreate it!" % wd)
            self.rmdir(wd)
            os.makedirs(wd)
        dl = self.HandleDownload(link,wd,managers[config['downloadmanager']]())
        if dl is None:
            self.logger.error("Downloading %s Unsuccessful!" % link)
            return False
        dl += ".json"
        try:
            f = open(os.path.join(wd,dl),'w')
            f.write(json.dumps(data))
            f.close()

            shutil.move(wd,os.path.join(config['impdir'],_id))
        except Exception as e:
            self.logger.error("File Operations Failed")
            self.logger.error("Error : %s" % e)
            return False

        return True

