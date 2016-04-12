MONGO_URI = "mongodb://localhost/requests"
APPDB_URI = "mongodb://localhost/filedb"
DOWNLOAD_DIRECTORY = "./tmp/"
IMPORTER_DIRECTORY = "../tempapps/"
FILEPUP_USER = ""
FILEPUP_PASS = ""
FILEPUP_API = ""
DOWNLOAD_MANAGER = "Wget"
LOGSTASH_GELF_HOST = ""
LOGSTASH_GELF_PORT = ""
TURBOBIT_USER = ''
TURBOBIT_PASS = ""

try:
	from local_settings import *
except:
	pass
