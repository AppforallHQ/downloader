Downloader
----------------
Get download request from a mongo collection and download url's from one of supported download types:

- direct link
- filepup 
- fileshack
- turbobit

Start a downloader listener to regularly check mongo collection and download provided links:

    $ python downloader.py --startdownloader

Or start downloader for a single link to download:

    $ python downloader.py --download SomeLink JsonData
