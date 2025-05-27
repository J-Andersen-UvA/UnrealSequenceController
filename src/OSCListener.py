import socket
import select
from pythonosc.osc_packet import OscPacket
from collections import defaultdict

class OSCListener:
    def __init__(self, ip="127.0.0.1", port=5501):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.sock.setblocking(False)
        self.latest_osc_values = defaultdict(lambda: None)

    def update(self):
        try:
            while True:
                ready = select.select([self.sock], [], [], 0.0)[0]
                if not ready:
                    break
                data, addr = self.sock.recvfrom(1024)
                packet = OscPacket(data)
                for timed_msg in packet.messages:
                    msg = timed_msg.message
                    address = msg.address.strip("/")
                    value = msg.params[-1] if msg.params else None
                    self.latest_osc_values[address] = value
        except Exception as e:
            print(f"[OSCListener] Error: {e}")
