第四次作业报告
================
郑子威 1300012711 信息科学技术学院

Assignment
--------------
完成以下工作，并撰写报告:
<br>
调研两种以上的分布式文件系统以及一种联合文件系统，说明其工作原理和特点以及使用方式。
<br>
安装配置一种分布式文件系统，要求启动容错机制，即一台存储节点挂掉仍然能正常工作。在报告里阐述搭建过程和结果。
<br>
在上次作业的基础上，将web服务器的主页提前写好在分布式文件系统里，在docker容器启动的时候将分布式文件系统挂载到容器里，并将该主页拷贝到正确的路径下，使得访问网站时显示这个主页。在报告中详细阐述过程和结果。
<br>
Docker中使用了联合文件系统来提供镜像服务，了解docker的镜像机制，并仿照其工作机制完成一次镜像的制作，具体要求为:创建一个docker容器，找到其文件系统位置，并将其保存，然后在该容器中安装几个软件包，找到容器的只读层（保存着这几个软件包），将其保存，之后通过aufs将这两个保存的文件系统挂载起来，使用docker import命令从其中创建镜像，并从该镜像中创建容器，要求此时可以使用之前安装好的软件包。在报告中详细阐述过程。
<br>

文件系统介绍
---------------
### HDFS

Hadoop分布式文件系统(HDFS)被设计成适合运行在通用硬件(commodity hardware)上的分布式文件系统。它和现有的分布式文件系统有很多共同点。但同时，它和其他的分布式文件系统的区别也是很明显的。HDFS是一个高度容错性的系统，适合部署在廉价的机器上。HDFS能提供高吞吐量的数据访问，非常适合大规模数据集上的应用。HDFS放宽了一部分POSIX约束，来实现流式读取文件系统数据的目的。HDFS在最开始是作为Apache Nutch搜索引擎项目的基础架构而开发的。HDFS是Apache Hadoop Core项目的一部分。<br>
HDFS有着高容错性（fault-tolerant）的特点，并且设计用来部署在低廉的（low-cost）硬件上。而且它提供高吞吐量（high throughput）来访问应用程序的数据，适合那些有着超大数据集（large data set）的应用程序。HDFS放宽了（relax）POSIX的要求（requirements）这样可以实现流的形式访问（streaming access）文件系统中的数据。<br>
![hdfs](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第四次作业/hdfs.jpeg)
如上图所示，HDFS也是按照Master和Slave的结构。分NameNode、SecondaryNameNode、DataNode这几个角色。
```
NameNode：是Master节点，是大领导。管理数据块映射；处理客户端的读写请求；配置副本策略；管理HDFS的名称空间；

SecondaryNameNode：是一个小弟，分担大哥namenode的工作量；是NameNode的冷备份；合并fsimage和fsedits然后再发给namenode。

DataNode：Slave节点，奴隶，干活的。负责存储client发来的数据块block；执行数据块的读写操作。

热备份：b是a的热备份，如果a坏掉。那么b马上运行代替a的工作。

冷备份：b是a的冷备份，如果a坏掉。那么b不能马上代替a工作。但是b上存储a的一些信息，减少a坏掉之后的损失。

fsimage:元数据镜像文件（文件系统的目录树。）

edits：元数据的操作日志（针对文件系统做的修改操作记录）

namenode内存中存储的是=fsimage+edits。

SecondaryNameNode负责定时默认1小时，从namenode上，获取fsimage和edits来进行合并，然后再发送给namenode。减少namenode的工作量。
```


### GlusterFS
主要应用在集群系统中，具有很好的可扩展性。软件的结构设计良好，易于扩展和配置，通过各个模块的灵活搭配以得到针对性的解决方案。可解决以下问题：网络存储，联合存储(融合多个节点上的存储空间)，冗余备份，大文件的负载均衡(分块)。由于缺乏一些关键特性，可靠性也未经过长时间考验，还不适合应用于需要提供 24 小时不间断服务的产品环境。目前适合应用于大数据量的离线应用。<br>
GlusterFS通过Infiniband RDMA 或者Tcp/Ip 方式将许多廉价的x86 主机，通过网络互联成一个并行的网络文件系统<br>
![gluster](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第四次作业/glusterfs.png)

