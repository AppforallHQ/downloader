# Downloader

A download manager that is able to download from several paid upload services
and can get download requests manually or from other apps (like crawlers) over
Mongo interface.

## Features

- Direct download request from commandline
- Automatic download request from other apps using Mongo interface
- Support multiple upload services in paid versin ([filepup](http://filepup.net), [fileshack](http://fileshack.net), [turbobit](http://turbobit.com/))
- Report download status using [Segment](http://segment.com)

## Getting Started

### Prerequisities

Downloader needs [MongoDB](http://mongodb.org), [Python 2.x](http://python.org) and it's package manager
**pip** to get started. In a development environment, it'll be a good idea to
use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org), so consider it as an optional requirement.

```
# apt-get install mongodb
# apt-get install python-pip
# pip install virtualenvwrapper
```

### Installing

After taking care of prerequisities, you can clone the git repo or download a
stable version from [released versions](https://github.com/FoundersBuddy/downloader/releases), 
and install node dependencies.

```bash
$ git clone https://github.com/FoundersBuddy/downloader.git
$ cd downloader
$ mkvirtualenv --python=/usr/bin/python2.7 downloader
$ pip install -r requirements.txt
```

### Usage

#### Configuration 

The authentication data for upload services and [Segment](http://segment.com)
can be configured in `settings.py` file.

#### Run services

You can start an automatic download service which listens to Mongo collection
for download requests like this:

    $ python downloader.py --startdownloader

Or start downloader for a single link to download:

    $ python downloader.py --download SomeLink JsonData

The `JsonData` can be an empty JSON object. (description follows)

### Requests

Each download request should be registred as a document in the mongo collection
with following description:

```
{
  'links': link,           # The actual link
  'canDownload': 1,        # indicates that the link is downloadable or not
  'data': {},              # Any optional data which can be used later
  'report': True,          # Report the download to the user or not (Segment configuration is required)
}
```

## Contributing

- Check for open issues or start a new one about your idea/problem. Please make sure descriptive data on the topic to help others to understand it.
- Fork the repository and create a new branch from the master branch, and apply your changes.
- Write a test which shows that your new implementation is fully operational.
- Send a pull request.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/FoundersBuddy/downloader/releases). 

## Authors

See the list of [contributors](https://github.com/FoundersBuddy/downloader/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
