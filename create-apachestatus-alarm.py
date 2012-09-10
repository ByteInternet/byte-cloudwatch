#!/usr/bin/python
import re,sys,pprint
import commands
import boto, boto.ec2, boto.ec2.cloudwatch
import metrics,time 

thisInstanceId      = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id")
thisRegion          = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/placement/availability-zone")
namespace           = "Byte/System"
conn                = boto.ec2.cloudwatch.connect_to_region(thisRegion[:-1])
alarmname           = thisInstanceId + "ApacheStatus"
metricname          = "Apachestatus"
unitname            = "Count"		
apachemetrics       = metrics.apacheMetrics()
dimensions          = {"instanceId" : thisInstanceId}

alarm_actions       = []

ApacheStatusAlarm   = MetricAlarm(name=alarmname,
                                    namespace=namespace,
                                    metric=metricname,
                                    statistic=unitname,
                                    comparison='>',
                                    threshold='2',
                                    period='60',
                                    evaluation_periods=2,
                                    actions_enabled=True,
                                    alarm_action=alarm_actions,
                                    dimensions=dimensions)
conn.create_alarm(ApacheStatusAlarm)
