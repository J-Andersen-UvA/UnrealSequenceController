# Unreal Sequence Controller

The Unreal Sequence Controller is a Python-based toolset designed to streamline and enhance the control of Unreal Engine Level Sequences. By leveraging Unreal's Python API, this project provides functionality for post processing animations using control rigs, and MIDI-based real-time control. With features such as time manipulation, keyframing, and animation export through a MIDI controller.

## tickHook.py
This Python script defines a tickHooker class for managing Unreal Engine's tick callbacks. It allows functions to be hooked into the tick system, executed for a specific number of ticks, or delayed by a set number of ticks.

## MIDIReader.py
This script implements a MidiListener class for handling MIDI input using the mido library. It supports device discovery, real-time MIDI message handling, and callback-based processing for control changes.

## main.py
The main entry point for the project, this script initializes the MIDI listener, tick hooker, and sequencer controls. It handles MIDI messages, maps them to Unreal Engine actions, and demonstrates loading animations, control rigs, and sequences.

## sequencerControls.py
This script provides the SequencerControls class, which manages Unreal Engine Level Sequences. It includes methods for adding actors, animations, and control rigs to sequences, as well as manipulating playback ranges, keyframes, and exporting animations.