import time
import multiprocessing
import logging
import struct
from socket import *
from http.server import BaseHTTPRequestHandler, HTTPServer

# Logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

receiver_ip = '172.10.0.2'

def get_screenshot(port):
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((receiver_ip, port))

    full_data = b''
    while True:
        data, addr = s.recvfrom(2048)
        if not data:
            break
        else:
            msg_length = struct.unpack('>I', data[:4])[0]
            full_data += data[4:(msg_length + 4)]
    s.close()

    return full_data


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/cam'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            try:
                while True:
                    image = get_screenshot(multiprocessing.current_process()._args[1]['port'])
                    self.wfile.write(bytes("--jpgboundary\n", "utf-8"))
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(image))
                    self.end_headers()
                    self.wfile.write(image)
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            return
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("""<html><head></head><body>
        Visiting /cam to see screen sharing
      </body></html>""", "utf-8"))
            return


def http_server(module, properties):
    print("starting http server...")
    try:
        receiver_ip = properties['ip_in']
        server = HTTPServer(('', properties['http_port']), CamHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()