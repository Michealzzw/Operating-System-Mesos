第一次作业报告
郑子威 1300012711 信息科学技术学院


了解虚拟机和容器技术，用自己的话简单叙述、总结并对比

    容器和虚拟机之间的差别主要在于操作系统资源的使用方式与虚拟化层的位置。
    对于虚拟化层的区别在于，虚拟机是独立的操作系统，而容器是构建在主机操作系统之上的容器层。
    对于操作系统资源而言，虚拟机与虚拟机之间是完全隔离的，每个虚拟机自身也可以认为是一种操作系统，直接从计算资源中分配实例；而容器则是由主机操作系统来进行分配，容器之间共享一个操作系统。因此，相对于资源使用效率而言，容器高于虚拟机；而虚拟机则更为独立，更容易迁移，两种技术互补。


运行Spark on Mesos(说明)，以不同并行度运行两次wordcount程序并比较，需要在报告中详细说明并附资源使用情况及时间花费截图

    运行Python版本的WordCount。
    分别运行core=1，2，4的程序
    为了有所比较，读较大的文件（300MB）
    CPUs: 4
    Mem:  1.4GB
    core4: 81s
    core2: 83s
    core1: 73s


叙述自己对这些软件技术与具体安装运行过程的看法，对于觉得存在问题的地方可以自己查阅资料或咨询助教

    通过安装，出现问题与解决问题，对mesos与spark的整个框架有了初步的了解
    运行在mesos上面和 spark standalone模式的区别是：
      1）stand alone
      需要自己启动spark master
      需要自己启动spark slaver（即工作的worker）
      2）运行在mesos
      启动mesos master
      启动mesos slaver
      启动spark的 ./sbin/start-mesos-dispatcher.sh -m mesos://127.0.0.1:5050
      配置spark的可执行程序的路径(也就是mesos里面所谓EXECUTOR)，提供给mesos下载运行。

      在mesos上面的运行流程：
      1）通过spark-submit提交任务到spark-mesos-dispatcher
      2）spark-mesos-dispatcher 把通过driver 提交到mesos master，并收到任务ID
      3）mesos master 分配到slaver 让它执行任务
      4) spark-mesos-dispatcher，通过任务ID查询任务状态


    出现的问题：
    1. Download出问题
      log: curl: (22) The requested URL returned error: 404 Not Found
      Error: Failed to download resource "readline--patch"
      Download failed: https://gist.githubusercontent.com/jacknagel/d886531fb6623b60b2af/raw/746fc543e56bc37a26ccf05d2946a45176b0894e/readline-6.3.8.diff
    解决：通过查询发现原因在于homebrew不是最新版本，update即可
    2. Permission
      log: You should probably change the ownership and permissions of /usr/local back to your user account.
      解决：homebrew 在sudo模式下不安全，但是默认的workpath需要权限，因此修改workpath的归属
      sudo chown -R $(whoami):admin /usr/local
    3.spark的example无法重新编译，也就无法添加conf
      解决：下载learningsparkexamples或者使用python，最后使用python，并且添加代码：
              spark = SparkSession\
            .builder\
            .master("mesos://127.0.0.1:5050")\
            .config("spark.executor.uri", "http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz")\
            .appName("PythonWordCount")\
            .getOrCreate()
    4.mac系统下找不到libmesos.so
    解决：官网上说明mac下应该是libmesos.dylib，但是却不在那个目录，通过find找到在build下的lib中
