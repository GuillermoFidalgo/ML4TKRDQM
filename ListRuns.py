#!/usr/bin/python

import __future__
import codecs, os, re, subprocess,shlex,numpy
import cernrequests,runregistry
from bs4 import BeautifulSoup

def getlist(file="ZeroBias_runs.txt"):
    f=open(file).read()
    runs= re.findall("000(\d{6})",str(f)) #get all 6 digit numbers followed by 000
    intruns=[int(num) for num in runs] # make the list full of intergers
    intruns.sort()  #have an ascending sorted list of runs 
    if len(intruns)==0: # Check if list is empty
        print("no runs found")
    else:
        print("Found some runs")
    intruns=list(dict.fromkeys(intruns))  #make a list into a dict and the back into a list. This eliminates any duplicate runs

    i=0
    checkiter=[]
    for x in intruns:    # Check if all runs are sorted from oldest to newest
        if x==intruns[-1]:
            break
        elif x > intruns[i+1]:
            print("iteration",i,"is greater the the next iteration")
            checkiter.append(i)
        i=i+1
    repeat=getrepeatedruns(intruns)


    if len(checkiter)!=0:
       print("Check the entries number "+checkiter+" of this list")
       return intruns,checkiter
    else:
        return intruns,checkiter



def getruntype_eos(runtype="ZeroBias"):
    command="ls -R /eos/cms/store/group/comm_dqm/DQMGUI_data/ | grep "+runtype+" > "+runtype+"_runs.txt"
    file=subprocess.call(command,shell=True)



def getRR(first=272000,last=326000,tkr_IN=True,tkr_strip_ON=True,tkr_pix_ON=True,collisions=True):
    runs = runregistry.get_runs(filter={
        'run_number': { 'and': [{'>': first}, {'<': last}]},
        'tracker_included': tkr_IN,
        'tracker-strip': tkr_strip_ON,
        'tracker-pixel': tkr_pix_ON
        })
    if collisions== True:
        coltype=[]
        for i in range(len(runs)):
            coltype.append(re.findall(r'collision*',str(runs[i])))
        print(coltype)
        
    return runs




def getrepeatedruns(global_runs_with_rootfiles):
    i=0
    repeatruns=[]
    for run in global_runs_with_rootfiles: 
        if run == global_runs_with_rootfiles[-1]:
    #         print "Last run",run
            break
        if run==global_runs_with_rootfiles[i+1]:
            #print "repeated run:",run
            repeatruns.append(run)
        i+=1
    print('there are',len(repeatruns),'repeated runs')
    return repeatruns




def compare_with_Gjsn(global_runs_with_rootfiles):
    baseurl='https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/'
    json_runs_2018="Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt"
    json_runs_2017="Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt"
    json_runs_2016="Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt"


    json_runs=[json_runs_2018,json_runs_2017,json_runs_2016]#,url_runs_2015]
    print('\n',"Fetching from: "+baseurl)
    print('\n',"list of relative urls: ",json_runs)
    
    
    json_runslist=[]
    for url in json_runs:
        response=cernrequests.get(baseurl+url) # open the document
        index = response.text                  # read the document
        a=str(index)                           # convert to string
        soup = BeautifulSoup(a, 'html.parser') # create the soup object

        a=re.findall(r"(\d{6})",str(soup))     #find exactly 6 occurrences of a number
                                               #in other words find 6 digit numbers

        print('\n',"amount of runs in the json",len(a),"in",url)
        print('\n',"From",a[0],"to",a[-1])
        json_runslist.append(a)
    json_list = [item for sublist in json_runslist for item in sublist]

    good=[]
    missing=[]
    bad=[]
    for jrun in json_list:
        for grun in global_runs_with_rootfiles:
            if jrun==grun:
                good.append(jrun)            
        if jrun not in global_runs_with_rootfiles:
            missing.append(jrun)

    for grun in global_runs_with_rootfiles:
        if grun not in json_list:
            bad.append(grun)
    # print "all good runs found",good,"\n"
    print( '\n',len(good),"good runs")
    print( '\n',len(missing),"missing runs")
    print( '\n',len(bad),"bad runs")
    return json_list,good,missing,bad






def getruns_afs(year="all",rdirs='False'):

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


