from src.MIDIToOSC.src.MIDIReader import MidiListener
from src.tickHook import tickHooker
from src.sequencer.sequencerControls import SequencerControls
import json

# Define a function to handle incoming MIDI messages
def handle_midi_message(msg):
    print(f"[MAIN] Received MIDI: {msg}")
    # Clamp value between 0 and 100 for OSC sending, its a float and usually between 0-127
    value = max(0, min(100, (msg.value / 127.0) * 100))
    if value == 0.0:
        value = 0.0  # Ensure value is exactly 0.0 if clamped to 0
    elif value == 100.0:
        value = 100.0

# Instantiate MIDI listener with the handler
midi = MidiListener(device_name="Hobscure MIDI 0", callback=handle_midi_message)
tickHooker_instance = tickHooker()

midi.list_devices()
# tickHooker_instance.hook(lambda dt: midi.listen_once())
# tickHooker_instance.wait_x_ticks_then_execute(lambda dt: midi.listen_once(), 10)
midi.open_port()
tickHooker_instance.hook_for_x_ticks(lambda dt: midi.listen_once(True), 200, final_func=lambda dt: midi.close_port())

# tickHooker_instance.unhook()