当GlusterFS安装在某个服务器端时，会创建一个gluster管理的后台进程，这个后台进程(glusterd)在集群中的每个服务端结点都会运行。之后，便会组织形成一个可信任的服务器池，brick可以通过这个服务器池作为目录被导出，多个brick可以组合成卷。<br>

在一个卷被创建后，glusterfsd进程开始运行在每个贡献brick的机器中。该进程会在/var/lib/glusterd/vols中创建配置文件，表示每个块在卷中的细节信息。客户端进程需要的配置文件也会被创建。<br>
当我们在客户端挂载该卷的时候，客户端glusterfs进程会和服务器端的glusterd进程通信。服务器端的glusterd进程会发送包含有客户端翻译表和其他一些能帮助客户端glusterfs进程直接和每个brick的glusterfsd进程通信的配置文件。<br>
使用方法
```
mount -t glusterfs <IP or hostname>:<volume_name> <mount_point>
```
### GFS
GFS（Goole File System）的主要假设如下：<br>
GFS的服务器都是普通的商用计算机，并不那么可靠，集群出现结点故障是常态。因此必须时刻监控系统的结点状态，当结点失效时，必须能检测到，并恢复之。<br>
系统存储适当数量的大文件。理想的负载是几百万个文件，文件一般都超过100MB，GB级别以上的文件是很常见的，必须进行有效管理。支持小文件，但不对其进行优化。<br>
负载通常包含两种读：大型的流式读（顺序读），和小型的随机读。前者通常一次读数百KB以上，后者通常在随机位置读几个KB。<br>
负载还包括很多连续的写操作，往文件追加数据（append）。文件很少会被修改，支持随机写操作，但不必进行优化。<br>
系统必须实现良好定义的语义，用于多客户端并发写同一个文件。同步的开销必须保证最小。<br>
高带宽比低延迟更重要，GFS的应用大多需要快速处理大量的数据，很少会严格要求单一操作的响应时间。<br>

从这些假设基本可以看出GFS期望的应用场景应该是大文件，连续读，不修改，高并发。国内的淘宝文件系统（TFS）就不一样，专门为处理小文件进行了优化。<br>

GFS主要由以下三个系统模块组成：<br>
Master：管理元数据、整体协调系统活动<br>
ChunkServer：存储维护数据块（Chunk），读写文件数据<br>
Client：向Master请求元数据，并根据元数据访问对应ChunkServer的Chunk<br>
![GFS](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第四次作业/gfs.jpeg)

### AUFS --- 联合文件系统
AUFS是一种Union File System，叫做Advance UFS。UnionFS就是把不同物理位置的目录合并mount到同一个目录中。<br>
AUFS完全重写了早期的UnionFS 1.x，其主要目的是为了可靠性和性能，并且引入了一些新的功能，比如可写分支的负载均衡。AUFS在使用上全兼容UnionFS，而且比之前的UnionFS在稳定性和性能上都要好很多。<br>
![aufs](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第四次作业/aufs.png)
Docker系统就是基于aufs，aufs的特性就在于，将多个目录合并到一个目录后，默认只有mount命令中第一个（也被称为最上层）目录是可读写的，后面多个都是只读的。然后对于挂载的目录，任何文件修改事实上都只操作了最上层目录。这个机制基于几个规则:<br>
同名（即同路径同名）文件，读到的是上层目录的。<br>
新建，修改：在最上层目录新建该文件<br>
删除：在最上层目录添加不可见的删除标记<br>
通过这么几个规则，docker就可以实现它的镜像操作，对于新建的镜像，新建一个最上层目录，后面mount上继承镜像的所有目录，这样对于新镜像的所有修改都只修改了属于新镜像的最上层目录。<br>
使用方法：
```
mount -v -t aufs -o br=A:B:.... none [挂载到的目录]
```
A即为最上层目录。<br>

