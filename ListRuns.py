#!/usr/bin/python

import __future__
import codecs, os, re
import cernrequests
from bs4 import BeautifulSoup

def getruns(year="all",rdirs='False'):

    baseurl='https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'
    url_runs_2018="Run2018/ZeroBias/"
    url_runs_2017="Run2017/ZeroBias/"
    url_runs_2016="Run2016/ZeroBias/"
    # url_runs_2015="Run2015/ZeroBias/"


    url_runs=[url_runs_2018,url_runs_2017,url_runs_2016]#,url_runs_2015]
    print("Fetching from: "+baseurl)
    print("list of relative urls: ",url_runs)

    global_rundir_with_rootfiles=[]
    global_runs_with_rootfiles=[]
    global_rundir_without_rootfiles=[]

    # runs_without_rootfiles=[]
    for url in url_runs:
        response=cernrequests.get(baseurl+url) # open the document
        index = response.text                  # read the document
        a=str(index)                           # convert to string
        soup = BeautifulSoup(a, 'html.parser') # create the soup object
        RUNSXXRE= soup.body.find_all(string=re.compile("000.")) # the "." for a regular expresions means that it will expect ANY character EXCEPT newlines

        rundir_with_rootfiles=[]
        runs_with_rootfiles=[]
        rundir_without_rootfiles=[]


        for rundir in RUNSXXRE:
            response=cernrequests.get(baseurl+url+rundir) # open the document
            index = response.text                  # read the document
            a=str(index)                           # convert to string
            soup = BeautifulSoup(a, 'html.parser') # create the soup object
            entries= soup.body.find_all(string=re.compile("DQM."))
            if len(entries)==0:
                rundir_without_rootfiles.append(str(rundir))        # Fill the list
                global_rundir_without_rootfiles.append(str(rundir)) # Fill the list
                #print rundir,"is empty"
            else:

                for n in re.findall(r"R(\d+)",str(entries)):    # This will only keep the 6 digits of the run numbers that we need (without the "R000")
                    x=str(int(n))                               # Since we wont want to do math with these numbers I will convert them to strings
                    runs_with_rootfiles.append(x)               # Fill the list
                    global_runs_with_rootfiles.append(x)        # Fill the list

                rundir_with_rootfiles.append(str(rundir))         # Fill the list
                global_rundir_with_rootfiles.append(str(rundir))  # Fill the list

                #print rundir,"has",len(entries),"root files"    
        print("===========================================================")
        print("For",url)
        print("Out of a total of",len(RUNSXXRE),"run directories:\n",len(rundir_with_rootfiles),"have root files\n",len(rundir_without_rootfiles),"are empty")
        print("There are",len(runs_with_rootfiles),"runs with root files")
        print("\n")
        #print "List of available runs for this year\n\n",runs_with_rootfiles

    print("===========================================================")
    print("For GLOBAL")
    print("Out of all run directories:\n",len(global_rundir_with_rootfiles),"have root files\n",len(global_rundir_without_rootfiles),"are empty")
    print("There are",len(global_runs_with_rootfiles),"runs with root files")
    print("\n")
    if rdirs=='True':
        return global_runs_with_rootfiles,global_rundir_with_rootfiles,global_rundir_without_rootfiles
    else:
        return global_runs_with_rootfiles


