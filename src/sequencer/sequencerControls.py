import unreal
from enum import Enum

class ctrlRigVals(Enum):
    RightHandIndex = "RightHandIndex"
    RightHandMiddle = "RightHandMiddle"
    RightHandRing = "RightHandRing"
    RightHandPinky = "RightHandPinky"
    RightHandThumb = "RightHandThumb"
    LeftHandIndex = "LeftHandIndex"
    LeftHandMiddle = "LeftHandMiddle"
    LeftHandRing = "LeftHandRing"
    LeftHandPinky = "LeftHandPinky"
    LeftHandThumb = "LeftHandThumb"

def get_actor_by_name(name):
    """
    Fetch an actor by name.

    Params:
    - name (str): The name of the actor to fetch.
    """
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in actors:
        if name in actor.get_name():
            return actor
    return None

class SequencerControls:
    def __init__(self, sequence: unreal.LevelSequence, frame_rate: int = 30):
        self.control_rig = None
        self.skeletal_mesh = None
        self.anim_sequence = None
        self.actor = None
        self.skeletal_mesh_binding_proxy = None
        self.sequence = sequence
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        self.time_controls = self.time_controls(sequence)
        self.frame_rate = frame_rate

    class time_controls:
        def __init__(self, sequence: unreal.LevelSequence):
            self.sequence = sequence
            self.initial_playback_range = self.get_sequence_range()
            self.timeKnobPrevious = 0.0

        def time_knob_control(self, timeKnobCur: float, step: int = 1):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            # Calculate the new time based on the percentage
            if timeKnobCur < -100.0 or timeKnobCur > 100.0:
                print("Error: timeKnobCur must be between -100 and 100, received:", timeKnobCur)
                return
            
            # Timeknob is clamped between 0 and 100
            forward = False
            if timeKnobCur > self.timeKnobPrevious:
                forward = True
            elif timeKnobCur == self.timeKnobPrevious:
                forward = timeKnobCur == 100.0
            self.timeKnobPrevious = timeKnobCur
            step = step if forward else -step

            curTime = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()
            new_time = curTime + step
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(new_time)
        
        def play_pause(self):
            if not self.sequence:
                print("Error: No sequence set.")
                return
            
            if unreal.LevelSequenceEditorBlueprintLibrary.is_playing():
                unreal.LevelSequenceEditorBlueprintLibrary.pause()
                print("[SequencerControls] Playback paused")
            else:
                unreal.LevelSequenceEditorBlueprintLibrary.play()
                print("[SequencerControls] Playback started")

        def jump_to_frame(self, frame_number: int):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame_number)
            print(f"[SequencerControls] Jumped to frame {frame_number}")

        def jump_x_frames_forward(self, x: int):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            current_time = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()
            new_time = current_time + x
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(new_time)
            print(f"[SequencerControls] Jumped {x} frames forward to {new_time}")
        
        def jump_x_frames_backward(self, x: int):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            current_time = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()
            new_time = current_time - x
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(new_time)
            print(f"[SequencerControls] Jumped {x} frames backward to {new_time}")

        def get_sequence_range(self):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            start = self.sequence.get_playback_start()
            end = self.sequence.get_playback_end()

            print(f"[SequencerControls] Sequence range: {start} to {end}")
            return (start, end)

        def set_sequence_range(self, start, end):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            # Set playback range directly
            self.sequence.set_playback_start(start)
            self.sequence.set_playback_end(end)

            print(f"[SequencerControls] Set playback range: {start} to {end}")
            return (start, end)

        def reset_sequence_range(self):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            # Reset to default range (0 to 1)
            self.set_sequence_range(self.initial_playback_range[0], self.initial_playback_range[1])
            print("[SequencerControls] Reset playback range to default")

        def current_time(self):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            current_time = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()
            print(f"[SequencerControls] Current time: {current_time}")
            return current_time
        
        def jump_to_percent(self, percent: float):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            start, end = self.get_sequence_range()
            new_time = start + (end - start) * (percent / 100.0)
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(new_time)
            print(f"[SequencerControls] Jumped to {percent}% of the sequence")            

    def add_actor_to_sequence(self, actor : unreal.Actor):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        # Add the actor to the sequence
        self.actor = actor
        unreal.LevelSequenceEditorBlueprintLibrary.add_actor_to_sequence(self.sequence, actor)
        print(f"[SequencerControls] Added actor {actor.get_name()} to sequence")
    
    def add_possesable_to_sequence(self, possesable_actor):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        # Add the spawnable to the sequence
        possesable = self.sequence.add_possessable(possesable_actor)
        print(f"[SequencerControls] Added spawnable {possesable_actor.get_name()} to sequence with ID {possesable}")
        self.skeletal_mesh = possesable_actor
        self.skeletal_mesh_binding_proxy = possesable

        return possesable

    def add_animation_to_actor(self, skeletal_mesh, anim):
        if not self.sequence:
            print("Error: No sequence set.")
            return
        
        # Don't add the same animation twice
        if self.anim_sequence == anim:
            print(f"[SequencerControls] Animation {anim.get_name()} already added to actor {skeletal_mesh.get_name()} in sequence")
            return

        params = unreal.MovieSceneSkeletalAnimationParams()
        params.set_editor_property('Animation', anim)
        anim_track = skeletal_mesh.add_track(unreal.MovieSceneSkeletalAnimationTrack)

        animation_section = anim_track.add_section()
        animation_section.set_editor_property('Params', params)
        animation_section.set_range(0, anim.get_play_length()*self.frame_rate)

        self.anim_sequence = anim
        print(f"[SequencerControls] Added animation {anim.get_name()} to actor {skeletal_mesh.get_name()} in sequence")
        return anim_track, animation_section
    
    def add_control_rig_to_actor(self, skeletal_mesh, control_rig):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        # Using the level sequence and actor binding, we can either find or create a control rig track from the class
        editor_system = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        world = editor_system.get_editor_world()
        # Get the rig class
        rig_class = control_rig.get_control_rig_class()
        rig_track = unreal.ControlRigSequencerLibrary.find_or_create_control_rig_track(world, self.sequence, rig_class, skeletal_mesh, is_layered_control_rig = True)

        # Get the Control Rig instance
        control_rig_instance = unreal.ControlRigSequencerLibrary.get_control_rigs(self.sequence)[0].control_rig

        print(f"[SequencerControls] Added Control Rig {control_rig.get_name()} to actor {skeletal_mesh.get_name()} in sequence")
        self.control_rig = control_rig_instance
        return rig_track, control_rig_instance

    def remove_existing_animation_tracks(self):
        """Remove all skeletal animation tracks from the current skeletal mesh binding."""
        if not self.skeletal_mesh_binding_proxy:
            unreal.log_warning("[SequencerControls] No skeletal mesh binding proxy found.")
            return

        for track in self.skeletal_mesh_binding_proxy.get_tracks():
            if isinstance(track, unreal.MovieSceneSkeletalAnimationTrack):
                unreal.log(f"[SequencerControls] Removing existing animation track: {track.get_display_name()}")
                self.skeletal_mesh_binding_proxy.remove_track(track)

    
    def set_keyframe_control_rig(self, ctrl_name, value, frame_number=None, modus="Float"):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        if not self.control_rig:
            print("Error: No control rig set.")
            return

        if frame_number is None:
            frame_number = unreal.FrameNumber(self.time_controls.current_time())

        seq_lib = unreal.ControlRigSequencerLibrary

        if modus == "Float":
            # Set the control rig float value
            seq_lib.set_local_control_rig_float(self.sequence, self.control_rig, ctrl_name, frame_number, value, set_key=True)
            # Set a keyframe at the current time
            current = seq_lib.get_local_control_rig_float(self.sequence, self.control_rig, ctrl_name, frame_number)
            print(f"[SequencerControls] Set {ctrl_name} to {value} at frame {frame_number}, current value: {current}")
        elif modus.startswith("Rotator"):
            rot_map = {
                "RotatorX": unreal.Rotator(value, 0, 0),
                "RotatorY": unreal.Rotator(0, value, 0),
                "RotatorZ": unreal.Rotator(0, 0, value)
            }
            rot = rot_map.get(modus)
            seq_lib.set_local_control_rig_rotator(self.sequence, self.control_rig, ctrl_name, frame_number, rot, set_key=True)
            current = seq_lib.get_local_control_rig_rotator(self.sequence, self.control_rig, ctrl_name, frame_number)
        elif modus.startswith("EulerRotation"):
            current_transform = seq_lib.get_local_control_rig_euler_transform(self.sequence, self.control_rig, ctrl_name, frame_number)
            if modus == "EulerRotationX":
                current_transform.rotation.roll = value
            elif modus == "EulerRotationY":
                current_transform.rotation.yaw = value
            elif modus == "EulerRotationZ":
                current_transform.rotation.pitch = value
            seq_lib.set_local_control_rig_euler_transform(self.sequence, self.control_rig, ctrl_name, frame_number, current_transform, set_key=True)
            current = seq_lib.get_local_control_rig_euler_transform(self.sequence, self.control_rig, ctrl_name, frame_number)
        elif modus.startswith("EulerTransform"):
            current_transform = seq_lib.get_local_control_rig_euler_transform(self.sequence, self.control_rig, ctrl_name, frame_number)
            if modus == "EulerTransformX":
                current_transform.location.x = value
            elif modus == "EulerTransformY":
                current_transform.location.y = value
            elif modus == "EulerTransformZ":
                current_transform.location.z = value
            seq_lib.set_local_control_rig_euler_transform(self.sequence, self.control_rig, ctrl_name, frame_number, current_transform, set_key=True)
            current = seq_lib.get_local_control_rig_euler_transform(self.sequence, self.control_rig, ctrl_name, frame_number)
        else:
            raise ValueError(f"Unsupported modus: {modus}")
        
        print(f"[SequencerControls] Set {ctrl_name} to {value} at frame {frame_number}, current value: {current}")
    
    def set_keyframe_all_zero(self):
        for ctrl in ctrlRigVals:
            print(f"[SequencerControls] Setting keyframe for {ctrl.value} to 0.0")
            self.set_keyframe_control_rig(ctrl.value, 0.0, modus="Float")

    def remove_keys_in_range_for_ctrl(self, ctrl_name, start_frame, end_frame):
        if not self.sequence or not self.control_rig:
            print("Error: No sequence or control rig set.")
            return

        if start_frame > end_frame:
            start_frame, end_frame = end_frame, start_frame

        for binding in self.sequence.get_bindings():
            for track in binding.get_tracks():
                if isinstance(track, unreal.MovieSceneControlRigParameterTrack):
                    for section in track.get_sections():
                        # We must iterate all possible scripting channels manually
                        all_channels = section.get_channels_by_type(unreal.MovieSceneScriptingFloatChannel)
                        # all_channels = section.get_channel_proxy().get_all_channels()
                        for channel in all_channels:
                            # This returns the name as shown in Sequencer
                            name = channel.channel_name
                            if name == ctrl_name:
                                if isinstance(channel, unreal.MovieSceneScriptingFloatChannel):
                                    keys = channel.get_keys()
                                    for key in keys:
                                        frame = key.get_time().frame_number.value
                                        if start_frame <= frame <= end_frame:
                                            print(f"[SequencerControls] Removing key on '{ctrl_name}' at frame {frame}")
                                            channel.remove_key(key)

    def export_current_sequence(self, file_name, file_path, ue_package_path="/Game/"):
        if not self.sequence:
            print("Error: No sequence set.")
            return
        
        # ls_editor = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
        # print(self.skeletal_mesh)
        # binding = self.sequence.find_binding_by_name(self.skeletal_mesh.get_name())
        binding = self.skeletal_mesh_binding_proxy

        # if not binding or binding.get_id() == unreal.Guid():
        #     print(self.skeletal_mesh)
        #     print("Error: Could not find valid binding for skeletal mesh.")
        #     return

        # bake_settings = unreal.BakingAnimationKeySettings()
        # bake_settings.reduce_keys = True
        # success = ls_editor.bake_transform_with_settings(
        #     object_bindings=[binding],
        #     settings=bake_settings
        # )

        # if success:
        #     print("Transform baking completed successfully.")
        # else:
        #     print("Transform baking failed.")

        # Get the current level sequence
        level_sequence = self.sequence
        # level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()

        # Grab the Level Editor World
        editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        world = editor_subsystem.get_editor_world()

        # Create animation sequence export options
        anim_seq_export_options = unreal.AnimSeqExportOption()
        anim_seq_export_options.export_morph_targets = True

        animFactory = unreal.AnimSequenceFactory()
        animFactory.target_skeleton = self.skeletal_mesh.skeletal_mesh_component.skeletal_mesh.skeleton
        # Get asset tools
        # Create an empty AnimSequence - /Game/Test_Anim
        print(dir(self.skeletal_mesh))
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        anim_sequence = unreal.AssetTools.create_asset(asset_tools, asset_name = file_name, package_path = ue_package_path, asset_class = unreal.AnimSequence, factory = animFactory)

        # Bake to the created AnimSequence
        unreal.SequencerTools.export_anim_sequence(world, level_sequence, anim_sequence, anim_seq_export_options, binding, False)



