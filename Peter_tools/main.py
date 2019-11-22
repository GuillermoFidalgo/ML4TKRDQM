#!/usr/bin/python

from test import *
import sys
outpath= input('Where would you like to dump output?\n Enter "." for current directory \n Enter "<a/path/to/directory/>" relative to current directory\n')
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
        print("Please try again")
        sys.exit(0)


#### For eos
#### Update eos runs
command = "diff ZeroBias_runs.txt ../ZeroBias_runs.txt"
file=subprocess.call(command,shell=True)

print(file)

#if command == 1:
#	getruntype_eos()
