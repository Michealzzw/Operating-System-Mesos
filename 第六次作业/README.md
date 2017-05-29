第六次作业报告
================
郑子威 1300012711 信息科学技术学院

Assignment
--------------
完成以下工作，并撰写报告:
<br>
<br>完成以下工作，并撰写报告:
<br>阅读Paxos算法的材料并用自己的话简单叙述
<br>模拟Raft协议工作的一个场景并叙述处理过程
<br>简述Mesos的容错机制并验证
<br>综合作业：
<br>编写一个mesos framework，使用calico容器网络自动搭建一个docker容器集群（docker容器数量不少于三个），并组成etcd集群，在etcd选举出的master节点上部署jupyter notebook，使得可以从外部访问该集群。同时满足以下条件：
<br>这些docker容器共用一套分布式存储
<br>这些docker容器可以互相免密码ssh登录，且在host表中的名字从XXX-0一直到XXX-n（XXX是自己取的名字，n是容器数量-1），其中XXX-0是etcd的master节点
<br>当其中一个容器被杀死时，集群仍满足上一个条件
<br>当etcd master节点被杀死时，jupyter notebook会转移到新的master节点提供服务，集群仍满足上一个条件。

Paxos算法描述
-------------------------
Paxos算法解决的是带有限定条件的拜占庭问题。在拜占庭问题中，只能保证大部分人是可靠的，但是信道与消息都有可能是不可靠的；而Paxos要求信道一定是可靠的，在这个限定条件下，保证一致性。<br>
在Paxos算法中，存在四个角色，Learner、Acceptor、Proposer和Client，如图：<br>
![Paxos](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/paxos.png)
如图，共有四种行为：<br>
（1）Proposer提出议题；<br>
（2）Acceptor初步接受，或者Acceptor初步不接受；<br>
（3）如果上一步Acceptor初步接受则Proposer再次向Acceptor确认是否最终接受；<br>
（4）Acceptor 最终接受 或者Acceptor 最终不接受。<br>
Paxos遵守一下几个规则来保证一致性：<br>
（1）Learner只接受当且仅当半数以上Acceptor接受的Proposal（只要某一时刻达到这个状态，Learner就会接受）。<br>
（2）Acceptor只会接受当前最后收到的Proposal。<br>
大致一个过程是这样的，proposer提出一个proposal，然后依次向每一个Acceptor初次提交申请，初次提交完毕后，第二次在统一询问所有accpetor是否接受这个proposal，如果接受就通过了，并且交由client执行下去，如果得到的结果是已经有别的proposal通过了，那么也直接执行这个通过了的proposal。也就是一旦learner得到一个结果，所有client都会执行这个结果，这就保持了一致性。此外，Acceptor在没有最终确认之前，每次收到新请求就会接受这个新请求。

Raft协议工作场景
--------------------
过去, Paxos一直是分布式协议的标准，但是Paxos难于理解，更难以实现，Google的分布式锁系统Chubby作为Paxos实现曾经遭遇到很多坑。<br>
来自Stanford的新的分布式协议研究称为Raft，它是一个为真实世界应用建立的协议，主要注重协议的落地性和可理解性。<br>
Consensus一致性:为了以容错方式达成一致，我们不可能要求所有服务器100%都达成一致状态，只要超过半数的大多数服务器达成一致就可以了，假设有N台服务器，N/2 +1 就超过半数，代表大多数了。<br>
Paxos和Raft都是为了实现Consensus一致性这个目标，这个过程如同选举一样，参选者需要说服大多数选民(服务器)投票给他，一旦选定后就跟随其操作。Paxos和Raft的区别在于选举的具体过程不同。<br>

在Raft中，存在下面三种角色：

    <br>Leader: 处理所有客户端交互，日志复制等，一般一次只有一个Leader.
    <br>Follower: 类似选民，完全被动
    <br>Candidate候选人: 类似Proposer律师，可以被选为一个新的领导人。