# # example usage for /Game/anims/testSequence.testSequence
# sequence = unreal.EditorAssetLibrary.load_asset("/Game/anims/testSequence.testSequence")
# sequencer_controls = SequencerControls(sequence, frame_rate=120)

# # Example usage of time controls
# sequencer_controls.time_controls.jump_to_frame(10)  # Jump to frame 10
# sequencer_controls.time_controls.jump_x_frames_forward(5)  # Jump 5 frames forward
# print(sequencer_controls.time_controls.reset_sequence_range())  # Reset the sequence range to default

# # Add an actor to the sequence
# actor = get_actor_by_name("SkeletalMeshActor_6")  # Fetch the actor by name
# skeletal_mesh = sequencer_controls.add_possesable_to_sequence(actor)  # Add the actor to the sequence
# print()

# # Add animation to the skeletal mesh in the sequence
# anim_asset = unreal.AnimSequence.cast(unreal.load_asset("/Game/anims/tmp/1_curved.1_curved"))
# anim_track, animation_section = sequencer_controls.add_animation_to_actor(skeletal_mesh, anim_asset)  # Add animation to the actor in the sequence
# sequencer_controls.time_controls.set_sequence_range(animation_section.get_start_frame(), animation_section.get_end_frame())  # Set the sequence range to the animation length

