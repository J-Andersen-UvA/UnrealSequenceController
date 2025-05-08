from src.MIDIToOSC.src.MIDIReader import MidiListener
from src.tickHook import tickHooker
from src.sequencer.sequencerControls import SequencerControls
import unreal
from functools import partial
from src.sequencer.sequencerControls import get_actor_by_name
import json

control_mapping = json.load(open("C:\\Users\\VICON\\Desktop\\Code\\UnrealSequenceController\\MIDIToCTRLMapping2.json", "r"))

# Define a function to handle incoming MIDI messages
def handle_midi_message(msg, sequencer_controls=None):
    print(f"[MAIN] Received MIDI: {msg}")
    # Map the MIDI value (0-127) to the range -100 to 100
    value = ((float(msg.value) / 127.0) * 200) - 100
    value = max(-100, min(100, value))  # Clamp value between -100 and 100
    if value == 0.0:
        value = 0.0  # Ensure value is exactly 0.0 if clamped to 0
    elif value == 100.0:
        value = 100.0
    elif value == -100.0:
        value = -100.0
    
    # Send the value to the sequencer
    if control_mapping[str(msg.control)] == "TimeKnob":
        sequencer_controls.time_controls.jump_to_percent(value)  # Jump to the percentage of the sequence length
    elif control_mapping[str(msg.control)] == "SaveSequence":
        sequencer_controls.export_current_sequence("file_name_test", "file_path", ue_package_path="/Game/")
    elif str(msg.control) in control_mapping.keys():
        # Check if the control_mapping[str(msg.control)] is a list of control and modus
        if isinstance(control_mapping[str(msg.control)], list):
            # If it's a list, set the single control with the modus
            sequencer_controls.set_keyframe_control_rig(control_mapping[str(msg.control)][0], value, modus=control_mapping[str(msg.control)][1])
            print(f"[SequencerControls] Set {control_mapping[str(msg.control)][0]} to {value} at frame {sequencer_controls.time_controls.current_time()} with modus {control_mapping[str(msg.control)][1]}")
        else:
            # If it's a single control, set it directly
            sequencer_controls.set_keyframe_control_rig(control_mapping[str(msg.control)], value)
            print(f"[SequencerControls] Set {control_mapping[str(msg.control)]} to {value} at frame {sequencer_controls.time_controls.current_time()}")

def load_in_animation(seq_path="/Game/anims/testSequence.testSequence", skelmesh_name="SkeletalMeshActor_6", anim_path="/Game/anims/tmp/pet/PET-A_250228_1_Anim.PET-A_250228_1_Anim", rig_path="/Game/Avatars/RPM/GlassesGuy/armHands_Rig.armHands_Rig"):
    # example usage for /Game/anims/testSequence.testSequence
    sequence = unreal.EditorAssetLibrary.load_asset(seq_path)
    sequencer_controls = SequencerControls(sequence, frame_rate=100)

    # Example usage of time controls
    sequencer_controls.time_controls.jump_to_frame(0)  # Jump to frame 10

    # Add an actor to the sequence
    actor = get_actor_by_name(skelmesh_name)  # Fetch the actor by name
    skeletal_mesh = sequencer_controls.add_possesable_to_sequence(actor)  # Add the actor to the sequence

    # Add animation to the skeletal mesh in the sequence
    anim_asset = unreal.AnimSequence.cast(unreal.load_asset(anim_path))
    anim_track, animation_section = sequencer_controls.add_animation_to_actor(skeletal_mesh, anim_asset)  # Add animation to the actor in the sequence
    sequencer_controls.time_controls.set_sequence_range(animation_section.get_start_frame(), animation_section.get_end_frame())  # Set the sequence range to the animation length

    # Add control rig to the skeletal mesh in the  sequence /Game/Avatars/RPM/GlassesGuy/armHands_Rig.armHands_Rig
    control_rig_asset = unreal.ControlRigBlueprint.cast(unreal.load_asset(rig_path))
    control_rig_track, control_rig_instance = sequencer_controls.add_control_rig_to_actor(skeletal_mesh, control_rig_asset)  # Add control rig to the actor in the sequence

    # Return the mapping of control numbers to their setters
    return sequencer_controls, sequence, control_rig_instance

sequencer_controls, sequence, control_rig_instance = load_in_animation()
midi = MidiListener(device_name="Hobscure MIDI 0", callback=lambda msg: handle_midi_message(msg, sequencer_controls=sequencer_controls))
tickHooker_instance = tickHooker()
midi.open_port()
tickHooker_instance.hook_for_x_ticks(midi.listen_once, 2000, final_func=midi.close_port)

