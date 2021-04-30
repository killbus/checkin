#!/bin/bash

# env >> /etc/environment
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# remove first and last quote (")
CRON="${CRON%\"}"
CRON="${CRON#\"}"

echo "SHELL=/bin/bash" > /var/spool/cron/crontabs/root
echo "BASH_ENV=/container.env" >> /var/spool/cron/crontabs/root
echo "${CRON} /usr/bin/flock -n /tmp/fcj.lockfile python /usr/src/app/discuz/discuz.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /var/spool/cron/crontabs/root

tini -s -- cron -f -l 2