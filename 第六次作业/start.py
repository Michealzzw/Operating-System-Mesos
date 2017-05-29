#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, time
import urllib.request, urllib.error



fd = os.popen("ifconfig cali0 | grep 'inet addr'")
tmp = fd.read();
addr = tmp.split(' ')[1][tmp.rfind(':')+1:].strip("\n");

os.system('ssh-keygen -f /home/admin/.ssh/id_rsa -t rsa -N ""')
os.system('echo "admin" | sudo -S bash -c "cat /home/admin/.ssh/id_rsa.pub >> /ssh_info/authorized_keys"')
os.system('/usr/sbin/service ssh start')

args = ['/usr/local/bin/etcd', '--name', 'node' + addr[-1], '--data-dir', '/var/lib/etcd', '--initial-advertise-peer-urls', 'http://' + addr + ':2380', '--listen-peer-urls', 'http://' + addr + ':2380', \
'--listen-client-urls', 'http://' + addr + ':2379,http://127.0.0.1:2379', '--advertise-client-urls', 'http://' + addr + ':2379', '--initial-cluster-token', 'etcd-cluster-hw6', \
'--initial-cluster', 'node0=http://192.168.0.100:2380,node1=http://192.168.0.101:2380,node2=http://192.168.0.102:2380,node3=http://192.168.0.103:2380,node4=http://192.168.0.104:2380', \
'--initial-cluster-state', 'new']
subprocess.Popen(args)



jupyter_open = False
watch_open = False




while True:
    try:
        response = urllib2.urlopen('http://127.0.0.1:2379/v2/stats/self')
    except urllib2.error.URLError as e:
        print('ERROR ', e.reason)
    else:
        result = reponse.read().decode('utf-8')
        data = json.loads(result)
        if watch_open == False:
            watch_flag = True
            args = ['/usr/local/bin/etcdctl', 'exec-watch', '--recursive', '/hosts', '--', '/usr/bin/python3', '/home/admin/code/watch.py', addr]
            subprocess.Popen(args)


        if data['state'] == 'StateLeader':
            if jupyter_open == False:
                jupyter_open = True
                args = ['/usr/local/bin/jupyter', 'notebook', '--NotebookApp.token=', '--ip=0.0.0.0', '--port=8888']
                subprocess.Popen(args)
                os.system('/usr/local/bin/etcdctl rm /hosts')
                os.system('/usr/local/bin/etcdctl mk /hosts/local-' + addr + ' ' + addr)
                os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')
            else:
                os.system('/usr/local/bin/etcdctl mk /hosts/local-' + addr + ' ' + addr)


        elif data['state'] == 'StateFollower':
            jupyter_open = False
            os.system('/usr/local/bin/etcdctl mk /hosts/' + addr + ' ' + addr)
