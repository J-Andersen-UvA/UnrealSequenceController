# Unreal Sequence Controller

The Unreal Sequence Controller is a Python-based toolset designed to streamline and enhance the control of Unreal Engine Level Sequences. By leveraging Unreal's Python API, this project provides functionality for post processing animations using control rigs, and MIDI-based real-time control. With features such as time manipulation, keyframing, and animation export through a MIDI controller.

## tickHook.py
This Python script defines a tickHooker class for managing Unreal Engine's tick callbacks. It allows functions to be hooked into the tick system, executed for a specific number of ticks, or delayed by a set number of ticks.

## OSCListener.py
This script defines the OSCListener class, which provides a non-blocking UDP listener for Open Sound Control (OSC) messages. It receives OSC packets, parses them using python-osc, and stores the latest values per address in a dictionary. This allows seamless integration of real-time OSC data (e.g., from a MIDI or fader device) into Unreal Engine’s tick-based system.

## OSCMain.py
The main entry point for the project, this script initializes the MIDI listener, tick hooker, and sequencer controls. It demonstrates loading animations, control rigs, and sequences.

## sequencerControls.py
This script provides the SequencerControls class, which manages Unreal Engine Level Sequences. It includes methods for adding actors, animations, and control rigs to sequences, as well as manipulating playback ranges, keyframes, and exporting animations.

📘 Functionality Overview
| Function | Description | Usage |
|:----|:----|:-----|
| get_actor_by_name(name) | Finds an actor in the current level by name substring match. | get_actor_by_name("MyCharacter") |
| add_actor_to_sequence(actor) | Adds an actor to the sequence (as a possessable). | sc.add_actor_to_sequence(actor) |
| add_possesable_to_sequence(actor) | Adds a possessable actor and tracks it internally. | skeletal_mesh = sc.add_possesable_to_sequence(actor) |
| add_animation_to_actor(mesh, anim) | Adds an animation section to the actor's track. | sc.add_animation_to_actor(mesh, anim) |
| add_control_rig_to_actor(mesh, rig_asset) | Adds a Control Rig to the sequence and returns it. | sc.add_control_rig_to_actor(mesh, rig) |
| set_keyframe_control_rig(ctrl_name, value, frame=None, modus="Float") | Keyframes a control rig channel (float, rotator, transform, etc.). | sc.set_keyframe_control_rig("RightHandIndex", 20.0) |
| remove_keys_in_range_for_ctrl(ctrl_name, start, end) | Removes float keys from a control rig channel within a frame range. | sc.remove_keys_in_range_for_ctrl("RightHandIndex", 100, 120) |
| export_current_sequence(file_name, file_path, ue_package_path) | Exports the sequence as an AnimSequence asset. | sc.export_current_sequence("RunAnim", "C:/Export", "/Game/Exports") |

🕓 time_controls (Nested Class)
Control sequence playback and timing using this internal utility.
| Function                                   | Description                                            | Example                                                |
| :--- | :--- | :--- |
| `jump_to_frame(frame)`                     | Jump to a specific frame.                              | `sc.time_controls.jump_to_frame(100)`                  |
| `jump_x_frames_forward(x)` / `backward(x)` | Move forward/backward `x` frames.                      | `sc.time_controls.jump_x_frames_forward(10)`           |
| `time_knob_control(value)`                 | Control time scrubbing interactively via a knob/fader. | `sc.time_controls.time_knob_control(-20.0)`            |
| `get_sequence_range()`                     | Get start and end frames.                              | `(start, end) = sc.time_controls.get_sequence_range()` |
| `set_sequence_range(start, end)`           | Set playback frame range.                              | `sc.time_controls.set_sequence_range(0, 240)`          |
| `reset_sequence_range()`                   | Restore original playback range.                       | `sc.time_controls.reset_sequence_range()`              |
| `current_time()`                           | Get current frame number.                              | `frame = sc.time_controls.current_time()`              |
| `jump_to_percent(percent)`                 | Jump to a percentage of total sequence time.           | `sc.time_controls.jump_to_percent(50.0)`               |
