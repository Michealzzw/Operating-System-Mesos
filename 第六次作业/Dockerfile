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
