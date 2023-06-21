import logging
import shlex
from subprocess import PIPE, Popen

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def syslog_listener(properties):
    log.debug('Function "syslog" launched with params %s: ' % properties)

    listen_port = properties['port']
    command = f'./syslog_udp_listener.sh'
    log.debug(command)
    (_, err) = Popen(shlex.split(command), shell=False, stdout=PIPE).communicate()
    if err:
        log.error(err)