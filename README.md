# Byte-Cloudwatch

This repository provides scripts to setup cloudwatch (multinode branch) or to monitor apache (singlenode branch).

* (singlenode branch) check-apache-metric.py - Checks is Apache is running. If not, it will try to restart apache. If that fails X times (X=specified with -r) it will reboot the instance.
    * -r: Number of Apache retries before submit
* metrics.py (undef) - Robin?
* put-system-metrics.py (undef) - Robin?

check-apache-metric.py should be run every minute (using cron, for example) to effectively monitor apache.
