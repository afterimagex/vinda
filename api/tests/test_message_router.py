import unittest

from flowpilot.common.easytag import EasyTag
from flowpilot.universe.core.message_router import MessageSubsystem


class Node:
    def __init__(self):
        MessageSubsystem().register_listener(EasyTag("node"), self.on_message)

    def on_message(self, x, y):
        pass


class TestMessageSubsystem(unittest.TestCase):

    def test_func(self):
        router = MessageSubsystem()

        def on_message(x, y):
            self.assertEqual(x, 0)
            self.assertEqual(y, "0")

        handle = router.register_listener(EasyTag("test1"), on_message)
        self.assertEqual(EasyTag("test1") in router._listener_map, True)
        router.broadcast_message(EasyTag("test1"), 0, "0")
        handle.unregister()
        self.assertEqual(len(router._listener_map), 0)

    def test_object(self):
        router = MessageSubsystem()
        node = Node()
        node = Node()
        self.assertEqual(EasyTag("node") in router._listener_map, True)
        router.broadcast_message(EasyTag("test1"), 0, "0")
        router.unregister_listener(EasyTag("node"), 1)
        self.assertEqual(len(router._listener_map), 1)


if __name__ == "__main__":
    unittest.main()
