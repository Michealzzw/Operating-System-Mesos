#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import uuid
import time
import socket
import signal
import getpass
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data, decode_data
from addict import Dict

TASK_CPU = 0.1
TASK_MEM = 32


class MinimalScheduler(Scheduler):
    
    def __init__(self):
        self.nginx_on = False;
    nginx_on = False;

    def resourceOffers(self, driver, offers):
        if self.nginx_on:
            return
        filters = {'refuse_seconds': 5}
        for offer in offers:
            if self.nginx_on:
                break
            cpus = self.getResource(offer.resources, 'cpus')
            mem = self.getResource(offer.resources, 'mem')
            if cpus < TASK_CPU or mem < TASK_MEM:
                continue



            DockerInfo = Dict() 
            DockerInfo.image = 'my-docker-nginx'
            DockerInfo.network = 'HOST'

            ContainerInfo = Dict();
            ContainerInfo.type = 'DOCKER';
            ContainerInfo.docker = DockerInfo;


#            DockerInfo.arguments = ['-p','10080:80'];
            
            CommandInfo = Dict();
            CommandInfo.shell = False;
            self.nginx_on = True;

            task = Dict()
            task_id = str(uuid.uuid4())
            task.task_id.value = task_id
            task.agent_id.value = offer.agent_id.value
            task.name = 'mynginx'

            task.container = ContainerInfo;
            task.command = CommandInfo;
            task.resources = [
                dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
                dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
            ]
            

            driver.launchTasks(offer.id, [task], filters)

    def getResource(self, res, name):
        for r in res:
            if r.name == name:
                return r.scalar.value
        return 0.0

    def statusUpdate(self, driver, update):
        logging.debug('Status update TID %s %s',
                      update.task_id.value,
                      update.state)
		     


def main(master):
    framework = Dict()
    framework.user = getpass.getuser()
    framework.name = "mynginx"
    framework.hostname = socket.gethostname()

    driver = MesosSchedulerDriver(
        MinimalScheduler(),
        framework,
        master,
        use_addict=True,
    )

    def signal_handler(signal, frame):
        driver.stop()

    def run_driver_thread():
        driver.run()

    driver_thread = Thread(target=run_driver_thread, args=())
    driver_thread.start()

    print('Scheduler running, Ctrl+C to quit.')
    signal.signal(signal.SIGINT, signal_handler)

    while driver_thread.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2:
        print("Usage: {} <mesos_master>".format(sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1])