# # Add control rig to the skeletal mesh in the  sequence /Game/Avatars/RPM/GlassesGuy/armHands_Rig.armHands_Rig
# control_rig_asset = unreal.ControlRigBlueprint.cast(unreal.load_asset("/Game/Avatars/RPM/GlassesGuy/armHands_Rig.armHands_Rig"))
# control_rig_track, control_rig_instance = sequencer_controls.add_control_rig_to_actor(skeletal_mesh, control_rig_asset)  # Add control rig to the actor in the sequence

# # Gets the local control values, each control type will have their own typed function
# frame = unreal.FrameNumber(0)
# transform = unreal.ControlRigSequencerLibrary.get_local_control_rig_float(sequence, control_rig_instance, "RightHandIndex", frame)
# print(transform)

# sequencer_controls.time_controls.jump_to_frame(30)  # Jump to frame 30
# frame = unreal.FrameNumber(sequencer_controls.time_controls.current_time())
# sequencer_controls.set_keyframe_control_rig("RightHandIndex", 20.0, frame)  # Set a keyframe for the control rig at frame 30
# transform = unreal.ControlRigSequencerLibrary.get_local_control_rig_float(sequence, control_rig_instance, "RightHandIndex", frame)
# print(transform)

# sequencer_controls.export_current_sequence("file_name_test", "C:/Users/VICON/Desktop/Code/UnrealSequenceController/tmp", ue_package_path="/Game/")