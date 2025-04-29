from src.MIDIToOSC.src.MIDIReader import MidiListener
from src.tickHook import tickHooker
import time

# Define a function to handle incoming MIDI messages
def handle_midi_message(msg):
    print(f"[MAIN] Received MIDI: {msg}")
    # Clamp value between 0 and 1 for OSC sending, its a float and usually between 0-127
    value = max(0, min(1, msg.value / 127.0))
    if value == 0.0:
        value = 0.0  # Ensure value is exactly 0.0 if clamped to 0
    elif value == 1.0:
        value = 1.0

# Instantiate MIDI listener with the handler
midi = MidiListener(device_name="Hobscure MIDI 0", callback=handle_midi_message)
tickHooker_instance = tickHooker()

midi.list_devices()
# tickHooker_instance.hook(lambda dt: midi.listen_once())

tickHooker_instance.unhook()