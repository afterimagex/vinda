import threading
import time


class UTimer(threading.Thread):
    def __init__(self, tick_event, interval=0.016):
        super().__init__()
        self._tick_event = tick_event
        self._interval = interval
        self._is_running = False

    def pause(self):
        pass

    def resume(self):
        pass

    def run(self):
        self._is_running = True
        next_tick_time = time.perf_counter()
        while self._is_running:
            current_time = time.perf_counter()
            sleep_time = next_tick_time - current_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._tick_event.set()
            next_tick_time += self._interval

    @property
    def delta_time(self) -> float:
        return self._interval

    def stop(self):
        self._is_running = False
        self.join()
