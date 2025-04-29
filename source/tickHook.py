import unreal
import time

class tickHooker:
    def __init__(self):
        self._tick_hooks = []

    def hook(self, tick_function):
        hook = unreal.register_slate_post_tick_callback(tick_function)
        self._tick_hooks.append(hook)

    def unhook(self):
        for hook in self._tick_hooks:
            unreal.unregister_slate_post_tick_callback(hook)
        self._tick_hooks = []

# # Example usage
# def example_function(delta_time):
#     # This function will be called every tick
#     unreal.log("Tick! Delta Time: {}".format(delta_time))

# tickHooker_instance = tickHooker()
# tickHooker_instance.hook(example_function)
# # time.sleep(5)  # Keep the script running for 5 seconds to see the tick function in action
# tickHooker_instance.unhook()  # Unhook the tick function when done