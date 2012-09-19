#!/usr/bin/python
import re,sys,pprint
import commands
import boto, boto.ec2, boto.ec2.cloudwatch, boto.ec2.autoscale
import metrics,time 

from boto.ec2.cloudwatch import MetricAlarm
from boto.ec2.autoscale import ScalingPolicy

thisInstanceId      = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id")
thisRegion          = commands.getoutput("wget -q -O - http://169.254.169.254/latest/meta-data/placement/availability-zone")
namespace           = "Byte/System"
# Connections
clconn              = boto.ec2.cloudwatch.connect_to_region(thisRegion[:-1])
ec2conn             = boto.ec2.connect_to_region(thisRegion[:-1])
asconn              = boto.ec2.autoscale.connect_to_region(region_name=thisRegion[:-1])


alarmname           = thisInstanceId + "ApacheStatus"
metricname          = "Apachestatus"
unitname            = "Maximum"	
apachemetrics       = metrics.apacheMetrics()
dimensions          = {"instanceId" : thisInstanceId}

# Loop through all instances, find this instance and get it's aws:autoscaling:groupName
all_instances       = ec2conn.get_all_instances()
instances           = [i for r in all_instances for i in r.instances]
for instance in instances:
    if instance.__dict__['id'] == thisInstanceId:
       thisAutoScalename = instance.__dict__['tags']['aws:autoscaling:groupName']

# Define the ScaleDownPolicy
ScalingDownPolicy = ScalingPolicy(name='ctScaleDown',
                                              adjustment_type='ChangeInCapacity',
                                              as_name=thisAutoScalename,
                                              scaling_adjustment=-1,
                                              cooldown=180)

asconn.create_scaling_policy(ScalingDownPolicy)

ScaleDownPolicy = asconn.get_all_policies(as_group=thisAutoScalename, policy_names=['ctScaleDown'])[0]

alarm_actions       = []
alarm_actions.append(ScaleDownPolicy.policy_arn)

ApacheStatusAlarm   = MetricAlarm(name=alarmname,
                                    namespace=namespace,
                                    metric=metricname,
                                    statistic=unitname,
                                    comparison='>',
                                    threshold='2',
                                    period='60',
                                    evaluation_periods=2,
				    alarm_actions=alarm_actions,
                                    dimensions=dimensions)
clconn.create_alarm(ApacheStatusAlarm)
