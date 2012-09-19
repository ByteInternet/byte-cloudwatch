#!/usr/bin/python
import re
import os
import sys
import pprint
import commands
import optparse
import logging
import metrics
import time 

def main():

	(options,args) = optionParser()
	timeout = 3

 	### Apache Metrics
	apachemetrics = metrics.apacheMetrics()

	metvals = apachemetrics.status()

	# Try to restart Apache if metrics show that apache is down (exitcode != 0)
	for n in range(0,int(options.retry)):
		if metvals["status"] == 0:
			break
		else:
			os.system("/usr/sbin/service apache2 start")
			metvals = apachemetrics.status()
			time.sleep(timeout)		

	if (metvals["status"] == 3): 
		os.system("/sbin/shutdown -h now")

	sys.exit(0)

def optionParser():
	parser = optparse.OptionParser()
	parser.add_option("-r","--retry"   ,dest="retry", action="store", default=1, help="Number of Apache retries before submit")

	return parser.parse_args()	


if __name__ == "__main__":
	main()