安装分布式文件系统
---------------
Docker系统上常用的分布式文件系统有Gluster和MooseFS。本次作业安装并挂载的是Gluster系统。
### 安装Gluster
通过PPA安装glusterfs-3.10(https://launchpad.net/~gluster/+archive/ubuntu/glusterfs-3.10)　。为了启动容错机制，三台服务器，两个作为服务器，一个作为客户端
```
sudo add-apt-repository ppa:gluster/glusterfs-3.10
sudo apt-get update
sudo apt-get install glusterfs-client #客户端，1003(172.16.1.33)
sudo apt-get install glusterfs-server #服务器端，1001(172.16.1.137)，1002(172.16.1.236)
```
在三台机器的/etc/hosts中都添加hostname server0 server1<br>

在server0上操作，创建卷my-volume
```
sudo gluster peer probe server1
sudo gluster volume create my-volume replica 2 server0:/home/pkusei/gluster-data server1:/home/pkusei/gluster-data
sudo gluster volume start my-volume
```
在客户端上操作，新建gluster-client-data，挂载my-volume
```
sudo mount -t glusterfs server0:/my-volume ./gluster-cilent-data/
```
此时已经完成挂载，在客户端的文件夹上做任何修改都能在server的brick上看到。<br>

挂载分布式文件系统
---------------
将上次作业的index.html拷贝到my-volume中，然后直接将该文件夹挂载到容器中nginx的html文件夹
```
cp ~/mydocikerbuild/index.nginx-debian.html ~/gluster-cilent-data/
sudo docker run -v ~/gluster-cilent-data:/var/www/html/ -p 10080:80 -d --name nginx-gluster my-docker-nginx-gluster
```
成功，能在http://162.105.174.25:10080/ 访问到网页，同时直接在my-volume就可以直接修改容器内部的主页<br>

Docker镜像制作    
---------------
启动一个ubuntu镜像的docker容器，查看挂载情况（需要sudo才能看到全部挂载）
```
sudo df -hT
none                         aufs             19G   12G  5.3G  70% /var/lib/docker/aufs/mnt/794c421d66fb514ad760a1d12284ebd327731f67d2383a0bf92577ca1c094580
```
进入该目录需要root账户，因此现设置root密码，切换至root：
```
sudo passwd root
su - root
cd /var/lib/docker/aufs/layers
root@oo-lab:/var/lib/docker/aufs/layers# cat 794c421d66fb514ad760a1d12284ebd327731f67d2383a0bf92577ca1c094580
794c421d66fb514ad760a1d12284ebd327731f67d2383a0bf92577ca1c094580-init
7fc03a7b0456cfff19352630545e9ecdf7985e7ce870cf977725f8522bc6a6a9
11c73ef4d95483ca8918c62aec0b7926f03890b071a5ab0646f87f072e71f747
13650ef0e89def6b876c9a9a5d926a84ca5a6f08991b34d769286398e92ba5be
e6fe59d226bdfac0e4a0fd9528fb1c0a2ac18fa35a2be60a2dd1e4dfcaa08328
57ed963ea7aeb419abd9f2df3a46f97a4af81f2dfc4abba657b3f92bae30ea18
9dba165e0d3fa7a514d4c1add0f1d17f84f7324163edbfcc987853796b83b90d
```
于是切换到../diff，将对应id的文件夹都拷贝到一个新建的文件夹，作为本地镜像的文件夹
```
mkdir /home/pkusei/myimage
cp -r [id] /home/pkusei/myimage/
```
在容器中安装一个vim
```
apt update
apt-get install vim
```
最后把修改过的，容器最高层（上面init的794c421d66fb514ad760a1d12284ebd327731f67d2383a0bf92577ca1c094580）对应的层拷贝到myimage中<br>
挂载所有文件到一个文件夹，导入为docker镜像
```
cd ~/myimage
mkdir merge
sudo mount -v -t aufs -o br=./6:./5:./4:./3:./2:./1:./0 none ./merge/
~/myimage/merge$ sudo tar -c . | sudo docker import - my_image
sha256:ecf306316f10e3c00ec13c7d5e739559e6f091abfb5095f616ddea89299afe57
```
最后，测试是否成功
```
 docker run -it my_image /bin/bash
 vim
 ```
