import logging
import multiprocessing
import os
import shlex
from subprocess import Popen, PIPE
import yaml

import filetransfer
import screenlistener
import screensharing
import syslogforwarding

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Default max bitrate
max_bitrate = 300

def launch_agents(module, properties):
    if properties['type'] == 'filetransfer':
        log.debug(f'Instanciating a file transfer module :: {module}')
        filetransfer.watch_folder(properties)
    elif properties['type'] == 'screen_listener':
        log.debug(f'Screen listener agent : ${module}')
        screenlistener.screen_listener(module, properties)
    elif properties['type'] == 'screen':
        log.debug(f'Screen sharing agent : ${module}')
        screensharing.watch_folder(module, properties)
    elif properties['type'] == 'syslog':
        log.debug(f'Syslog forwarding agent : ${module}')
        syslogforwarding.syslog_forwarding(properties)


if __name__ == '__main__':
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Log infos about the configuration file
    log.info(f'Configuration name : {config["config_name"]}')
    log.info(f'Configuration version : {config["config_version"]}')
    log.info(f'Configuration date : {config["config_date"]}')

    # Initial max bitrate
    if 'bitrate' in config:
        max_bitrate = config['max_bitrate']

    # Set static ARP
    (_, err) = Popen(
        shlex.split(
            f'arp -s {config["dyode_receiver"]["ip"]} {config["dyode_receiver"]["mac"]}'),
        shell=False, stdout=PIPE).communicate()
    if err:
        log.error(err)

    modules_quantity = len((config['modules']))
    log.debug(f'Number of modules : {modules_quantity}')

    # Get modules config
    modules = config.get('modules')

    # Iterate on modules
    for module, properties in modules.items():
        properties['ip_out'] = config['dyode_receiver']['ip']
        properties['interface_in'] = config['dyode_sender']['interface']
        if properties.get('in') and not os.path.exists(properties['in']):
            os.makedirs(properties['in'])
        if properties.get('temp') and not os.path.exists(properties['temp']):
            os.makedirs(properties['temp'])
        log.debug(f'Trying to launch a new process for module {module}')
        p = multiprocessing.Process(
            name=str(module), target=launch_agents, args=(module, properties))
        p.start()
1