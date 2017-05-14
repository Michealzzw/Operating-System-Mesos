第四=五次作业报告
================
郑子威 1300012711 信息科学技术学院

Assignment
--------------
完成以下工作，并撰写报告:
<br>
<br>描述Linux内核如何对 IP 数据包进行处理。
<br>在服务器上使用iptables分别实现如下功能并测试：1)拒绝来自某一特定IP地址的访问；2）拒绝来自某一特定mac地址的访问；3）只开放本机的http服务，其余协议与端口均拒绝；4）拒绝回应来自某一特定IP地址的ping命令。
<br>解释Linux网络设备工作原理, 至少介绍bridge, vlan, veth工作过程。
<br>说明在calico容器网络中，一个数据包从源容器发送到目标容器接收的具体过程。
<br>调研除calico以外的任意一种容器网络方案(如weave、ovs、docker swarm overlay)，比较其与calico的优缺点。
<br>编写一个mesos framework，使用calico容器网络自动搭建一个docker容器集群（docker容器数量不少于三个），并在其中一个容器中部署jupyter notebook。运行后外部主机可以通过访问宿主机ip+8888端口使用jupyter notebook对docker集群进行管理。


Linux内核如何处理 IP 数据包
---------------
![层](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第五次作业/1.jpeg)
如图，从链路层到应用层，每经过一层，数据就会被加上一个头，然后被打包成最后的数据包在网络上传输；相对的，在接收方处就是一层层的把头去掉。<br>
那么，“栈”模式底层机制基本就是像下面这个样子：
![栈](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第五次作业/2.jpeg)
接收：对于收到的每个数据包，都从“A”点进来，经过路由判决，如果是发送给本机的就经过“B”点，然后往协议栈的上层继续传递；否则，如果该数据包的目的地是不本机，那么就经过“C”点，然后顺着“E”点将该包转发出去。<br>
发送：对于发送的每个数据包，首先也有一个路由判决，以确定该包是从哪个接口出去，然后经过“D”点，最后也是顺着“E”点将该包发送出去。<br>
所以Linux对于数据包有5个关键点，而Netfilter就是Linux从2.4.x引入的子系统。这是一个通用、抽象的过程，提供一整套的hook函数的管理机制，使得诸如数据包过滤、网络地址转换(NAT)和基于协议类型的连接跟踪成为了可能。Netfilter在内核中位置如下图所示：
![netfilter](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第五次作业/3.jpeg)
Netfilter通过在五个关键点挂载上一些拦截、处理函数，从而实现各种处理功能。
![netfilter](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第五次作业/4.jpeg)
<br>

使用iptables
---------------
1)拒绝来自某一特定IP地址的访问；<br>
```
pkusei@oo-lab:~$ ping 172.16.1.33
PING 172.16.1.33 (172.16.1.33) 56(84) bytes of data.
64 bytes from 172.16.1.33: icmp_seq=1 ttl=64 time=0.605 ms
64 bytes from 172.16.1.33: icmp_seq=2 ttl=64 time=0.426 ms
64 bytes from 172.16.1.33: icmp_seq=3 ttl=64 time=0.451 ms
64 bytes from 172.16.1.33: icmp_seq=4 ttl=64 time=0.380 ms
pkusei@oo-lab:~$ sudo iptables -A INPUT -s 10.2.67.113 -j REJECT
pkusei@oo-lab:~$ ping 172.16.1.33
PING 172.16.1.33 (172.16.1.33) 56(84) bytes of data.
--- 172.16.1.33 ping statistics ---
14 packets transmitted, 0 received, 100% packet loss, time 13104ms
```
```
pkusei@oo-lab:~$ ping 172.16.1.236
PING 172.16.1.236 (172.16.1.236) 56(84) bytes of data.
From 172.16.1.236 icmp_seq=1 Destination Port Unreachable
From 172.16.1.236 icmp_seq=2 Destination Port Unreachable
From 172.16.1.236 icmp_seq=3 Destination Port Unreachable
From 172.16.1.236 icmp_seq=4 Destination Port Unreachable
From 172.16.1.236 icmp_seq=5 Destination Port Unreachable
```
在1002机器上reject 1003的ip之后，ping就无法接收到数据了，同时在1003上ping1002已经unreachable<br>
```
pkusei@oo-lab:~$ sudo iptables -A INPUT -s 10.2.67.113 -j REJECT
```
删除该规则<br>
2）拒绝来自某一特定mac地址的访问；<br>
通过ifconfig -a中查看ens32得到1003的mac地址
```
pkusei@oo-lab:~$ sudo iptables -A INPUT -m mac --mac-source 02:00:1e:4c:00:03 -j REJECT
```
效果与之前一样<br>
3）只开放本机的http服务，其余协议与端口均拒绝；<br>
```
pkusei@oo-lab:~$ sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
pkusei@oo-lab:~$ sudo iptables -P INPUT DROP
```
完成后，ssh直接被断开，通过燕云查看iptables
```
pkusei@oo-lab:~$ sudo iptables -L INPUT --line-numbers
Chain INPUT (policy DROP)
num  target     prot opt source               destination         
1    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
```
恢复
```
pkusei@oo-lab:~$ sudo iptables -P INPUT ACCEPT
```
4）拒绝回应来自某一特定IP地址的ping命令。
<br>
```
pkusei@oo-lab:~$ sudo iptables -A INPUT -p icmp --icmp-type 8 -s 172.16.1.33 -j REJECT
```
此时1003无法ping 1002，反之1002可以ping 1003。<br>

