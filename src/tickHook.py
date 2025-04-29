import unreal

class tickHooker:
    def __init__(self):
        self._delegate_handle = None
        self._bound_func = None

    def hook(self, func):
        if self._delegate_handle is not None:
            print("Already hooked, unhooking first.")
            self.unhook()

        if not callable(func):
            raise ValueError("Provided func must be callable")

        # Wrap to accept delta_seconds and call your function
        def tick_wrapper(delta_seconds):
            func(delta_seconds)

        self._bound_func = tick_wrapper
        self._delegate_handle = unreal.register_slate_post_tick_callback(self._bound_func)
        print("Tick hooked.")

    def unhook(self):
        if self._delegate_handle is not None:
            unreal.unregister_slate_post_tick_callback(self._delegate_handle)
            print("Tick unhooked.")
            self._delegate_handle = None
            self._bound_func = None
        else:
            print("No tick hook to unhook.")

    def hook_for_x_ticks(self, func, x, final_func=None):
        if not isinstance(x, int) or x <= 0:
            raise ValueError("x must be a positive integer")

        def tick_wrapper(delta_seconds):
            nonlocal x
            if x > 0:
                func(delta_seconds)
                x -= 1
            if x == 0:
                if final_func:
                    final_func(delta_seconds)
                self.unhook()

        self.hook(tick_wrapper)

    def wait_x_ticks_then_execute(self, func, x):
        if not isinstance(x, int) or x <= 0:
            raise ValueError("x must be a positive integer")

        def tick_wrapper(delta_seconds):
            nonlocal x
            if x > 0:
                x -= 1
            if x == 0:
                func(delta_seconds)
                self.unhook()

        self.hook(tick_wrapper)