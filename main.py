#!/usr/bin/python

from ListRuns import *
import sys
outpath= input('Where would you like to dump output?\n Enter "." for current directory or enter "<a/path/to/directory/>" relative to current directory\n')

print("Path : "+str(outpath))

choice=input('Is this  correct? \n a) Y\n b) N\n')


if choice == "Y" or choice == "y" or choice == "a":
	print("Output will be dumped in",str(outpath))
elif choice == "N" or choice == "n" or choice == "b":
	print("Please try again")
	sys.exit(0)

choice=input('Specify where whould you like to look :\n a) afs\n b) eos\n c)RunRegistry\n')

if choice == "a" or choice == "afs" or choice == "b" or choice == "eos" or choice == "c" or choice == "RunRegistry":
        print("Will look for runs in",choice)
else:
        print("Please try entering one of the options")
        sys.exit(0)


#### For eos
#### Update eos runs
if  choice == "b" or choice == "eos":
    command1 = "wc -l ZeroBias_runs.txt | cut -d' ' -f1"
    command2="ls -R /eos/cms/store/group/comm_dqm/DQMGUI_data/ | grep 'ZeroBias' | wc -l | cut -d' ' -f1"
    file1=subprocess.call(command1,shell=True)
    file2=subprocess.call(command2,shell=True)
    print('If the numbers are both equal then you have the most updated version of the list')
    arequal=input("Are the numbers above equal? y or n \n")
    if arequal=='n':
        print('Updating the text file with list of runs')
        getruntype_eos()
        print('checking if all went well "checkiter should be empty"\n')
        list_runs,checkiter=getlist(file="ZeroBias_runs.txt")
        print('Checkiter is',checkiter)
    elif arequal=='y': 
        print('You have the most updated list of runs\n Check for a new file in your specified path')
        list_runs,checkiter=getlist(file="ZeroBias_runs.txt")
    
    subprocess.call('mkdir -pv '+outpath,shell=True)
    f= open(outpath+'/AvailableRuns.txt',"w")
    f.write("%s" % list_runs)
    f.close()
    
    

### For afs

if choice == "a" or choice == "afs":
    print("Searching in afs....")
    getruns_afs()
    
    
elif choice == "c" or choice == "RunRegistry":
    getRR()
    
