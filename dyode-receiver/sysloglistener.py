import logging
import shlex
from subprocess import PIPE, Popen

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def syslog_listener(module, properties):
    log.debug('Function "syslog" launched with params %s: ' % properties)

    listen_port = properties['port']
    command = f'syslog_udp_listener -p {listen_port} -d {properties["out"]} -f {properties["filename"]}'
    log.debug(command)
    (_, err) = Popen(shlex.split(command), shell=False, stdout=PIPE).communicate()
    if err:
        log.error(err)