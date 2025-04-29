import unreal

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
        self.sequence = sequence
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        self.time_controls = self.time_controls(sequence)
        self.frame_rate = frame_rate

    class time_controls:
        def __init__(self, sequence: unreal.LevelSequence):
            self.sequence = sequence
            self.current_time = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()
            self.initial_playback_range = self.get_sequence_range()

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
            self.current_time = new_time
            print(f"[SequencerControls] Jumped {x} frames forward to {new_time}")
        
        def jump_x_frames_backward(self, x: int):
            if not self.sequence:
                print("Error: No sequence set.")
                return

            current_time = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()
            new_time = current_time - x
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(new_time)
            self.current_time = new_time
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

    def add_actor_to_sequence(self, actor : unreal.Actor):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        # Add the actor to the sequence
        unreal.LevelSequenceEditorBlueprintLibrary.add_actor_to_sequence(self.sequence, actor)
        print(f"[SequencerControls] Added actor {actor.get_name()} to sequence")
    
    def add_possesable_to_sequence(self, possesable_actor):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        # Add the spawnable to the sequence
        possesable = self.sequence.add_possessable(possesable_actor)
        print(f"[SequencerControls] Added spawnable {possesable_actor.get_name()} to sequence with ID {possesable}")
        return possesable

    def add_animation_to_actor(self, skeletal_mesh, anim):
        if not self.sequence:
            print("Error: No sequence set.")
            return

        params = unreal.MovieSceneSkeletalAnimationParams()
        params.set_editor_property('Animation', anim)
        anim_track = skeletal_mesh.add_track(unreal.MovieSceneSkeletalAnimationTrack)

        animation_section = anim_track.add_section()
        animation_section.set_editor_property('Params', params)
        animation_section.set_range(0, anim.get_play_length()*sequencer_controls.frame_rate)

        print(f"[SequencerControls] Added animation {anim.get_name()} to actor {skeletal_mesh.get_name()} in sequence")
        return anim_track, animation_section


# example usage for /Game/anims/testSequence.testSequence
sequence = unreal.EditorAssetLibrary.load_asset("/Game/anims/testSequence.testSequence")
sequencer_controls = SequencerControls(sequence, frame_rate=100)

# Example usage of time controls
sequencer_controls.time_controls.jump_to_frame(10)  # Jump to frame 10
sequencer_controls.time_controls.jump_x_frames_forward(5)  # Jump 5 frames forward
print(sequencer_controls.time_controls.reset_sequence_range())  # Reset the sequence range to default

actor = get_actor_by_name("SkeletalMeshActor_6")  # Fetch the actor by name
skeletal_mesh = sequencer_controls.add_possesable_to_sequence(actor)  # Add the actor to the sequence
print()

# Add animation to the skeletal mesh in the sequence
anim_asset = unreal.AnimSequence.cast(unreal.load_asset("/Game/anims/tmp/1_curved.1_curved"))
anim_track, animation_section = sequencer_controls.add_animation_to_actor(skeletal_mesh, anim_asset)  # Add animation to the actor in the sequence
sequencer_controls.time_controls.set_sequence_range(0, animation_section.get_end_frame())  # Set the sequence range to the animation length
