import logging
from multiprocessing import Process
import yaml

import filereceiver
import screenreceiver
import sysloglistener

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def launch_agents(module, properties):
    if properties['type'] == 'filereceiver':
        log.debug(f'Instanciating a file transfer module :: ${module}')
        filereceiver.file_reception_loop(properties)
    elif properties['type'] == 'screen':
        log.debug(f'Screen sharing : ${module}')
        screen_process = Process(name='http_server', target=screenreceiver.http_server,
                                                 args=(module, properties))
        screen_process.start()
    elif properties['type'] == 'syslog':
        log.debug(f'Syslog listener: ${module}')
        syslog_process = Process(name='syslog_listener', target=sysloglistener.syslog_listener,
                                                 args=(module, properties))
        syslog_process.start()

if __name__ == '__main__':
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Log infos about the configuration file
    log.info(f'Configuration name : {config["config_name"]}')
    log.info(f'Configuration version : {config["config_version"]}')
    log.info(f'Configuration date : {config["config_date"]}')

    # Iterate on modules
    modules = config.get('modules')
    for module, properties in modules.items():
        properties['ip_in'] = config['dyode_sender']['ip']
        properties['interface_out'] = config['dyode_receiver']['interface']
        log.debug(f'Parsing {module}')
        log.debug(f'Trying to launch a new process for module {module}')
        p = Process(name=str(module), target=launch_agents, args=(module, properties))
        p.start()
