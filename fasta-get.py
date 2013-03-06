#! /usr/bin/python

##	fasta-get.py
##	for obtaining FASTA protein sequence files from the NCBI RefSeq complete database, located at ftp://ftp.ncbi.nlm.nih.gov/refseq/release/complete/
##	1) downloads FASTA.faa.gz files
##	2) extracts .gz files
##	3) concatenates all files into one large file and removes .gz files
##	Sandip Chatterjee

import gzip
from ftplib import FTP
import os
import time

startTime = time.time()

print "Accessing NCBI RefSeq/complete at ftp://ftp.ncbi.nlm.nih.gov/refseq/release/complete/"
#directoryLineList = urllib2.urlopen('ftp://ftp.ncbi.nlm.nih.gov/refseq/release/complete/').read().splitlines()

ftp = FTP('ftp.ncbi.nlm.nih.gov')
ftp.login()

ftp.cwd('refseq/release/complete/')
dirListing = []
ftp.retrlines("LIST",dirListing.append)		##	retrieve directory

##	generate python list of file info for each file
fileLines = []
for line in dirListing:
	fileLines.append(line.split(None, 8))

fileNameList = []
for fileLine in fileLines:
	fileNameList.append(fileLine[-1])

##	filter and keep only filenames that have 'protein.faa.gz'
fileNameList = filter(lambda x: 'protein.faa.gz' in x,fileNameList)

newFileName = time.strftime("%m%d%y_%H%M%S")+'_refseq_complete.fasta'
extractedFile = open(newFileName, 'ab')

fileCount = 0
for fileName in fileNameList:
	ftp.retrbinary('RETR '+fileName, open(fileName, 'wb').write)
	gzipFile = gzip.open(fileName, 'rb')
	extractedFile.write(gzipFile.read())
	gzipFile.close()
	os.remove(fileName)
	fileCount += 1

extractedFile.close()

print "Downloaded, extracted, and concatenated "+str(fileCount)+" files in "+str((time.time()-startTime)/60)+" minutes"
print "Saved compiled data to "+newFileName
print "(DATE_CURRENTTIME_refseq_complete.fasta)"

ftp.quit()