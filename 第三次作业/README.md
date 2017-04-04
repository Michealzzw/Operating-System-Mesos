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
###运行：
      curl -fsSL https://get.docker.com/gpg | sudo apt-key add -
      sudo docker run hello-world
      sudo docker run -it ubuntu
安装完成后运行hello-world与ubuntu测试，结果如下
![Hello-world](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/0.png)
![Ubuntu](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/第三次作业/1.png)

介绍Docker五个命令
-------------
### Docker run
### Docker images
### Docker network
### Docker exec & attach
### Docker rmi

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