Linux网络设备工作原理
---------------
### Bridge
Bridge是 Linux 上用来做 TCP/IP 二层协议交换的设备，与现实世界中的交换机功能相似。<br>
Bridge 设备实例可以和 Linux 上其他网络设备实例连接，即attach一个从设备，类似于在现实世界中的交换机和一个用户终端之间连接一根网线。当有数据到达时，Bridge会根据报文中的MAC信息进行广播、转发、丢弃处理。<br>
Bridge 的功能主要在内核里实现。当一个从设备被attach到Bridge上时，相当于现实世界里交换机的端口被插入了一根连有终端的网线。这时在内核程序里，netdev_rx_handler_register()被调用，一个用于接受数据的回调函数被注册。以后每当这个从设备收到数据时都会调用这个函数可以把数据转发到Bridge上。当 Bridge 接收到此数据时，br_handle_frame()被调用，进行一个和现实世界中的交换机类似的处理过程：判断包的类别（广播/单点），查找内部 MAC 端口映射表，定位目标端口号，将数据转发到目标端口或丢弃，自动更新内部 MAC 端口映射表以自我学习。<br>
Bridge 和现实世界中的二层交换机有一个区别，数据被直接发到 Bridge 上，而不是从一个端口接受。这种情况可以看做 Bridge 自己有一个 MAC 可以主动发送报文，或者说 Bridge 自带了一个隐藏端口和寄主 Linux 系统自动连接，Linux 上的程序可以直接从这个端口向 Bridge 上的其他端口发数据。所以当一个 Bridge 拥有一个网络设备时，如 bridge0 加入了 eth0 时，实际上 bridge0 拥有两个有效 MAC 地址，一个是 bridge0 的，一个是 eth0 的，他们之间可以通讯。由此带来一个有意思的事情是，Bridge 可以设置 IP 地址。通常来说 IP 地址是三层协议的内容，不应该出现在二层设备 Bridge 上。但是 Linux 里 Bridge 是通用网络设备抽象的一种，只要是网络设备就能够设定 IP 地址。当一个 bridge0 拥有 IP 后，Linux 便可以通过路由表或者 IP 表规则在三层定位 bridge0，此时相当于 Linux 拥有了另外一个隐藏的虚拟网卡和 Bridge 的隐藏端口相连，这个网卡就是名为 bridge0 的通用网络设备，IP 可以看成是这个网卡的。当有符合此 IP 的数据到达 bridge0 时，内核协议栈认为收到了一包目标为本机的数据，此时应用程序可以通过 Socket 接收到它。一个更好的对比例子是现实世界中的带路由的交换机设备，它也拥有一个隐藏的 MAC 地址，供设备中的三层协议处理程序和管理程序使用。设备里的三层协议处理程序，对应名为 bridge0 的通用网络设备的三层协议处理程序，即寄主 Linux 系统内核协议栈程序。设备里的管理程序，对应 bridge0 寄主 Linux 系统里的应用程序。<br>

Bridge 的实现当前有一个限制：当一个设备被 attach 到 Bridge 上时，那个设备的 IP 会变的无效，Linux 不再使用那个 IP 在三层接受数据。举例如下：如果 eth0 本来的 IP 是 192.168.1.2，此时如果收到一个目标地址是 192.168.1.2 的数据，Linux 的应用程序能通过 Socket 操作接受到它。而当 eth0 被 attach 到一个 bridge0 时，尽管 eth0 的 IP 还在，但应用程序是无法接受到上述数据的。此时应该把 IP 192.168.1.2 赋予 bridge0。<br>
另外需要注意的是数据流的方向。对于一个被 attach 到 Bridge 上的设备来说，只有它收到数据时，此包数据才会被转发到 Bridge 上，进而完成查表广播等后续操作。当请求是发送类型时，数据是不会被转发到 Bridge 上的，它会寻找下一个发送出口。用户在配置网络时经常忽略这一点从而造成网络故障。
![bridge](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第五次作业/2.1.jpeg)

