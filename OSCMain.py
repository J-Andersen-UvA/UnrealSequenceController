from src.OSCListener import OSCListener
from src.OSCToSequencer import OSCToSequencerBridge
from src.tickHook import tickHooker
from src.sequencer.sequencerControls import SequencerControls, get_actor_by_name
import unreal

def load_in_animation():
    seq = unreal.EditorAssetLibrary.load_asset("/Game/anims/empty.empty")
    controls = SequencerControls(seq, frame_rate=24)
    actor = get_actor_by_name("SkeletalMeshActor_6")
    skeletal_mesh = controls.add_possesable_to_sequence(actor)
    anim_asset = unreal.AnimSequence.cast(unreal.load_asset("/Game/anims/Cinematics/2025-05-28/Scene_1_204_Subscenes/Animation/GlassesGuyRecord_Scene_1_204.GlassesGuyRecord_Scene_1_204"))
    _, section = controls.add_animation_to_actor(skeletal_mesh, anim_asset)
    controls.time_controls.set_sequence_range(section.get_start_frame(), section.get_end_frame())
    rig_asset = unreal.ControlRigBlueprint.cast(unreal.load_asset("/Game/Avatars/RPM/GlassesGuy/armHands_Rig.armHands_Rig"))
    controls.add_control_rig_to_actor(skeletal_mesh, rig_asset)
    return controls

# Init systems
osc_listener = OSCListener()
sequencer_controls = load_in_animation()
bridge = OSCToSequencerBridge(osc_listener, sequencer_controls, "C:\\Users\\VICON\\Desktop\\Code\\UnrealSequenceController\\FAD9.json")

# Tick function
def tick_func(delta_seconds):
    osc_listener.update()
    bridge.update()

tick = tickHooker()
tick.hook(tick_func)


# tick.unhook()  # Uncomment to unhook the tick when done