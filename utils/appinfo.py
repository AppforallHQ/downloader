#!/usr/bin/python

from pymongo import MongoClient
import re,httplib,sys,json,subprocess
import dateutil.parser,calendar,time

SYMBOLS = {
    'iec'           : ('', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
}

def bytes2human(n, format='%(value).2f %(symbol)s', symbols='iec'):
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)


DATADIC = {u'sdev': u'supportedDevices',
            u'prc': u'price',
            u'iscr': u'ipadScreenshotUrls',
            u'bid': u'bundleId',
            u'des': u'description',
            u'a60': u'artworkUrl60',
            u'nam': u'trackName',
            u'ven': u'artistName',
            u'cid': u'primaryGenreId',
            u'cat': u'primaryGenreName',
            u'a120': u'artworkUrl100',
            u'ver': u'version',
            u'a512': u'artworkUrl512',
            u'id': u'trackId',
            u'scr': u'screenshotUrls',
            u'advisories': u'advisories',
            u'minos' : u'minimumOsVersion',
            u'sellerName' : u'sellerName',
            u'sellerUrl' : u'sellerUrl',
            u'contentAdvisoryRating' : u'contentAdvisoryRating',
            u'averageUserRatingForCurrentVersion':u'averageUserRatingForCurrentVersion',
            u'userRatingCountForCurrentVersion':u'userRatingCountForCurrentVersion',
            u'trackContentRating':u'trackContentRating',
            u'averageUserRating':u'averageUserRating',
            u'userRatingCount':u'userRatingCount'
            }






client = MongoClient()
db = client.appdb

query = db.apps.find({},timeout=False)

class AppInfo:
    def getfilesize(self,n):
        return bytes2human(int(n))+'B'
    def __init__(self,appid="",bundleId="",version=""):
        self.version=version
        self.conn = httplib.HTTPSConnection("itunes.apple.com")
        if appid != "":
            self.param = "id="+appid
        else:
            self.param = "bundleId="+bundleId
        self.data = {}
        self._getAppInfo()
    def __getitem__(self,x):
        return self.data[x]
    #def __setitem__(self,key,value):
    #    self.data[key]=value
    def __iter__(self):
        return self.data.keys().__iter__()
    
    def _getAppInfo(self):
        self.conn.request("GET","https://itunes.apple.com/lookup?"+self.param)
        self.param = self.param[self.param.find('=')+1:]
        back = self.conn.getresponse().read()
        res = json.loads(back)
        if res[u'resultCount'] != 1:
            print "App %s Not Found" % self.param
            return {}
        for item in DATADIC:
            try:
                self.data[item] = res[u'results'][0][DATADIC[item]]
            except:
                print "On App %s, Item '%s' not found" % (self.param,item)


        #ADDITIONAL DATA
        alldata = res[u'results'][0][u'trackViewUrl']
        fnd = alldata.find("?")
        alldata = alldata[:fnd if fnd != -1 else len(alldata)]
        alldata = alldata + "?mt=8&ign-msr=https%3A%2F%2Fwww.google.com%2F"

        

        proc= subprocess.Popen(["curl","--user-agent","iTunes/12.0 (Macintosh; OS X 10.10) AppleWebKit/0600.1.25",alldata],stdout=subprocess.PIPE)
        grep = subprocess.Popen(["grep","releaseNote"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        out = grep.communicate(proc.communicate()[0])[0]
        out = out.replace('<script type="text/javascript" charset="utf-8">its.serverData=','')
        out = out.replace('</script>','')
        try:
            js = json.loads(out)
        except:
            print "Additional Data Couldn't be retrieved on %s" % self.param
            return self.data
        try:
            self.data[u'siz']=self.getfilesize(res[u'results'][0][u'fileSizeBytes'])
            self.data[u'id']=str(self.data[u'id'])
            self.data[u'req']=js[u'storePlatformData'][u'product-dv-product'][u'results'][self.data[u'id']][u'softwareInfo'][u'requirementsString']


            #VERSION AND RELEASE NOTE
            if self.version != "":
                self.data[u'ver']=self.version
            history = js[u'pageData'][u'softwarePageData'][u'versionHistory']
            flag = False
            for ver in history:
                if ver[u'versionString']==self.data[u'ver']:
                    self.data['releaseNote']=ver[u'releaseNotes']
                    date = dateutil.parser.parse(ver[u'releaseDate'])
                    stamp = calendar.timegm(date.timetuple())
                    self.data['rel'] = stamp
                    flag = True
            if not flag:
                self.data['releaseNote']=res[u'results'][0][u'releaseNotes']
                date = dateutil.parser.parse(res[u'results'][0][u'releaseDate'])
                stamp = calendar.timegm(date.timetuple())
                self.data['rel'] = stamp

            #ADDITIONAL DATA
            self.data[u'add']=long(time.time())
            self.data[u'dl']=0

            #CAN ESTIMATE IT
            self.data[u'gdl']=0


            self.data[u'cop']=[]
        except:
            print "Error in %s : %s" % (self.param,sys.exc_info()[1])
        #THIS PART IS WRITTEN LIKE Alireza's Importer

        iphone = len(self.data[u'scr'])>0
        ipad = len(self.data[u'scr'])>0
        if iphone and ipad:
            self.data[u'com']='universal'
        elif ipad:
            self.data[u'com']='ipad'
        else:
            self.data[u'com']='iphone'
        
        #MUST BE COPIED TO LOCAL DIR CREATED
        self.data[u'a160'] = js[u'storePlatformData'][u'product-dv-product'][u'results'][self.data[u'id']][u'artwork'][0][u'url']


        #BIGSCR
        self.data[u'bigscr']=[]
        self.data[u'bigiscr']=[]
        
        screens = js[u'storePlatformData'][u'product-dv-product'][u'results'][self.data[u'id']][u'screenshotsByType']

        #TRIPLE (BOOLEAN,ALLDATA KEYS, DB KEY)
        idevicedata={"iphone":(iphone,("iphone","iphone5"),u"bigscr"),
                     "ipad":(ipad,("ipad"),u"bigiscr")}

        
        for devicedata in idevicedata:
            devicedata = idevicedata[devicedata]
            if not devicedata[0]:
                continue
            key = ""
            for ky in devicedata[1]:
                if ky in screens.keys():
                    key = ky
            if key == "":
                continue
            self.data[devicedata[2]]=[]
            for item in screens[key]:
                MAX,ind = -1,0
                for i in range(len(item)):
                    if(item[i][u'height']*item[i][u'width'] > MAX):
                        MAX = item[i][u'height']*item[i][u'width']
                        ind = i
                self.data[devicedata[2]].append(item[ind][u'url'])

        return self.data

