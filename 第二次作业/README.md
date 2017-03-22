第二次作业报告
郑子威 1300012711 信息科学技术学院


用自己的语言描述Mesos的组成结构，指出它们在源码中的具体位置，简单描述一下它们的工作流程

    Apache Mesos由四个组件组成，分别是master，slave，framework和executor。

    master:
      是系统的核心，负责管理接入mesos的各个framework（由frameworks_manager管理）和slave（由slaves_manager管理），并将slave上的资源按照某种策略分配给framework（由独立插拔模块Allocator管理）。
      Code:
      master: src/master/master.cpp
      Allocator: src/master/allocator/allocator.cpp

    slave:
      负责接收并执行来自master的命令、管理节点上的task，并为各个task分配资源。
      slave将自己的资源量发送给master，由master中的Allocator模块决定将资源（CPU和内存）分配给哪个framework。
      slave会将CPU个数和内存量发送给master，而用户提交作业时，需要指定每个任务需要的CPU个数和内存量，这样，当任务运行时，slave会将任务放到包含固定资源的container中运行，以达到资源隔离的效果。

    Framework:
      是指外部的计算框架，如Hadoop，Mesos等，这些计算框架可通过注册(master::register)的方式接入mesos，以便mesos进行统一管理和资源分配。Mesos要求可接入的框架必须有一个调度器模块，该调度器负责框架内部的任务调度。当一个framework想要接入mesos时，需要修改自己的调度器，以便向mesos注册，并获取mesos分配给自己的资源， 这样再由自己的调度器将这些资源分配给框架中的任务，也就是说，整个mesos系统采用了双层调度框架：第一层，由mesos将资源分配给框架；第二层，框架自己的调度器将资源分配给自己内部的任务。

    Executor:
      主要用于启动框架内部的task。由于不同的框架，启动task的接口或者方式不同，当一个新的框架要接入mesos时，需要编写一个executor，告诉mesos如何启动该框架中的task。


用自己的语言描述框架（如Spark On Mesos）在Mesos上的运行过程，并与在传统操作系统上运行程序进行对比

    Spark On Mesos是一个双层调度的运行过程，框架（spark）通过注册获取mesos分配给自己的资源，然后再由自己的调度器将这些资源分配给框架中的任务。
    在mesos上面的运行流程：
    1）通过spark-submit提交任务到spark-mesos-dispatcher
    2）spark-mesos-dispatcher 把通过driver 提交到mesos master，并收到任务ID
    3）mesos master 分配到slaver 让它执行任务
    4) spark-mesos-dispatcher，通过任务ID查询任务状态

    而传统的操作系统由进程调度器统一调度（分配资源+分配时间片）



叙述master和slave的初始化过程

    master 初始化过程
    （src/master/master.cpp）
    （void Master::initialize()）
    1. 检查各项运行参数
    2. 检查authenticate等
    3. 初始化role，设置weight  （from line 649）
    4. 初始化allocator （from line 707）
    5. 然后开启各种监听函数，设置route

    slave 初始化过程
    （src/slave/slave.cpp）
    （void Master::initialize()）
    1. 检查进程组相关信息以及是否已经创建某个agent
    2. 检查authenticate等
    3. 初始化资源预估器（from line 429）
    4. 初始化attributes
    5. 初始化hostname
    6. 初始化statusUpdateManager
    7. 注册一系列处理函数。



