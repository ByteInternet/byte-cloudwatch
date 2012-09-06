#!/usr/bin/python
import re,sys,pprint
import commands
import optparse,logging
import boto, boto.ec2, boto.ec2.cloudwatch
import metrics 

pp             = pprint.PrettyPrinter(indent=4)
thisInstanceId = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id")
thisRegion     = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/placement/availability-zone")
namespace      = "Byte/System"

def main():

	(options,args) = optionParser()
	conn = boto.ec2.cloudwatch.connect_to_region(thisRegion[:-1])
 	### Disk Metrics
	if options.disk != "":
		metricname  = "Disk"	
		diskmetrics = metrics.diskMetrics(options.disk)

		# For disk we always want percentage used (other options: free/used bytes)
		metvals = diskmetrics.usedpercent()

		if options.verbose: 
			print "Disk metrics (path = "+options.disk+":" 
			pp.pprint(metvals)
		for m in metvals:
			if m == "percent":
				unitname="Percent"
				val = float(metvals[m][:-1])
			else:
				unitname="Bytes"
				val = float(metvals[m])
			conn.put_metric_data(namespace=namespace,
								 name=metricname+m,
								 value=val,
								 unit=unitname,
								 dimensions=dict(instanceId=thisInstanceId))

	### File Metrics
	if options.file != "":
		metricname = "FileExists";
		fileMetrics = metrics.file()
		unitname = "Count"

		if options.verbose:
			print "File "+options.file+" exists = "+str(fileMetrics.exists(options.file))

		conn.put_metric_data(namespace=namespace,
							 name=metricname+"-"+options.file,
							 value=fileMetrics.exists(options.file),
							 unit=unitname,
							 dimensions=dict(instanceId=thisInstanceId))
		
	### Memory Metrics
	if options.mem:
		metricname = "Memory"		
		memMetrics = metrics.memoryMetrics()

		metvals = memMetrics.all()

		if options.verbose:
			print "Memory metrics:"
			pp.pprint(metvals) 
		for m in metvals:
			conn.put_metric_data(namespace=namespace,
								 name=metricname+m,
 								 value=float(metvals[m]),
								 unit="Bytes",
								 dimensions=dict(instanceId=thisInstanceId))
	sys.exit(0)

def optionParser():
	parser = optparse.OptionParser()
	parser.add_option("-v","--verbose" ,dest="verbose" ,action="store_true",default=False)
	parser.add_option("-m","--mem" ,    dest="mem",     action="store_true",default=False,
				      help="Memory metrics")
	parser.add_option("-d","--disk",    dest="disk",    action="store"     ,default="",
					  help="Disk metrics, give pathname")
	parser.add_option("-f","--file" ,   dest="file",    action="store",     default="",
					  help="File metrics, give filename")
	return parser.parse_args()	

if __name__ == "__main__":
	main()
