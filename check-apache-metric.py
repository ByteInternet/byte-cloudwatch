#!/usr/bin/python
import re
import sys
import pprint
import commands
import optparse
import logging
import boto, boto.ec2, boto.ec2.cloudwatch
import metrics
import time 

pp             = pprint.PrettyPrinter(indent=4)
thisInstanceId = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id")
thisRegion     = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/placement/availability-zone")
namespace      = "Byte/System"

def main():

	(options,args) = optionParser()
	conn = boto.ec2.cloudwatch.connect_to_region(thisRegion[:-1])
	timeout = 3

 	### Apache Metrics
	metricname  = "Apache"
	unitname = "Count"		
	apachemetrics = metrics.apacheMetrics()

	if options.verbose:
		print "I am inctance: "+ thisInstanceId
		print "Gathering Apache metrics"
		print "Trying to restart %s times before submitting metrics if Apache is dead.\n" % options.retry
		

	# For disk we always want percentage used (other options: free/used bytes)
	metvals = apachemetrics.status()

	for n in range(0,int(options.retry)):
		if metvals["status"] == 0:
			break
		else:
			if options.verbose:
				print "Exitcode of 'service apache2 status' is %s" % metvals["status"]
				print "So Apache appears not to be running."
				print "Trying apache2 restart..."
				print commands.getoutput("service apache2 start")
				print "Waiting for %s seconds before continuing." % str(timeout)
			metvals = apachemetrics.status()
			time.sleep(timeout)		

	if options.verbose: 
		print "Apache metrics:" 
		pp.pprint(metvals)

	for m in metvals:
		val = float(metvals[m])
		conn.put_metric_data(namespace=namespace,
							 name=metricname+m,
							 value=val,
							 unit=unitname,
							 dimensions=dict(instanceId=thisInstanceId))
	if options.verbose:
		print "Submitting the following data:"
		print "Namespace %s , value %s , unitname %s" % (metricname+m, val, unitname)
		print "Dimensions: %s " % str(dict(instanceId=thisInstanceId))
		


	sys.exit(0)

def optionParser():
	parser = optparse.OptionParser()
	parser.add_option("-v","--verbose" ,dest="verbose" ,action="store_true",default=False)
	parser.add_option("-r","--retry"   ,dest="retry", action="store", default=1, help="Number of Apache retries before submit")

	return parser.parse_args()	


if __name__ == "__main__":
	main()
