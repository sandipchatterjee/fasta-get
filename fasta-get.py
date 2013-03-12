#! /usr/bin/python

##	fasta-get.py
##	Sandip Chatterjee
##
##	Usage:
##		for new download:
##		>>python fasta-get.py
##		
##		for resuming directory download (from previous run):
##		>>python fasta-get.py [FILENAME].log
##
##	for obtaining FASTA protein sequence files from the NCBI RefSeq complete database, located at ftp://ftp.ncbi.nlm.nih.gov/refseq/release/complete/
##	1) downloads FASTA.faa.gz files
##	2) extracts .gz files
##	3) concatenates all files into one large file and removes .gz files (order of files concatenated is not necessarily maintained)

import gzip
from ftplib import FTP
import os
import time
import sys
import shutil

startTime = time.time()

if len(sys.argv) == 1:
	resumeFlag = False
elif len(sys.argv) == 2:
	resumeFlag = True
	if ".log" not in sys.argv[1]:
		print 'Proper usage: >>fasta-get.py *.log ## resume from last downloaded file in this log file'
		sys.exit()
else:
	print "Wrong number of arguments"
	print 'Proper usage: >>fasta-get.py ## run without resuming'
	print 'Proper usage: >>fasta-get.py *.log ## resume from last downloaded file in this log file'
	sys.exit()

print "Accessing NCBI RefSeq/complete at ftp://ftp.ncbi.nlm.nih.gov/refseq/release/complete/"

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
extractedFile = open(newFileName, 'a')

##	if resuming from input log file...
if resumeFlag:

	##	read in file names from given file log
	logfileNameList = []
	fileLog = open(sys.argv[1], 'rb')
	for line in fileLog:
		logfileNameList.append(line.split()[0])
	logfileNameList = filter(lambda x: '.protein.faa.gz' in x,logfileNameList)	##	only keep lines that contain valid filenames of interest...
	fileLog.close()

	##	concatenate old fasta file and new (empty) fasta file	
	oldFastaFile = open(sys.argv[1].strip('.log'),'rb')
	shutil.copyfileobj(oldFastaFile,extractedFile)	
	oldFastaFile.close()

	##	update log file
	fileLog = open(sys.argv[1], 'rb')
	extractedFileLog = open(newFileName+'.log', 'wb')
	shutil.copyfileobj(fileLog,extractedFileLog)
	extractedFileLog.close()
	fileLog.close()

	##	remove previously downloaded filenames from new filename (removes order from list due to set operations)
	fileNameList = list(set(fileNameList)-set(logfileNameList))

fileCount = 0
for fileName in fileNameList:
	
	tempFile = open(fileName, 'wb')
	ftp.retrbinary('RETR '+fileName, tempFile.write)
	tempFile.close()

	gzipFile = gzip.open(fileName, 'rb')
	extractedFile.write(gzipFile.read())
	gzipFile.close()

	os.remove(fileName)

	fileCount += 1
	extractedFileLog = open(newFileName+'.log', 'a')
	extractedFileLog.write(fileName+" - Item #"+str(fileCount)+' of '+str(len(fileNameList))+' downloaded, extracted, and appended to master file'+'\n')	
	extractedFileLog.close()

endStatus = "Downloaded, extracted, and concatenated "+str(fileCount)+" files in "+str((time.time()-startTime)/60)+" minutes"

extractedFile.close()

extractedFileLog = open(newFileName+'.log', 'a')
extractedFileLog.write(endStatus)
extractedFileLog.write("(DATE_CURRENTTIME_refseq_complete.fasta)")
extractedFileLog.close()

print endStatus
print "Saved compiled data to "+newFileName
print "(DATE_CURRENTTIME_refseq_complete.fasta)"

ftp.quit()