下面描述一个3服务器的选举过程：<br>
（1）首先，对于联通的服务器中，没有一个Leader的时候，任何一个服务器都可以选择成为Candidate，然后对所有follower请求邀票<br>
![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft1.png)<br>
![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft2.png)<br>
（2）得到大多数票之后，该服务器成为Leader并进行指令<br>

![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft3.png)<br>
![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft4.png)<br>
![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft5.png)<br>
（3）此时，如果Leader挂掉了，剩下的部分follower自动成为Candidate，邀票<br>
![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft6.png)<br>
（4）如果有多个Candidate，那么在timeout之后再次投票。<br>
![raft](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/raft7.png)<br>
还有一种情况，如果在这一过程中，发生了网络分区或者网络通信故障，使得Leader不能访问大多数Follwers了，那么Leader只能正常更新它能访问的那些Follower服务器，则失去Leader的组继续选举一个新Leader来与外界通讯，如果之后恢复了，则原来的旧Leader自动退化，他的所有更新都不算commit，并且回滚到新Leader的更新。<br>
日志复制：<br>
1. 假设Leader领导人已经选出，这时客户端发出增加一个日志的要求。<br>
2. Leader要求Followe遵从他的指令，都将这个新的日志内容追加到他们各自日志中。<br>
3. 大多数follower服务器将日志写入磁盘文件后，确认追加成功，发出Commited Ok。 <br>
4. 在下一个心跳heartbeat中，Leader会通知所有Follwer更新commited 项目。<br>


Mesos容错机制
-------------------------
Mesos Framework会自动检查agent的状态，而master的容错机制通过zookeeper实现。<br>
Mesos使用热备份技术，运用ZooKeeper同时运行多个master，一个作为活跃，其他作为备份。<br>
当当前的master挂掉时，agent和scheduler可以连接到新被选举出的备份的master上，使其成为活跃的master。<br>
下面验证安装zookeeper：<br>
三台机器上，从官网上下载并解压，进入conf进行配置文件
```
wget http://mirrors.hust.edu.cn/apache/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
tar -xvf zookeeper-3.4.6.tar.gz
cd zookeeper-3.4.6/conf
cp zoo_sample.cfg zoo.cfg
```
在所有机器上设置cfg如下：
```
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/home/pkusei/zookeeper
# the port at which the clients will connect
clientPort=2181
#master
server.1=172.16.1.137:2888:3888
server.2=172.16.1.236:2888:3888
server.3=172.16.1.33:2888:3888
```
之后在每一台机器上设置myid
```
mkdir ~/zookeeper
echo "1" > ~/zookeeper/myid #1001
echo "2" > ~/zookeeper/myid #1002
echo "3" > ~/zookeeper/myid #1003
```
每一台机器上启动zooServer
```
bin/zkServer.sh start

ZooKeeper JMX enabled by default
Using config: /home/pkusei/zookeeper-3.4.6/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
```
成功之后，查看三台机器的zookeeper情况，发现已经一台是Leader，其他是Follower
```
pkusei@oo-lab:~/zookeeper-3.4.6$ bin/zkServer.sh status
JMX enabled by default
Using config: /home/pkusei/zookeeper-3.4.6/bin/../conf/zoo.cfg
Mode: follower
pkusei@oo-lab:~/zookeeper-3.4.6$

pkusei@oo-lab:~/zookeeper-3.4.6$ bin/zkServer.sh status
JMX enabled by default
Using config: /home/pkusei/zookeeper-3.4.6/bin/../conf/zoo.cfg
Mode: leader
pkusei@oo-lab:~/zookeeper-3.4.6$
pkusei@oo-lab:~/zookeeper-3.4.6$ vim zookeeper.out
pkusei@oo-lab:~/zookeeper-3.4.6$ bin/zkServer.sh status
JMX enabled by default
Using config: /home/pkusei/zookeeper-3.4.6/bin/../conf/zoo.cfg
Mode: follower
pkusei@oo-lab:~/zookeeper-3.4.6$
```
在三台机器上，运行zookeeper模式下的mesos-master与mesos-agent
```
sudo nohup mesos-master --zk=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos \
--quorum=2 --ip=172.16.1.137 --port=5050 --cluster=mesos_with_zookeeper \
--hostname=162.105.174.25 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
> master.log 2>&1 &


sudo nohup mesos-master --zk=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos \
--quorum=2 --ip=172.16.1.236 --port=5050 --cluster=mesos_with_zookeeper \
--hostname=162.105.174.25 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
> master.log 2>&1 &

sudo nohup mesos-master --zk=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos \
--quorum=2 --ip=172.16.1.33 --port=5050 --cluster=mesos_with_zookeeper \
--hostname=162.105.174.25 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
> master.log 2>&1 &


nohup mesos-agent --master=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos --work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.1.137 --port=5051 \
--hostname=162.105.174.25 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &

nohup mesos-agent --master=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos --work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.1.236 --port=5051 \
--hostname=162.105.174.25 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &

nohup mesos-agent --master=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos --work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.1.33 --port=5051 \
--hostname=162.105.174.25  --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &
```

