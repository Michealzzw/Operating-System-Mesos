#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, time
import urllib.request, urllib.error
import http.client

def signal_handler(signal, frame):
	global last_pid, last_master
	if last_master != -1:
		last_pid.kill()

	sys.exit(0)
def main():
	global last_pid, last_master
	addr = '172.16.1.137'

	last_master = -1

	signal.signal(signal.SIGINT, signal_handler)

	while True:

		for i in range(5):
			try:
				response = urllib2.urlopen('http://127.0.0.1:2379/v2/stats/self')
			except (urllib.error.URLError, socket.timeout):
				print ("node "+str(i)" is not master")
			else:
				result = reponse.read().decode('utf-8')
		        data = json.loads(result)
				if data['state'] == 'StateLeader':
					print ("node "+str(i)" is master")
					if last_master != i:
						if last_master != -1:
							last_pid.kill()
						args = ['/usr/local/bin/configurable-http-proxy', '--default-target=http://192.168.0.10' + str(i) + ':8888', '--ip=' + ip_addr, '--port=8888']
						last_pid = subprocess.Popen(args)
						last_master = i



if __name__ == '__main__':
	main()
