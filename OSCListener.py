import socket
import select
from pythonosc.osc_packet import OscPacket
from src.tickHook import tickHooker
from collections import defaultdict

# Settings
ip = "127.0.0.1"
port = 5501

# Non-blocking socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))
sock.setblocking(False)

# OSC data tracking
latest_osc_values = defaultdict(lambda: None)
previous_osc_values = {}

def handle_osc_message(address, args):
    value = args[-1] if args else None
    latest_osc_values[address] = value

def listen_for_osc_tick(delta_seconds):
    try:
        while True:
            ready = select.select([sock], [], [], 0.0)[0]
            if not ready:
                break
            data, addr = sock.recvfrom(1024)

            packet = OscPacket(data)
            for timed_msg in packet.messages:
                msg = timed_msg.message
                handle_osc_message(msg.address, msg.params)
    except Exception as e:
        print(f"OSC error: {e}")

    # Only print changed values
    for address, value in latest_osc_values.items():
        prev = previous_osc_values.get(address)
        if value != prev:
            print(f"{address}: {value}")
            previous_osc_values[address] = value

tick = tickHooker()
tick.hook(listen_for_osc_tick)