查找资料，简述Mesos的资源调度算法，指出在源代码中的具体位置并阅读，说说你对它的看法



    Mesos中的调度机制被称为“Resource Offer”，采用了基于资源量的调度机制，这不同于Hadoop中的基于slot的机制。在mesos中，slave直接将资源量（CPU和内存）汇报给master，由master将资源量按照某种机制分配给framework，其中，“某种机制”是“Dominant Resource Fairness（DRF）”

    对于类似mesos采用双层调度框架的系统，在设计时，需要解决以下问题：“Mesos在不知道各个framework资源需求的情况下，如何满足其需求？”，更具体一些，“Mesos在不知道framework中哪些数据存放在哪些节点情况下，如何做到数据locality？”为了解决该问题，mesos提供了“reject offer”机制，允许framework暂时拒绝不满足其资源需求的slave，在此，mesos采用了类似于Hadoop中的“delay scheduling“调度机制。

    在mesos中，作业调度是一个分布式的过程，当出现失败情况时，需要表现出一定的高效性和鲁棒性。为此，mesos提供了以下机制：

    （1）filters机制。 每次调度过程，mesos-master需要与framework-scheduler进行通信，如果有些framework总是拒绝slave，那么由于额外的通信开销会使得调度性能低效。为此避免不必要的通信，mesos提供了filters机制，允许framework只接收“剩余资源量大于L的slave”或者“只接收node列表中的slave”。

    （2）rescinds机制。如果某个framework在一定的时间内没有为分配的资源返回对应的任务，则mesos会回收其资源量，并将这些资源分配给其他framework。


    Dominant Resource Fairness（DRF）

      DRF是一种支持多资源的max-min fair 资源分配机制，其中max表示max{CPU,mem}，而min表示min{user1,user2,…}=min{max{CPU1,mem1}, max{CPU2,mem2}, …}，其中user代表mesos中的framework，算法伪代码如下图所示：

      ![DRF](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/%E7%AC%AC%E4%BA%8C%E6%AC%A1%E4%BD%9C%E4%B8%9A/DRF.png)

      举例说明，假设系统中共有9 CPUs 和18 GB RAM，有两个user（framework）分别运行了两种任务，分别需要的资源量为<1 CPU, 4 GB> 和 <3 CPUs, 1 GB>。对于用户A，每个task要消耗总CPU的1/9和总内存的2/9，因而A的支配性资源为内存；对于用户B，每个task要消耗总CPU的1/3和总内存的1/18，因而B的支配性资源为CPU。DRF将均衡所有用户的支配性资源，即：A获取的资源量为：<3 CPUs，12 GB>，可运行3个task；而B获取的资源量为<6 CPUs, 2GB>，可运行2个task，这样分配，每个用户获取了相同比例的支配性资源，即：A获取了2/3的RAMs，B获取了2/3的CPUs。

      DRF算法的一个可能的调度序列如下图所示：

      ![DRF](https://github.com/Michealzzw/Operating-System-Mesos/raw/master/%E7%AC%AC%E4%BA%8C%E6%AC%A1%E4%BD%9C%E4%B8%9A/DRF2.png)


    Mesos调度问题

      Mesos采用了Resource Offer机制，这种调度机制面临着资源碎片问题，即：每个节点上的资源不可能全部被分配完，剩下的一点可能不足以让任何任务运行，这样，便产生了类似于操作系统中的内存碎片问题。

写一个完成简单工作的框架(语言自选，需要同时实现scheduler和executor)并在Mesos上运行，在报告中对源码进行说明并附上源码，本次作业分数50%在于本项的完成情况、创意与实用程度。（后面的参考资料一定要读，降低大量难度）

    实现任务：统计素数个数
    使用PyMesos项目
    Code：Scheduler
      1 #!/usr/bin/env python2.7
      2 from __future__ import print_function
      3
      4 import sys
      5 import time
      6 import math
      7 from threading import Thread
      8
      9 from pymesos import MesosExecutorDriver, Executor, decode_data
      10 from addict import Dict
      11
      12
      13 class MinimalExecutor(Executor):
      14     def launchTask(self, driver, task):
      15         def run_task(task):
      16             update = Dict()
      17             update.task_id.value = task.task_id.value
      18             update.state = 'TASK_RUNNING'
      19             update.timestamp = time.time()
      20             driver.sendStatusUpdate(update)
      21             start = int(decode_data(task.data).split(' ')[0])
      22             end = int(decode_data(task.data).split(' ')[1])
      23             primeNum = 0
      24             for i in range(start,end):
      25                 flag = True
      26                 for j in range(2, int(math.sqrt(i))):
      27                     if (i % j == 0):
      28                         flag = False
      29                         break
      30                 if flag:
      31                     primeNum = primeNum+1
      32
      33             driver.sendFrameworkMessage(encode_data(str(primeNum)))
      34             update = Dict()
      35             update.task_id.value = task.task_id.value
      36             update.state = 'TASK_FINISHED'
      37             update.timestamp = time.time()
      38             driver.sendStatusUpdate(update)
      39
      40         thread = Thread(target=run_task, args=(task,))
      41         thread.start()
      42
      43
      44 if __name__ == '__main__':
      45     import logging
      46     logging.basicConfig(level=logging.DEBUG)
      47     driver = MesosExecutorDriver(MinimalExecutor(), use_addict=True)
      48     driver.run()

    Code: Scheduler
      1 #!/usr/bin/env python2.7
      2 from __future__ import print_function
      3
      4 import sys
      5 import uuid
      6 import time
      7 import socket
      8 import signal
      9 import getpass
      10 from threading import Thread
      11 from os.path import abspath, join, dirname
      12
      13 from pymesos import MesosSchedulerDriver, Scheduler, encode_data
      14 from addict import Dict
      15
      16 TASK_CPU = 0.1
      17 TASK_MEM = 32
      18 EXECUTOR_CPUS = 0.1
      19 EXECUTOR_MEM = 32
      20
      21
      22 class MinimalScheduler(Scheduler):
      23
      24     primeNum = 0;
      25     taskNum = 5;
      26     taskDone = 0;
      27     nowTaskID = 0;
      28     maxNum = 10;
      29     block = maxNum / taskNum;
      30
      31     def __init__(self, executor):
      32         self.executor = executor
      33     
      34     def frameworkMessage(self, driver, executorId, slaveId, message):
      35         self.taskDone = self.taskDone+1;
      36         start = int(decode_data(message).split(' ')[0])
      37         end = int(decode_data(message).split(' ')[1])
      38         primeNum = int(decode_data(message).split(' ')[2])
      39         self.primeNum = self.primeNum + primeNum
      40         print('From %s to %s, Prime Number is %s'%(start,end,primeNum))
      41         if self.taskDone >= self.taskDone:
      42             print('From 2 to %s, Prime Number is %s', self.maxNum, self.primeNum)
      43             driver.stop()
      44
      45     def resourceOffers(self, driver, offers):
      46         if self.nowTaskID >= self.taskNum:
      47             return
      48         filters = {'refuse_seconds': 5}
      49         for offer in offers:
      50             if self.nowTaskID >= self.taskNum:
      51                 break
      52             cpus = self.getResource(offer.resources, 'cpus')
      53             mem = self.getResource(offer.resources, 'mem')
      54             if cpus < TASK_CPU or mem < TASK_MEM:
      55                 continue
      56
      57             task = Dict()
      58             task_id = str(uuid.uuid4())
      59             task.task_id.value = task_id
      60             task.agent_id.value = offer.agent_id.value
      61             task.name = 'task {}'.format(task_id)
      62             task.executor = self.executor
      63
      64
      65             start = self.nowTaskID*self.block+2
      66             end = (self.nowTaskID+1)*self.block+2
      67             if end > self.maxNum+1:
      68                 end = self.maxNum+1
      69             task.data = encode_data(str(start)+' '+str(end))
      70
      71             task.resources = [
      72                 dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
      73                 dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
      74             ]
      75             print('Task %s start from %s to %s'%(self.nowTaskID, start, end))
      76             self.nowTaskID = self.nowTaskID + 1
      77             driver.launchTasks(offer.id, [task], filters)
      78
      79     def getResource(self, res, name):
      80         for r in res:
      81             if r.name == name:
      82                 return r.scalar.value
      83         return 0.0
      84
      85     def statusUpdate(self, driver, update):
      86         logging.debug('Status update TID %s %s',
      87                       update.task_id.value,
      88                       update.state)
      89
      90
      91
      92 def main(master):
      93     executor = Dict()
      94     executor.executor_id.value = 'MinimalExecutor'
      95     executor.name = executor.executor_id.value
      96     executor.command.value = '%s %s' % (
      97         sys.executable,
      98         abspath(join(dirname(__file__), 'executor.py'))
      99     )
      100     executor.resources = [
      101         dict(name='mem', type='SCALAR', scalar={'value': EXECUTOR_MEM}),
      102         dict(name='cpus', type='SCALAR', scalar={'value': EXECUTOR_CPUS}),
      103     ]
      104
      105     framework = Dict()
      106     framework.user = getpass.getuser()
      107     framework.name = "MinimalFramework"
      108     framework.hostname = socket.gethostname()
      109
      110     driver = MesosSchedulerDriver(
      111         MinimalScheduler(executor),
      112         framework,
      113         master,
      114         use_addict=True,
      115     )
      116
      117     def signal_handler(signal, frame):
      118         driver.stop()
      119
      120     def run_driver_thread():
      121         driver.run()
      122
      123     driver_thread = Thread(target=run_driver_thread, args=())
      124     driver_thread.start()
      125
      126     print('Scheduler running, Ctrl+C to quit.')
      127     signal.signal(signal.SIGINT, signal_handler)
      128
      129     while driver_thread.is_alive():
      130         time.sleep(1)
      131
      132
      133 if __name__ == '__main__':
      134     import logging
      135     logging.basicConfig(level=logging.DEBUG)
      136     if len(sys.argv) != 2:
      137         print("Usage: {} <mesos_master>".format(sys.argv[0]))
      138         sys.exit(1)
      139     else:
      140         main(sys.argv[1])
