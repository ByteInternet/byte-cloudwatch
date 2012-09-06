#!/usr/bin/python
import re,sys,pprint
import commands
import optparse,logging
import boto, boto.ec2, boto.ec2.cloudwatch
import metrics,time 

pp             = pprint.PrettyPrinter(indent=4)
thisInstanceId = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id")
thisRegion     = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/placement/availability-zone")
namespace      = "Byte/System"

def main():

	(options,args) = optionParser()
	conn = boto.ec2.cloudwatch.connect_to_region(thisRegion[:-1])
 	### Apache Metrics
	metricname  = "Apache"
	unitname = "Count"		
	apachemetrics = metrics.apacheMetrics()

	# For disk we always want percentage used (other options: free/used bytes)
	metvals = apachemetrics.status()

	for n in range(0,int(options.retry)):
		if metvals["status"] == 0:
			break
		else:
			if options.verbose:
				print "Apache not running... Trying apache2 restart..."
				print commands.getoutput("service apache2 start")
			metvals = apachemetrics.running()
			time.sleep(5)		

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
	sys.exit(0)

def optionParser():
	parser = optparse.OptionParser()
	parser.add_option("-v","--verbose" ,dest="verbose" ,action="store_true",default=False)
	parser.add_option("-r","--retry"   ,dest="retry", action="store", default=1, help="Number of Apache retries before submit")

	return parser.parse_args()	


if __name__ == "__main__":
	main()
