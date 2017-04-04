第三次作业报告
================
郑子威 1300012711 信息科学技术学院

Assignment
--------------
安装配置Docker。
<br>
查阅相关资料及docker相关文档，介绍docker基本命令(如run,images,network等)，要求至少包含镜像管理，容器管理，网络管理三部分的命令，至少介绍5个不同的命令，尽量完整的介绍命令，包括命令的含义和其用法，例子。<br>
<br>
创建一个基础镜像为ubuntu的docker镜像，随后再其中加入nginx服务器，之后启动nginx服务器并利用tail命令将访问日志输出到标准输出流。要求该镜像中的web服务器主页显示自己编辑的内容，编辑的内容包含学号和姓名。之后创建一个自己定义的network，模式为bridge，并让自己配的web服务器容器连到这一网络中。要求容器所在宿主机可以访问这个web服务器搭的网站。请在报告中详细阐述搭建的过程和结果。<br>
<br>
尝试让docker容器分别加入四个不同的网络模式:null,bridge,host,overlay。请查阅相关资料和docker文档，阐述这些网络模式的区别。<br>
<br>
阅读mesos中负责与docker交互的代码，谈谈mesos是怎样与docker进行交互的，并介绍docker类中run函数大致做了什么。<br>
<br>
写一个framework，以容器的方式运行task，运行前面保存的nginx服务器镜像，网络为HOST，运行后，外部主机可以通过访问宿主ip+80端口来访问这个服务器搭建的网站，网站内容包含学号和姓名。报告中对源码进行说明，并附上源码和运行的相关截图。<br>

安装配置Docker
--------------
### 运行：
      curl -fsSL https://get.docker.com/gpg | sudo apt-key add -
      sudo docker run hello-world
      sudo docker run -it ubuntu
安装完成后运行hello-world与ubuntu测试，结果如下
![Hello-world](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/0.png)
![Ubuntu](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/1.png)

介绍Docker五个命令
-------------
### Docker run
      docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
      OPTIONS:
        -a stdin: 指定标准输入输出内容类型，可选 STDIN/STDOUT/STDERR 三项；
        -d: 后台运行容器，并返回容器ID；
        -i: 以交互模式运行容器，通常与 -t 同时使用；
        -t: 为容器重新分配一个伪输入终端，通常与 -i 同时使用；
        --name="nginx-lb": 为容器指定一个名称；
        --dns 8.8.8.8: 指定容器使用的DNS服务器，默认和宿主一致；
        --dns-search example.com: 指定容器DNS搜索域名，默认和宿主一致；
        -h "mars": 指定容器的hostname；
        -e username="ritchie": 设置环境变量；
        --env-file=[]: 从指定文件读入环境变量；
        --cpuset="0-2" or --cpuset="0,1,2": 绑定容器到指定CPU运行；
        -m :设置容器使用内存最大值；
        --net="bridge": 指定容器的网络连接类型，支持 bridge/host/none/container: 四种类型；
        --link=[]: 添加链接到另一个容器；
        --expose=[]: 开放一个端口或一组端口；
docker用于运行镜像的命令，会新建一个容器并在该容器上运行镜像，对于没有分配名字的container，run会自动分配一个名字（不能创建与运行中container名字相同的container），如上面的helloworld和下面的多个ubuntu。使用-itd为了让其生成一个后台运行的bash，使得不是建立后直接消亡。
![RUN](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/2.png)

### Docker images
      docker images [OPTIONS] [REPOSITORY[:TAG]]
      OPTIONS:
        -a :列出本地所有的镜像（含中间映像层，默认情况下，过滤掉中间映像层）；
        --digests :显示镜像的摘要信息；
        -f :显示满足条件的镜像；
        --format :指定返回值的模板文件；
        --no-trunc :显示完整的镜像信息；
        -q :只显示镜像ID。
docker用于查看本地镜像的命令，实例：
![RUN](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/3.png)
### Docker network
      docker network [COMMAND] [...]
      COMMANG:
      ls : 列出本地所有network，初始默认包含三个网络null, host ,bridge，不可以被rm掉
      inspect : 查看network信息或者一个container对应的网络信息等等，后面跟网络名或者--format设置返回信息与格式
      disconnect [network] [container] : 从一个network中disconnect一个container
      connect [network] [container] : 把一个container连接到一个network
      create -d [network type] [network name] : 新建一个网络，设置网络类型与网络名
      prune : 移除无用network
      rm : 移除network
docker用于管理network的重要命令，实例：
![RUN](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/4.png)
### Docker exec & attach
      docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
      OPTIONS:
        -d :分离模式: 在后台运行
        -i :即使没有附加也保持STDIN 打开
        -t :分配一个伪终端
docker进入容器进行操作的重要操作，类似ssh但是不需要开启sshd，更安全。一般使用 -it<br>
类似的有attach命令，但是attach，但是attach使用Ctrl-c推出后container也停止运行

### Docker rmi
docker rmi [OPTIONS] IMAGE [IMAGE...]
OPTIONS：
  -f :强制删除；
  --no-prune :不移除该镜像的过程镜像，默认移除；
管理镜像的命令

构建nginx镜像my-nginx-web
-------------


网络模式
-------------
### bridge
### null
### host
### overlay

Mesos与Docker的交互
-------------

在Mesos上运行my-nginx-web
-------------
