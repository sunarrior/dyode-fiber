import datetime
import hashlib
import logging
import os
import subprocess
import time
import json

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# List all files recursively
def list_all_files(root_dir):
    files = []
    dirs = []
    for root, directories, filenames in os.walk(root_dir):
        for directory in directories:
            dirs.append(os.path.join(root, directory))
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return dirs, files

def write_manifest(dirs, files, files_hash, manifest_filename, root, new):
    data = {'dirs': [d.replace(root, new, 1) for d in dirs], 'files': []}
    log.debug([d.replace(root, new, 1) for d in dirs])
    for f in files:
        data['files'].append([f.replace(root, new, 1), files_hash[f]])
        log.debug(f + ' :: ' + files_hash[f])

    with open(manifest_filename, 'wb') as configfile:
        json.dump(data, configfile)

# Send a file using udpcast
def send_file(file_path, interface, ip_out, port_base, max_bitrate):
    command = f'udp-sender --async --fec 4x4 --max-bitrate {max_bitrate}m \
                --mcast-rdv-addr {ip_out} --mcast-data-addr {ip_out} \
                --portbase {port_base} --autostart 1 \
                --interface {interface} -f "{file_path}"'
    log.debug(command)
    (_, err) = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
    if err:
      log.error(err)
    time.sleep(1.5)

def file_copy(params):
    # Is delete files and directories after transfer, default is True
    delete = True
    if 'delete' in params and params['delete'] == 'no':
        delete = False
    log.debug(f'Local copy starting ... with params :: {params}')

    # List and check if any flies or directories exists
    dirs, files = list_all_files(params[1]['in'])
    if len(files) == 0 or len(dirs) == 0:
        log.debug('No file or directory detected')
        return 0
    
    manifest_data = {}
    for f in files:
        if os.path.isfile(f):
            manifest_data[f] = hash_file(f)
    log.debug('Writing manifest file')
    # Use a dedicated name for each process to prevent race conditions
    manifest_filename = 'manifest_' + str(params[0]) + '.json'
    write_manifest(dirs, files, manifest_data, manifest_filename, params[1]['in'], params[1]["out"])
    log.info('Sending manifest file : ' + manifest_filename)

    log.debug(datetime.datetime.now())
    send_file(manifest_filename,
              params[1]['interface_in'],
              params[1]['ip_out'],
              int(params[1]['port']) + 2,
              params[1]['bitrate'])
    log.debug('Deleting manifest file')
    os.remove(manifest_filename)
    for f in files:
        log.info('Sending: ' + f)
        log.debug(datetime.datetime.now())
        send_file(f,
                  params[1]['interface_in'],
                  params[1]['ip_out'],
                  params[1]['port'],
                  params[1]['bitrate'])
        log.info('Deleting: ' + f)
        if delete:
            os.remove(f)
    if delete:
        for d in dirs:
            log.info('Deleting Dir: ' + d)
            try:
                os.rmdir(d)
            except:
                pass


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
