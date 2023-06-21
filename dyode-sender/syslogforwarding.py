import logging
import shlex
from subprocess import PIPE, Popen

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def syslog_forwarding(properties):
    log.debug('Function "syslog" launched with params %s: ' % properties)

    listen_port = properties['port']
    send_port = properties['port']
    command = f'udp-redirect -r ${properties["listen_ip"]}:${listen_port} \
                              -d ${properties["ip_out"]}:${send_port}'
    log.debug(command)
    (_, err) = Popen(shlex.split(command), shell=False, stdout=PIPE).communicate()
    if err:
        log.error(err)