### vlan

VLAN 又称虚拟网络，是一个被广泛使用的概念，有些应用程序把自己的内部网络也称为 VLAN。此处主要说的是在物理世界中存在的，需要协议支持的 VLAN。它的种类很多，按照协议原理一般分为：MACVLAN、802.1.q VLAN、802.1.qbg VLAN、802.1.qbh VLAN。其中出现较早，应用广泛并且比较成熟的是 802.1.q VLAN，其基本原理是在二层协议里插入额外的 VLAN 协议数据（称为 802.1.q VLAN Tag)，同时保持和传统二层设备的兼容性。Linux 里的 VLAN 设备是对 802.1.q 协议的一种内部软件实现，模拟现实世界中的 802.1.q 交换机。<br>
![vlan](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第五次作业/2.2.jpeg)
如图所示，Linux 里 802.1.q VLAN 设备是以母子关系成对出现的，母设备相当于现实世界中的交换机 TRUNK 口，用于连接上级网络，子设备相当于普通接口用于连接下级网络。当数据在母子设备间传递时，内核将会根据 802.1.q VLAN Tag 进行对应操作。母子设备之间是一对多的关系，一个母设备可以有多个子设备，一个子设备只有一个母设备。当一个子设备有一包数据需要发送时，数据将被加入 VLAN Tag 然后从母设备发送出去。当母设备收到一包数据时，它将会分析其中的 VLAN Tag，如果有对应的子设备存在，则把数据转发到那个子设备上并根据设置移除 VLAN Tag，否则丢弃该数据。在某些设置下，VLAN Tag 可以不被移除以满足某些监听程序的需要，如 DHCP 服务程序。举例说明如下：eth0 作为母设备创建一个 ID 为 100 的子设备 eth0.100。此时如果有程序要求从 eth0.100 发送一包数据，数据将被打上 VLAN 100 的 Tag 从 eth0 发送出去。如果 eth0 收到一包数据，VLAN Tag 是 100，数据将被转发到 eth0.100 上，并根据设置决定是否移除 VLAN Tag。如果 eth0 收到一包包含 VLAN Tag 101 的数据，其将被丢弃。上述过程隐含以下事实：对于寄主 Linux 系统来说，母设备只能用来收数据，子设备只能用来发送数据。和 Bridge 一样，母子设备的数据也是有方向的，子设备收到的数据不会进入母设备，同样母设备上请求发送的数据不会被转到子设备上。可以把 VLAN 母子设备作为一个整体想象为现实世界中的 802.1.q 交换机，下级接口通过子设备连接到寄主 Linux 系统网络里，上级接口同过主设备连接到上级网络，当母设备是物理网卡时上级网络是外界真实网络，当母设备是另外一个 Linux 虚拟网络设备时上级网络仍然是寄主 Linux 系统网络。<br>
需要注意的是母子 VLAN 设备拥有相同的 MAC 地址，可以把它当成现实世界中 802.1.q 交换机的 MAC，因此多个 VLAN 设备会共享一个 MAC。当一个母设备拥有多个 VLAN 子设备时，子设备之间是隔离的，不存在 Bridge 那样的交换转发关系，原因如下：802.1.q VLAN 协议的主要目的是从逻辑上隔离子网。现实世界中的 802.1.q 交换机存在多个 VLAN，每个 VLAN 拥有多个端口，同一 VLAN 端口之间可以交换转发，不同 VLAN 端口之间隔离，所以其包含两层功能：交换与隔离。Linux VLAN device 实现的是隔离功能，没有交换功能。一个 VLAN 母设备不可能拥有两个相同 ID 的 VLAN 子设备，因此也就不可能出现数据交换情况。如果想让一个 VLAN 里接多个设备，就需要交换功能。在 Linux 里 Bridge 专门实现交换功能，因此将 VLAN 子设备 attach 到一个 Bridge 上就能完成后续的交换功能。总结起来，Bridge 加 VLAN device 能在功能层面完整模拟现实世界里的 802.1.q 交换机。<br>
Linux 支持 VLAN 硬件加速，在安装有特定硬件情况下，图中所述内核处理过程可以被放到物理设备上完成。

### veth

VETH 设备出现较早，它的作用是反转通讯数据的方向，需要发送的数据会被转换成需要收到的数据重新送入内核网络层进行处理，从而间接的完成数据的注入。<br>
VETH 设备总是成对出现，送到一端请求发送的数据总是从另一端以请求接受的形式出现。该设备不能被用户程序直接操作，但使用起来比较简单。创建并配置正确后，向其一端输入数据，VETH 会改变数据的方向并将其送入内核网络核心，完成数据的注入。在另一端能读到此数据

Calico中数据包传输过程    
---------------

调研Weave
---------------


Mesos Framework
---------------
