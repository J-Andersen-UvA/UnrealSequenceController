import unreal
from src.sequencer.sequencerControls import SequencerControls, get_actor_by_name

class AnimationSessionManager:
    def __init__(self, input_folder: str, output_folder: str, sequence_path: str, rig_path: str):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.sequence_path = sequence_path
        self.rig_path = rig_path
        self.todo = []
        self.current_animation = None

    def initialize(self):
        # Initialize the session manager, validate environment, and gather animations
        self._validate_environment()
        self._gather_animations_from_folder()

    def _validate_environment(self):
        # Warn if folders/assets are missing or misconfigured
        if not unreal.EditorAssetLibrary.does_directory_exist(self.input_folder):
            unreal.log_warning(f"Input folder does not exist: {self.input_folder}")
        if not unreal.EditorAssetLibrary.does_directory_exist(self.output_folder):
            unreal.log_warning(f"Output folder does not exist: {self.output_folder}")
        if not unreal.EditorAssetLibrary.does_asset_exist(self.sequence_path):
            unreal.log_warning(f"Sequence asset does not exist: {self.sequence_path}")
        if not unreal.EditorAssetLibrary.does_asset_exist(self.rig_path):
            unreal.log_warning(f"Control Rig asset does not exist: {self.rig_path}")
        if self.input_folder == self.output_folder:
            unreal.log_warning("Input and output folders are the same. This may cause issues with asset management.")

    def _is_valid_animation(self, path: str) -> bool:
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            return False
        asset = unreal.EditorAssetLibrary.load_asset(path)
        return isinstance(asset, unreal.AnimSequence)

    def _gather_animations_from_folder(self):
        # Define a list of animations to process
        self.todo = unreal.EditorAssetLibrary.list_assets(self.input_folder, recursive=True, include_folder=True)
        print(self.todo)
        # Check if each item in todo is a valid animation asset, otherwise log a warning and remove it
        self.todo = [anim for anim in self.todo if self._is_valid_animation(anim)]

        if not self.todo:
            unreal.log_warning("No valid animation assets found in todo list. Input folder may be empty or misconfigured.")

    def load_next_from_todo(self, actor_name: str = "SkeletalMeshActor_6") -> SequencerControls:
        """Loads the next animation from the todo list (FIFO)."""
        if not self.todo:
            unreal.log_warning("[Session] Todo list is empty. Nothing to load.")
            return None

        next_asset = self.todo[0]
        unreal.log(f"[Session] Loading next animation from todo: {next_asset}")

        return self.load_animation_from_todo(next_asset, actor_name)

    def load_animation_from_todo(self, anim_name: str, actor_name: str = "SkeletalMeshActor_6") -> SequencerControls:
        """Load an animation from the todo list using a name or partial match."""
        matching = [asset for asset in self.todo if asset.endswith(anim_name)]

        if not matching:
            unreal.log_warning(f"Animation {anim_name} not found in todo list.")
            return None

        full_asset_path = matching[0]  # take first match
        controls = self.load_animation(full_asset_path.replace(f"{self.input_folder}/", ""), actor_name)  # Strip path if needed
        if not controls:
            unreal.log_warning(f"Failed to load animation: {anim_name}")
            return None

        return controls

    def load_animation(self, anim_name: str, actor_name: str = "SkeletalMeshActor_6") -> SequencerControls:
        """Load animation into the sequence and return a configured SequencerControls object."""

        # Load sequence
        sequence = unreal.EditorAssetLibrary.load_asset(self.sequence_path)
        if not sequence:
            unreal.log_warning(f"Failed to load sequence: {self.sequence_path}")
            return None

        controls = SequencerControls(sequence, frame_rate=24)

        # Load actor
        actor = get_actor_by_name(actor_name)
        if not actor:
            unreal.log_warning("Could not find actor 'SkeletalMeshActor_6'")
            return None

        # Add actor to sequence
        skeletal_mesh = controls.add_possesable_to_sequence(actor)
        if not skeletal_mesh:
            unreal.log_warning("Failed to add actor to sequence.")
            return None
        
        controls.remove_existing_animation_tracks()

        # Load animation
        anim_path = f"{self.input_folder}/{anim_name}"
        anim_asset = unreal.AnimSequence.cast(unreal.load_asset(anim_path))
        if not anim_asset:
            unreal.log_warning(f"Could not load animation: {anim_path}")
            return None

        # Add animation to actor and set sequence range
        _, section = controls.add_animation_to_actor(skeletal_mesh, anim_asset)
        if not section:
            unreal.log_warning(f"Failed to add animation section for {anim_name}.")
            return None
        controls.time_controls.set_sequence_range(section.get_start_frame(), section.get_end_frame())

        # Load control rig
        rig_asset = unreal.ControlRigBlueprint.cast(unreal.load_asset(self.rig_path))
        if not rig_asset:
            unreal.log_warning(f"Could not load Control Rig: {self.rig_path}")
            return None

        controls.add_control_rig_to_actor(skeletal_mesh, rig_asset)
        if not controls.control_rig:
            unreal.log_warning("Failed to add Control Rig to actor.")
            return None

        # Success
        unreal.log(f"[Session] Loaded animation {anim_name} into sequence.")
        self.current_animation = anim_name # Store current animation name
        return controls

    def bake_and_export(self, file_name: str, controls: SequencerControls = None):
        """Bake and export the current animation to the output folder as an AnimSequence."""
        if controls is None:
            unreal.log_warning("[Session] No SequencerControls provided for export.")
            return

        # Convert to Unreal-friendly file path and name
        ue_package_path = self.output_folder
        file_path = f"{self.output_folder}/{file_name}"

        try:
            unreal.log(f"[Session] Baking and exporting animation: {file_name}")
            controls.export_current_sequence(file_name=file_name, file_path=file_path, ue_package_path=ue_package_path)
            unreal.log(f"[Session] Successfully exported animation to: {ue_package_path}/{file_name}")
        except Exception as e:
            unreal.log_error(f"[Session] Export failed: {e}")

    def cleanup_input(self, anim_name: str, delete_original: bool = False, move_folder: str = None):
        # Move or delete original after export
        full_path = f"{self.input_folder}/{anim_name}"
        if not unreal.EditorAssetLibrary.does_asset_exist(full_path):
            unreal.log_warning(f"[Session] Cannot clean up: {full_path} does not exist.")
            return

        if delete_original:
            unreal.EditorAssetLibrary.delete_asset(f"{self.input_folder}/{anim_name}")
            unreal.log(f"[Session] Deleted original animation: {anim_name}")
        else:
            if move_folder:
                new_path = f"{move_folder}/{anim_name}_original"
            else:
                new_path = f"{self.output_folder}/{anim_name}_original"
            if unreal.EditorAssetLibrary.does_asset_exist(new_path):
                unreal.log_warning(f"[Session] Target cleanup path already exists: {new_path}")
                return
            unreal.EditorAssetLibrary.rename_asset(f"{self.input_folder}/{anim_name}", new_path)
            unreal.log(f"[Session] Moved original animation to: {new_path}")

        # Remove from todo list
        if anim_name in self.todo:
            self.todo.remove(anim_name)
            unreal.log(f"[Session] Removed {anim_name} from todo list.")
        else:
            unreal.log_warning(f"{anim_name} not found in todo list for cleanup.")

# Example usage:
session_manager = AnimationSessionManager("/Game/anims/Editing/EditingInput", "/Game/anims/Editing/EditingOutput", "/Game/anims/Editing/blank.blank", "/Game/Avatars/RPM/GlassesGuy/armHands_Rig.armHands_Rig")
session_manager.initialize()
control_sequence = session_manager.load_next_from_todo()

if control_sequence:
    anim_name = session_manager.current_animation.replace(f"{session_manager.input_folder}/", "").split(".")[0]
    session_manager.bake_and_export(anim_name, control_sequence)
    session_manager.cleanup_input(anim_name, delete_original=False, move_folder="/Game/anims/Editing/OldOriginal")