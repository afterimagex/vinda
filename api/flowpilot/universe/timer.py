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


class WorldTimer:
    def __init__(self) -> None:
        self._real_time_seconds: float = 0.0
        self._time_seconds: float = 0.0
        self._unpaused_time_seconds: float = 0.0
        self._frame_number: int = 0

    def update(self, delta_time: float):
        if delta_time <= 0:
            delta_time = 1.0 / 30.0

        # 更新世界真实时间
        self._real_time_seconds += delta_time

        # 考虑时间缩放因子
        time_dilation = self._get_time_dilation()

        # 计算缩放后的DeltaTime
        scaled_delta_time = delta_time * time_dilation

        # 更新游戏时间
        self._time_seconds += scaled_delta_time

        # 更新Unpaused时间（不考虑暂停的时间）
        self._unpaused_time_seconds += 0.0 if self._is_paused() else scaled_delta_time

        # 更新帧数
        self._frame_number += 1

        # 记录统计数据
        self._last_delta_time = delta_time
        self._last_real_time = self._real_time_seconds
        self._last_time = self._time_seconds


# 在虚幻引擎（Unreal Engine）中，定时器（Timer）是一个常见的工具，用于在指定的时间间隔内执行某些逻辑操作。虽然世界（World）和引擎（Engine）中都可以使用定时器，但它们的作用域和使用场景有所不同。

# ### World Timer（世界定时器）

# `UWorld` 中的定时器通常用于与具体的游戏世界实例相关的操作。每个 `UWorld` 实例都有一个 `FTimerManager` 对象来管理与该世界相关的定时器。`UWorld` 中的定时器通常用于在游戏逻辑中执行一些时限相关的操作，例如延迟执行某个函数、定期更新某些状态等。

# #### 特点：
# - **作用域：** 绑定到特定的 `UWorld` 实例。
# - **使用场景：** 游戏逻辑、与具体世界实例相关的任务。
# - **生命周期：** 与 `UWorld` 实例的生命周期一致。

# #### 示例代码：

# ```cpp
# // 在某个Actor中设置一个定时器
# GetWorld()->GetTimerManager().SetTimer(MyTimerHandle, this, &AMyActor::MyFunction, 1.0f, true);
# ```

# ### Engine Timer（引擎定时器）

# `UEngine` 中的定时器是引擎全局范围内的定时器。它们通常用于一些全局性的操作，如全局事件调度、引擎级别的任务管理等。与 `UWorld` 的定时器不同，引擎中的定时器不绑定到具体的世界实例。

# #### 特点：
# - **作用域：** 全局范围，不绑定到具体的 `UWorld` 实例。
# - **使用场景：** 引擎级别的任务、全局事件调度。
# - **生命周期：** 与引擎的生命周期一致。

# #### 示例代码：

# 虽然引擎级别的定时器通常不直接用于游戏逻辑，但你可以在自定义引擎模块或全局管理器中使用它们：

# ```cpp
# // 假设在一个全局管理器中使用引擎定时器
# GEngine->GetEngineTimerManager().SetTimer(MyEngineTimerHandle, this, &UGlobalManager::GlobalFunction, 1.0f, true);
# ```

# ### 主要区别总结

# 1. **作用域：**
#    - **World Timer：** 绑定到具体的 `UWorld` 实例，适用于与游戏世界相关的任务。
#    - **Engine Timer：** 全局范围，适用于引擎级别的任务。

# 2. **使用场景：**
#    - **World Timer：** 游戏逻辑、与某个世界实例相关的定时任务。
#    - **Engine Timer：** 引擎级别的任务、全局事件调度。

# 3. **生命周期：**
#    - **World Timer：** 与 `UWorld` 实例的生命周期一致。
#    - **Engine Timer：** 与引擎的生命周期一致。

# ### 何时使用哪种定时器

# - **使用 World Timer：** 当你需要在游戏逻辑中设置定时任务，并且这些任务与具体的世界实例相关时，应该使用 `UWorld` 的定时器。
# - **使用 Engine Timer：** 当你需要进行全局任务调度或引擎级别的任务管理时，可以考虑使用引擎的定时器。不过这种情况相对较少，因为大多数游戏逻辑都会与具体的世界实例相关。

# 了解这两种定时器的区别和适用场景，可以帮助你更高效地管理和调度游戏中的定时任务。
