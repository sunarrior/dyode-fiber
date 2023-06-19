import datetime
import errno
import hashlib
import logging
import multiprocessing
from multiprocessing import Process, Popen, PIPE, Queue
import os
import random
import shlex
import shutil
# Imports
import string
import subprocess
import json

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def parse_manifest(file_path, in_path, out_path):
    log.debug("config file:" + file_path)
    files = []
    dirs = []
    with open(file_path, 'r') as config_file:
        try:
            data = json.load(config_file)
            files = data['files']
            dirs = data['dirs']
            if in_path != out_path:
                t = []
                for f in files:
                    t.append(out_path + os.path.relpath(f, in_path))
                files = t
                t = []
                for d in dirs:
                    t.append(out_path + os.path.relpath(d, in_path))
                dirs = t
        except:
            pass
    return dirs, files


def check_hash_process(queue):
    while True:
        temp_file, hash_list, success_log, failure_log = queue.get()
        if hash_list is None:
            if temp_file is None:
                break
            else:
                for the_file in os.listdir(temp_file):
                    file_path = os.path.join(temp_file, the_file)
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                continue
        h = hash_file(temp_file)
        if h not in hash_list:
            log.error('Invalid checksum for file ' + temp_file + " " + h)
            with open(failure_log, 'a') as f:
                f.write(bytes(h + ' ' + temp_file + '\n', 'utf-8'))
            os.remove(temp_file)
        else:
            f = hash_list[h]
            file_path = os.path.dirname(f)
            if not os.path.exists(file_path):
                try:
                    os.makedirs(file_path)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            shutil.move(temp_file, f)
            log.info('File Available: ' + f)
            with open(success_log, 'a') as file:
                file.write(bytes(h + ' ' + f + '\n', 'utf-8'))
    queue.put(None)


# File reception forever loop
def file_reception_loop(params):
    # background hash check
    queue = Queue()

    hash_p = Process(target=check_hash_process, args=(queue,))
    hash_p.daemon = True
    hash_p.start()

    while True:
        wait_for_file(queue, params)


# Launch UDPCast to receive a file
def receive_file(file_path, interface, ip_in, port_base, timeout=0):
    command = f'udp-receiver --nosync --mcast-rdv-addr {ip_in} \
              --interface {interface} --portbase {port_base} -f "{file_path}"'
    if timeout > 0:
        command = f'{command} --start-timeout {timeout} --receive-timeout {timeout}'
    log.debug(command)
    (output, err) = Popen(shlex.split(command), shell=False, stdout=PIPE,
                                     stderr=PIPE).communicate()
    if output:
        log.debug(output)
    if err:
        log.error(err)


# File reception function
def wait_for_file(queue, params):
    log.debug('Waiting for file ...')
    # Use a dedicated name for each process to prevent race conditions
    process_name = multiprocessing.current_process().name
    if not os.path.exists(params['temp']):
        os.mkdir(params['temp'])
    manifest_filename = params['temp'] + '/manifest_' + process_name + '.json'
    receive_file(manifest_filename, params['interface_out'], params['ip_in'], int(
        params['port']) + 2)
    dirs, files = parse_manifest(
        manifest_filename, params['in'], params['out'] + '/')
    if len(files) == 0:
        log.error('No file listed in manifest')
        return 0
    log.debug('Manifest content : %s' % files)

    hash_list = dict()
    for f, h in files:
        hash_list[h] = f

    for f, h in files:
        # filename = os.path.basename(f)
        # mkdir on the fly
        temp_file = params['temp'] + '/' + ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
        receive_file(temp_file, params['interface_out'],
                     params['ip_in'], params['port'], params['timeout'])
        log.info('File ' + temp_file + ' received at ' +
                 str(datetime.datetime.now()))
        if os.path.exists(temp_file):
            queue.put((temp_file, hash_list,
                       params['out'] + '/transfer_success.log',
                       params['out'] + '/transfer_failure.log'))

    os.remove(manifest_filename)
    queue.put((params['temp'], None, None, None))

########################### Shared functions ###################################

def hash_file(file):
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)

    return hasher.hexdigest()
