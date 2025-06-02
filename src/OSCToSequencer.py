import time
import json

class OSCToSequencerBridge:
    def __init__(self, osc_listener, sequencer_controls, control_mapping_path, rate_limit_interval=0.05):
        self.osc_listener = osc_listener
        self.sequencer_controls = sequencer_controls
        self.rate_limit_interval = rate_limit_interval
        self.previous_osc_values = {}
        self.last_update_times = {}
        self.time_knob_speed = 5.0  # Default speed for time knob control
        self.remove_keys_start_frames = {}

        with open(control_mapping_path, "r") as f:
            self.control_mapping = json.load(f)

    def convert_to_range(self, value):
        try:
            return max(-100.0, min(100.0, ((float(value) * 200.0) - 100.0)))
        except:
            return 0.0
    
    def pop_previous_value(self, control_id):
        self.previous_osc_values.pop(control_id, None)
        self.osc_listener.latest_osc_values.pop(control_id, None)

    def update(self):
        now = time.time()
        to_pop = []
        for control_id, value in self.osc_listener.latest_osc_values.items():
            if value is None or control_id not in self.control_mapping:
                continue

            # Rate limiting
            if now - self.last_update_times.get(control_id, 0) < self.rate_limit_interval:
                continue

            # Skip unchanged
            if self.previous_osc_values.get(control_id) == value:
                continue

            self.last_update_times[control_id] = now
            self.previous_osc_values[control_id] = value
            mapped = self.control_mapping[control_id]
            converted_value = self.convert_to_range(value)

            # Handle actions
            if isinstance(mapped, str):
                if mapped == "TimeKnob":
                    self.sequencer_controls.time_controls.time_knob_control(converted_value, self.time_knob_speed)
                    # remove the TimeKnob from previous_osc_values to avoid repeated updates
                    to_pop.append(control_id)
                elif mapped == "TimeKnobSlow":
                    if value == 1.0:
                        self.time_knob_speed = 1.0
                    elif value == 0.0:
                        self.time_knob_speed = 5.0
                elif mapped == "TimeKnobFast":
                    if value == 1.0:
                        self.time_knob_speed = 10.0
                    elif value == 0.0:
                        self.time_knob_speed = 5.0
                elif mapped == "SaveSequence":
                    self.sequencer_controls.export_current_sequence("file_name_test", "file_path", ue_package_path="/Game/")
                elif mapped == "FrameForward":
                    self.sequencer_controls.time_controls.step_forward()
                elif mapped == "FrameBackward":
                    self.sequencer_controls.time_controls.step_backward()
                elif mapped == "PlayPause":
                    self.sequencer_controls.time_controls.play_pause()
                elif mapped == "KeyframeAllZero":
                    self.sequencer_controls.set_keyframe_all_zero()
                # elif mapped == "Stop":
                #     self.sequencer_controls.time_controls.pause()
                elif mapped.startswith("RemoveKeys"):
                    # If value is 1, record the current frame
                    if value == 1.0:
                        current_frame = self.sequencer_controls.time_controls.current_time()
                        self.remove_keys_start_frames[control_id] = current_frame
                    # If value is 0, remove keys between the recorded start frame and the current frame
                    elif value == 0.0 and control_id in self.remove_keys_start_frames:
                        start_frame = self.remove_keys_start_frames.pop(control_id)
                        current_frame = self.sequencer_controls.time_controls.current_time()
                        # Assuming the control_id is in the form "RemoveKeys<control_name>"
                        ctrl_name = mapped.split("RemoveKeys")[-1]
                        self.sequencer_controls.remove_keys_in_range_for_ctrl(ctrl_name, start_frame, current_frame)
                else:
                    self.sequencer_controls.set_keyframe_control_rig(mapped, converted_value)
            elif isinstance(mapped, dict):
                for ctrl in mapped["set_prev"]:
                    ctrl_mapping = self.control_mapping.get(ctrl)
                    if isinstance(ctrl_mapping, str):
                        if ctrl in self.previous_osc_values:
                            self.sequencer_controls.set_keyframe_control_rig(ctrl_mapping, self.convert_to_range(self.previous_osc_values[ctrl]))
                    elif isinstance(ctrl_mapping, list):
                        if ctrl in self.previous_osc_values:
                            self.sequencer_controls.set_keyframe_control_rig(ctrl_mapping[0], self.convert_to_range(self.previous_osc_values[ctrl]), modus=ctrl_mapping[1])
            elif isinstance(mapped, list):
                self.sequencer_controls.set_keyframe_control_rig(mapped[0], converted_value, modus=mapped[1])

            print(f"[OSCToSequencerBridge] Updated {control_id} to {converted_value} with mapping {mapped}")
        
        # Remove popped controls from previous values, useful for controls like TimeKnob that should need to be updated repeatedly on max values
        for control_id in to_pop:
            self.pop_previous_value(control_id)
