import sys
import commands
import re
import os

class file:
	def exists(self,filename):
		if os.path.isfile(filename) == True:
			return 1
		else:
			return 0

class diskMetrics:
	disk = ""
	diskstats = {}
	def __init__(self,mountpoint):
		self.disk = mountpoint
	def free(self):
		self.diskstats["free"] = commands.getoutput("df "+self.disk+" | tail -n 1 | awk '{ print $4 }'")	
		return self.diskstats
	def used(self):
		self.diskstats["used"] =  commands.getoutput("df "+self.disk+" | tail -n 1 | awk '{ print $3 }'")	
		return self.diskstats
	def usedpercent(self):
		self.diskstats["percent"] = commands.getoutput("df "+self.disk+" | tail -n 1 | awk '{ print $5 }'")	
		return self.diskstats
	def all(self):
		self.free()
		self.used()
		self.usedpercent()
		return self.diskstats

class memoryMetrics:
	memoryMetrics = {}
	def free(self):
		self.memoryMetrics["free"] = commands.getoutput("free | grep Mem | awk ' { print $4 }'")
		return self.memoryMetrics
	def used(self):
		self.memoryMetrics["used"] = commands.getoutput("free | grep Mem | awk ' { print $3 }'")
		return self.memoryMetrics
	def total(self):
		self.memoryMetrics["total"] = commands.getoutput("free | grep Mem | awk ' { print $2}'")
		return self.memoryMetrics
	def all(self):
		self.free()
		self.used()
		self.total()
		return self.memoryMetrics
		return memoryMetrics

class apacheMetrics:
	apacheMetrics = {}
	# service apache status
	def status(self):
		self.apacheMetrics["status"] = commands.getstatusoutput('service apache2 status')[0] >> 8
		return self.apacheMetrics

