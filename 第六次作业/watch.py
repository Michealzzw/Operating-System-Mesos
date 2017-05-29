#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, fcntl
import urllib2

addr = sys.argv[1];
action = os.getenv('ETCD_WATCH_ACTION')

response = urllib2.urlopen('http://127.0.0.1:2379/v2/stats/self')
result = reponse.read().decode('utf-8')
data = json.loads(result)

if action == 'expire': #重新刷新host
	if data['state'] == 'StateLeader':
		os.system('/usr/local/bin/etcdctl mk /hosts/local-' + addr + ' ' + addr)
		os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')

else if action == 'create':
	if data['state'] == 'StateFollower':
		os.system('/usr/local/bin/etcdctl mk /hosts/' + addr + ' ' + addr)
	fd = os.popen('/usr/local/bin/etcdctl ls --sort --recursive /hosts')
	hosts = fd.read().strip('\n').split('\n')
	hosts_fd = open('/tmp/hosts', 'w')
	fcntl.flock(hosts_fd.fileno(), fcntl.LOCK_EX)

	hosts_fd.write('127.0.0.1 localhost cluster' + '\n')
	i = 0
	for host in hosts:
		host = host[host.rfind('/') + 1:]
		if host_ip[0] == 'l':
			hosts_fd.write(host_ip[6:] + ' cluster-' + str(i) + '\n')
		else:
			hosts_fd.write(host_ip + ' cluster-' + str(i) + '\n')
		i = i+1;

	hosts_fd.flush()
	os.system('/bin/cp /tmp/hosts /etc/hosts')

	# release the lock automatically
	hosts_fd.close()
