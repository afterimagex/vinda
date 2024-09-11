import asyncio
import threading


class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(SingletonMeta, cls).__call__(
                    *args, **kwargs
                )
        return cls._instances[cls]


class AsyncSingletonMeta(type):
    _instances = {}
    _lock = asyncio.Lock()

    async def __call__(cls, *args, **kwargs):
        async with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(AsyncSingletonMeta, cls).__call__(
                    *args, **kwargs
                )
        return cls._instances[cls]


class AsyncThreadSafeSingleton(type):
    """
    A thread-safe and coroutine-safe singleton metaclass. This metaclass ensures
    that a class has only one instance, even in a mixed environment of threads
    and asynchronous coroutines.

    To create a singleton class:

    .. code-block:: python

        class MySingleton(metaclass=AsyncThreadSafeSingleton):
            def __init__(self):
                pass

            async def async_method(self):
                async with self._async_lock:
                    # Perform async operations safely
                    await asyncio.sleep(1)
                    print("Async method executed")

            def sync_method(self):
                with self._thread_lock:
                    # Perform sync operations safely
                    print("Sync method executed")

    To use the singleton instance in a multithreaded environment:

    .. code-block:: python

        def thread_task():
            instance = MySingleton()
            instance.sync_method()

        thread = threading.Thread(target=thread_task)
        thread.start()
        thread.join()

    To use the singleton instance in an asynchronous coroutine environment:

    .. code-block:: python

        async def coroutine_task():
            instance = MySingleton()
            await instance.async_method()

        asyncio.run(coroutine_task())

    To use the singleton instance in both threads and coroutines:

    .. code-block:: python

        def main():
            thread = threading.Thread(target=thread_task)
            thread.start()
            asyncio.run(coroutine_task())
            thread.join()
    """

    _instances = {}
    _thread_lock = threading.Lock()  # Thread lock for instance creation
    _async_lock = None  # Async lock for coroutine access

    def __call__(cls, *args, **kwargs):
        # Ensure instance creation is thread-safe
        with cls._thread_lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(AsyncThreadSafeSingleton, cls).__call__(
                    *args, **kwargs
                )
                cls._instances[cls]._init_async_lock()
        return cls._instances[cls]

    def _init_async_lock(cls):
        # Initialize the async lock
        if cls._async_lock is None:
            cls._async_lock = asyncio.Lock()
