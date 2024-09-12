class AsyncWorldEventMixin:
    pass


class WorldEventMixin:

    def __init__(self):
        self._tickable = False
        self._has_begun_play = False
        self._mark_pending_kill = False

    def _on_children(self, method_name, *args, **kwargs):
        for obj in self.children():
            if isinstance(obj, WorldEventMixin):
                getattr(obj, method_name)(*args, **kwargs)

    def on_begin_play(self):
        self._on_children("on_begin_play")
        if not self._has_begun_play:
            self._has_begun_play = True
            self.begin_play()

    def on_tick(self, delta_time: float):
        self._on_children("on_tick", delta_time)
        if self._tickable:
            self.tick(delta_time)

    def on_end_play(self, end_play_reason: str):
        self._on_children("on_end_play", end_play_reason)
        self._has_begun_play = False
        self.end_play(end_play_reason)

    # def on_finally_destroy(self):
    #     self._on_children("on_finally_destroy")
    #     if self._mark_destroy:
    #         self.finally_destroy()

    def begin_play(self):
        """begin_play"""

    def end_play(self, end_play_reason):
        """end_play"""

    def tick(self, delta_time: float):
        """tick"""

    def destroy(self):
        """标记待销毁"""
        self._on_children("on_destroy")
        self._mark_pending_kill = True

    # def finally_destroy(self):
    #     """销毁前最后一个回调"""
    #     if world := self.ctx.world():
    #         world.final_remove_actor(self)