![suicide](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/1.pic_hd.jpg)
此时，暂停Leader mesos-master，再查看zookeeper的日志，发现一个master被推选为新的Leader
```
kill -SIGSTOP 18554

I0527 07:57:46.509798 13328 group.cpp:340] Group process (zookeeper-group(4)@172.16.1.236:5050) connected to ZooKeeper
I0527 07:57:46.509824 13328 group.cpp:830] Syncing group operations: queue size (joins, cancels, datas) = (0, 0, 0)
I0527 07:57:46.509829 13328 group.cpp:418] Trying to create path '/mesos' in ZooKeeper
I0527 07:57:46.514636 13322 contender.cpp:268] New candidate (id='4') has entered the contest for leadership
I0527 07:57:46.518590 13323 network.hpp:432] ZooKeeper group memberships changed
I0527 07:57:46.518712 13325 group.cpp:699] Trying to get '/mesos/log_replicas/0000000002' in ZooKeeper
I0527 07:57:46.518831 13328 detector.cpp:152] Detected a new leader: (id='3')
I0527 07:57:46.519179 13327 group.cpp:699] Trying to get '/mesos/json.info_0000000003' in ZooKeeper
I0527 07:57:46.520280 13322 replica.cpp:495] Replica received implicit promise request from __req_res__(2)@172.16.1.33:5050 with proposal 9
I0527 07:57:46.521106 13325 group.cpp:699] Trying to get '/mesos/log_replicas/0000000003' in ZooKeeper
I0527 07:57:46.522085 13328 zookeeper.cpp:259] A new leading master (UPID=master@172.16.1.33:5050) is detected
I0527 07:57:46.523219 13328 master.cpp:2137] The newly elected leader is master@172.16.1.33:5050 with id b3496c49-1c1d-444a-864a-3c1bbcf7fdd4
I0527 07:57:46.522652 13327 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.1.33:5050, log-replica(1)@172.16.1.236:5050 }
I0527 07:57:46.524014 13322 replica.cpp:344] Persisted promised to 9
I0527 07:57:46.528012 13328 replica.cpp:539] Replica received write request for position 113 from __req_res__(4)@172.16.1.33:5050





I0527 08:28:46.011745 13328 network.hpp:432] ZooKeeper group memberships changed
I0527 08:28:46.011874 13328 group.cpp:699] Trying to get '/mesos/log_replicas/0000000003' in ZooKeeper
I0527 08:28:46.014782 13329 detector.cpp:152] Detected a new leader: (id='4')
I0527 08:28:46.014858 13329 group.cpp:699] Trying to get '/mesos/json.info_0000000004' in ZooKeeper
I0527 08:28:46.016595 13329 zookeeper.cpp:259] A new leading master (UPID=master@172.16.1.236:5050) is detected
I0527 08:28:46.016887 13329 master.cpp:2124] Elected as the leading master!
I0527 08:28:46.016911 13329 master.cpp:1646] Recovering from registrar
I0527 08:28:46.017884 13329 log.cpp:553] Attempting to start the writer
I0527 08:28:46.018924 13324 replica.cpp:495] Replica received implicit promise request from __req_res__(3)@172.16.1.236:5050 with proposal 10
I0527 08:28:46.019814 13324 replica.cpp:344] Persisted promised to 10
I0527 08:28:46.023479 13328 group.cpp:699] Trying to get '/mesos/log_replicas/0000000004' in ZooKeeper
I0527 08:28:46.023818 13323 coordinator.cpp:238] Coordinator attempting to fill missing positions
I0527 08:28:46.023892 13323 log.cpp:569] Writer started with ending position 120
I0527 08:28:46.025048 13323 registrar.cpp:362] Successfully fetched the registry (755B) in 7.931136ms
I0527 08:28:46.025164 13323 registrar.cpp:461] Applied 1 operations in 23919ns; attempting to update the registry
I0527 08:28:46.026494 13323 coordinator.cpp:348] Coordinator attempting to write APPEND action at position 121
I0527 08:28:46.026841 13323 replica.cpp:539] Replica received write request for position 121 from __req_res__(6)@172.16.1.236:5050
I0527 08:28:46.029083 13326 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.1.137:5050, log-replica(1)@172.16.1.236:5050 }
I0527 08:28:46.029610 13325 replica.cpp:693] Replica received learned notice for position 121 from @0.0.0.0:0

```
然后再次恢复之前停止的master之后，因为查找不到新的master，这个master自杀了
![suicide](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/2.pic_hd.jpg)
```
root@oo-lab:/home/pkusei/zookeeper-3.4.6# kill -SIGCONT 18554
root@oo-lab:/home/pkusei/zookeeper-3.4.6#
[1]-  Exit 1                  sudo nohup mesos-master --zk=zk://172.16.1.137:4181,172.16.1.236:4181,172.16.1.33:4181/mesos --quorum=2 --ip=172.16.1.33 --port=5050 --cluster=mesos_with_zookeeper --hostname=162.105.174.25 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos > master.log 2>&1
```

