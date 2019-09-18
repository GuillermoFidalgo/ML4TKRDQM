# ML4TRKDQM

## Prerequisites

This script was tested using ```Python``` version ```3.6```. 
Although other versions might work too, this is the only one tested.

Test your python version by running

```bash
python --version
```

```
Python 3.6.8
```

### Virtual environment

*Side Note* **If you clone from this repo please remove `venv/` and all of its contents *before creating a virtual enviroment***

I highly recommend setting up a virtual environment to not get conflicts between different versions of packages.

You can create a virtual python virtual environment with:

```bash
python3 -m venv venv
```

Then you need to *activate* the virtual environment

```bash
. venv/bin/activate
```

You should now see a ```(venv) ``` in front of you terminal line.

```
(venv) [yourname@yourmachine ML4TKRDQM]$
```


### Installing packages

All tools necessary for data retrieval and data analysis are installable via ```pip```

*pip* comes bundled in Python 3.6 so, you should already have it installed.

These commands install all the tools necessary for this notebook:

```bash
pip install git+https://github.com/CMSTrackerDPG/cernrequests
pip install git+https://github.com/CMSTrackerDPG/runregcrawlr
pip install git+https://github.com/CMSTrackerDPG/dqmcrawlr
pip install git+https://github.com/CMSTrackerDPG/wbmcrawlr
pip install git+https://github.com/CMSTrackerDPG/cms-tracker-studies
pip install runregistry
pip install numpy
pip install matplotlib
pip install pandas
pip install seaborn
pip install scipy
pip install scikit-learn
```

*Side Note*: ```cernrequests``` is also available in pypi, so you could also install it via:

```bash
pip install cernrequests
```

This would install the current stable version of the package, 
while the github link always installs the latest version inside the master branch of the repository.
In order to update the pypi package, a maintainer is necessary which will leave in April 2019.


## Authentication Setup

A lot of resources at CERN are only accessible with proper authentication. 
Some only require you to be within the CERN GPN, some require you to just authenticate with your Grid User Certificate, while others require cookies.
In general should [request a grid user certificate](https://ca.cern.ch/ca/), if you dont already have.
After that, you should have downloaded a file called ```myCertificate.p12```
Now this file needs to be converted into *public* and *private* key. You can do that using ```openssl```.
The tools for this notebook, assume that your public and private key are inside the ```private``` folder.
If you do not like this behavior you can change the path by exporting the ```CERN_CERTIFICATE_PATH``` environment variable as described [here](https://github.com/CMSTrackerDPG/cernrequests#configuration).

In general you can do the just described steps with:

```bash
mkdir -p ~/private
openssl pkcs12 -clcerts -nokeys -in myCertificate.p12 -out ~/private/usercert.pem
openssl pkcs12 -nocerts -in myCertificate.p12 -out ~/private/userkey.tmp.pem
openssl rsa -in ~/private/userkey.tmp.pem -out ~/private/userkey.pem
```

These commands should ask you for the user certificate password. 
In the simplest case, just enter them twice.

*Note*: Your private key ```userkey.pem``` and public key ```usercert.pem``` have to be **passwordless** for the tools to work.
