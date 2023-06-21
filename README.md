# **DYODE FIBER**

This project base on repository: 
1. [amirhakh - dyode-half-fiber](https://github.com/amirhakh/data-diode/tree/master/dyode-half-fiber)
2. [wavestone-cdt - dyode](https://github.com/wavestone-cdt/dyode/tree/master/DYODE%20v1%20(full))


## **Hardware setup**
> 2 Computer with vmware\
> 3 Media converters (MC100CM)\
> 2 Fiber cable\
> 2 Ethernet cable\
> 2 USB LAN

## **VMWare setup**
> 40GB Storage \
> 4GB Ram
> Change USB config to type 3.1 (to working with USB to LAN)

## **Enviroment setup**
> Python 3.10.4 \
> Ubuntu 22.04 \
> Static ip highside: 172.10.0.1/30 \
> Static ip lowside: 172.10.0.2/30

## **Installation dependencies**
```shell
sudo apt install udpcast
sudo apt install scrot -y # only for highside
sudo apt install tcl-udp -y # only for lowside
sudo pip install -r requirement.txt
```

## **Build udp-redirect**
> I take udp-redirect sources from amirhakh. Thanks **Ivan Tikhonov** and **Amir Haji Ali Khamseh'i** for this wonderfull works!
```shell
cd udpcast
gcc -o udp-redirect udp-redirect.c
```

## **Setup rsyslog**
Setup rsyslog to throw all log to locahost port 514
```shell
sudo nano /etc/rsyslog.d/50-default.conf
```

Add line below

```nano
...
*.*;auth,authpriv.none          -/var/log/syslog
*.*                             @127.0.0.1:514 <--- add this line
#cron.*                         /var/log/cron.log
#daemon.*                       -/var/log/daemon.log
...
```

Restart rsyslog service
```shell
sudo service rsyslog restart
```

## **Increase net.core.rmem_max and net.core.rmem_default**
> From [amirhakh](https://github.com/amirhakh/data-diode/blob/master/dyode-half-fiber/README.md) and [udpcast](http://www.udpcast.linux.lu/cmd.html) advice, it better to play around with rmem_max and rmem_default kernel parameter to have more IP packet buffer to avoid packet drop

## **Do before start program**
1. Run screenshot.sh if you want to use screen sharing
2. Create folder dyode, temp, screen on highsde
3. Create folder dyode, temp, syslog on lowside

## **NOTE**
1. Set static arp need sudo permission to be worked. It not working in python code when run on python command from terminal, so I temporary create set_static_arp.sh to do it by manual. It may work without sudo when we put program to linux service.
2. udp-redirect build, syslog_udp_listener.sh also need sudo to be worked
## **Feature**
1. File transfer (testing on 1GB file)
2. Screen sharing (1 frame/s)
3. Syslog forwarding

## **TODO**
- Testing full feature as service
- Auto create folder if not exists
- Optimize code and shell script

## **Troubleshoting**
1. Installing wireshark to monitor network flow on both machine
```shell
sudo apt install wireshark
```

1. Error **"Can't bind our address..."**:
- Using netstat to check if there are any services using port 514
```shell
netstat -ano | grep 514
```
- Find it PID by ps command and kill it
```shell
ps -ef | grep something
kill $PID
```