综合作业
-------------------------
<br>编写一个mesos framework，使用calico容器网络自动搭建一个docker容器集群（docker容器数量不少于三个），并组成etcd集群，在etcd选举出的master节点上部署jupyter notebook，使得可以从外部访问该集群。同时满足以下条件：
<br>这些docker容器共用一套分布式存储
<br>这些docker容器可以互相免密码ssh登录，且在host表中的名字从XXX-0一直到XXX-n（XXX是自己取的名字，n是容器数量-1），其中XXX-0是etcd的master节点
<br>当其中一个容器被杀死时，集群仍满足上一个条件
<br>当etcd master节点被杀死时，jupyter notebook会转移到新的master节点提供服务，集群仍满足上一个条件。
<br>
<br>
集群安装流程同hw5，安装calico_net
### 分布式存储
本次作业采用glusterfs作为分布式存储，设置一个三台机器上的bluster_server。结果如下 <br>
```
pkusei@oo-lab:~/hw6_gluster$ sudo gluster volume info

Volume Name: hw6_gluster
Type: Replicate
Volume ID: 682e12ff-3480-4cad-a4fb-24313dea6877
Status: Started
Snapshot Count: 0
Number of Bricks: 1 x 3 = 3
Transport-type: tcp
Bricks:
Brick1: server0:/home/pkusei/hw6_gluster
Brick2: server1:/home/pkusei/hw6_gluster
Brick3: server2:/home/pkusei/hw6_gluster
```
由于server是不能够用来修改的，因此在三台机器上都部署gluster客户端文件夹。
```
sudo mount  -t glusterfs server0:/home/pkusei/hw6_gluster ~/hw6_client
```
此时hw6_client就是docker container挂载的文件夹
### 监控host表
host表实时修改的原理在于每一个节点能够实时更新自己host。这里我们使用etcdctl来实现：<br>
对于集群中的每一个节点，可以通过etcdctl来以键值对的方式共享数据。<br>
etcdclt可以设置键值对的生命周期，同时还可以设置对文件的监控，一旦文件发生改变就可以进行操作。
```
etcdctl mk /hosts #新建文件hosts
etcdctl updatedir --ttl 30 /hosts #存活周期为30秒，所以30秒后就会死亡
etcdctl mk /hosts/<name> <value> 添加键值对
etcdctl exec-watch --recursive /hosts -- [command] #设置watch操作，一旦hosts发生变化就会进行操作
```
所以通过一个监控脚本来更新/etc/hosts表
```
#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, fcntl
import urllib2

action = os.getenv('ETCD_WATCH_ACTION')

response = urllib2.urlopen('http://127.0.0.1:2379/v2/stats/self')
result = reponse.read().decode('utf-8')
data = json.loads(result)

if action == 'expire': #重新刷新host
	if data['state'] == 'StateLeader':
		os.system('/usr/local/bin/etcdctl mk /hosts/local-' + ip_addr + ' ' + ip_addr)
		os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')

else if action == 'create':
	if data['state'] == 'StateFollower':
		os.system('/usr/local/bin/etcdctl mk /hosts/' + ip_addr + ' ' + ip_addr)
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

```
### 互相免密登陆
互相免密登陆的原理是，设置一个共享文件夹用于存储集群中所有节点的ssh公钥，然后在启动ssh之前，将ssh的密码文件改为共享文件夹，这样每次登陆的时候ssh就会先对文件夹扫描看是否存在这个节点的公钥，如果存在就可以无密登陆。
如下
```
ssh-keygen -f /home/admin/.ssh/id_rsa -t rsa -N "" #生成密钥
echo "admin" | sudo -S bash -c "cat /home/admin/.ssh/id_rsa.pub >> /ssh_key/authorized_keys" #加入共享文件夹
/usr/sbin/service ssh start #开启ssh
```
### 入口脚本
入口脚本需要完成以下几个工作:<br>
（1）配置ssh<br>
（2）打开etcd<br>
（3）设置etcdctl的键值监控<br>
（4）定期更新etcdctl/hosts键值对<br>
（5）当前查看是否master，是则启动jupyter
```
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

```
### Dockerfile
```
FROM ubuntu:latest

RUN apt update
RUN apt install -y sudo
RUN apt install -y python3-pip
RUN apt install -y ssh
RUN apt install -y net-tools
RUN apt install -y curl
RUN apt install -y vim
RUN pip3 install --upgrade pip
RUN pip3 install jupyter

RUN useradd -ms /bin/bash admin && adduser admin sudo && echo 'admin:admin' | chpasswd

RUN wget -P /root https://github.com/coreos/etcd/releases/download/v3.1.7/etcd-v3.1.7-linux-amd64.tar.gz && tar -zxf /root/etcd-v3.1.7-linux-amd64.tar.gz -C /root
RUN ln -s /root/etcd-v3.1.7-linux-amd64/etcd /usr/local/bin/etcd && ln -s /root/etcd-v3.1.7-linux-amd64/etcdctl /usr/local/bin/etcdctl

RUN mkdir /var/run/sshd
RUN echo 'AuthorizedKeysFile /ssh_key/authorized_keys' >> /etc/ssh/sshd_config
ADD code/ /home/admin/code/
RUN mkdir /home/admin/shared_folder
USER admin
WORKDIR /home/admin

CMD ["/usr/bin/python3", "/home/admin/code/start.py"]

```
### 自动代理
需要分别扫描五个端口，依次发送request请求，然后对应的设置configure_proxy。因此写一个python来实时扫描：
```
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
```
### 结果
![suicide](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/3.pic_hd.jpg)
![suicide](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/4.pic_hd.jpg)
![suicide](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/5.pic_hd.jpg)
![suicide](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第六次作业/6.pic.jpg)
