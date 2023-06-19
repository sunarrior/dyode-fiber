import logging
import multiprocessing
import pyinotify
# import shlex
# from subprocess import Popen, PIPE
import yaml

import filetransfer

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Default max bitrate
max_bitrate = 100


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        log.info(f'New file detected :: {event.pathname}')
        # If a new file is detected, launch the copy
        filetransfer.file_copy(multiprocessing.current_process()._args)


# When a new file finished copying in the input folder, send it
def watch_folder(properties):
    # inotify kernel watchdog
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE
    notifier = pyinotify.AsyncNotifier(wm, EventHandler())
    wdd = wm.add_watch(properties['in'], mask, rec=True, auto_add=True)
    log.debug(f'watching :: {properties["in"]}')
    notifier.loop()


def launch_agents(module, properties):
    if properties['type'] == 'filetransfer':
        log.debug(f'Instanciating a file transfer module :: {module}')
        watch_folder(properties)


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
    # output, err = Popen(
    #     shlex.split(
    #         'arp -s ' + config['dyode_receiver']['ip'] + ' ' + config['dyode_receiver']['mac']),
    #     shell=False, stdout=PIPE, stderr=PIPE).communicate()
    # if output:
    #     log.debug(output)
    # if err:
    #     log.error(err)

    modules_quantity = len((config['modules']))
    log.debug(f'Number of modules : {modules_quantity}')

    # Get modules config
    modules = config.get('modules')

    # Check if any modules have no bitrate config
    modules_without_bitrate = 0
    for module, properties in modules.items():
        if 'bitrate' in properties:
            max_bitrate = max_bitrate - properties['bitrate']
        else:
            modules_without_bitrate = modules_without_bitrate + 1
    if max_bitrate < 0:
        log.error('Sum of bitrate is bigger than the maximum defined !')
        exit(1)

    # Iterate on modules
    for module, properties in modules.items():
        properties['ip_out'] = config['dyode_receiver']['ip']
        properties['interface_in'] = config['dyode_sender']['interface']
        if 'bitrate' not in properties:
            properties['bitrate'] = max_bitrate // modules_without_bitrate
        log.debug(f'Parsing {module}')
        log.debug(f'Trying to launch a new process for module {module}')
        p = multiprocessing.Process(
            name=str(module), target=launch_agents, args=(module, properties))
        p.start()
