import time
import multiprocessing
import logging
import struct
import math
from socket import *
import pyinotify

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def screen_file_copy(file, params):
    port = params[1]['port']
    buffer_size = 2048
    addr = (params[1]['ip_out'], port)

    f = open(file, 'rb')
    file_data = f.read()
    file_length = len(file_data)

    nb_of_packets = int(math.floor(file_length // (buffer_size - 4))) + 1
    s = socket(AF_INET, SOCK_DGRAM)

    for i in range(1, nb_of_packets + 1):
        if i < nb_of_packets:
            data = file_data[((i - 1) * (buffer_size - 4)):(i * (buffer_size - 4))]
            msg = struct.pack('>I', len(data)) + data
        elif i == nb_of_packets:
            data = file_data[((i - 1) * (buffer_size - 4)):file_length]
            msg = struct.pack('>I', len(data)) + data
        s.sendto(msg, addr)
        time.sleep(0.0002)
        i += 1
    s.sendto(b'', addr)
    s.close()
    f.close()


class ScreenshotHandler(pyinotify.ProcessEvent):

    def process_IN_CLOSE_WRITE(self, event):
        current_process = multiprocessing.current_process()
        log.debug('New screenshot detected !')
        screen_file_copy(event.pathname, current_process._args)


def watch_folder(module, params):
    log.debug('Watching folder %s for screenshots ...' % params['in'])
    screen_wm = pyinotify.WatchManager()
    screen_mask = pyinotify.IN_CLOSE_WRITE
    screen_notifier = pyinotify.AsyncNotifier(screen_wm, ScreenshotHandler())
    screen_wdd = screen_wm.add_watch(params['in'], screen_mask, rec=True)
    screen_notifier.loop()

