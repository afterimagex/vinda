import asyncio
from collections import deque


class Event:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class Workflow:
    def __init__(self):
        self.event_queue = deque()
        self.event_handlers = {}

    def register_handler(self, event_name, handler):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def emit_event(self, event):
        self.event_queue.append(event)

    async def process_events(self):
        while self.event_queue:
            event = self.event_queue.popleft()
            if event.name in self.event_handlers:
                handlers = self.event_handlers[event.name]
                await asyncio.gather(*(handler(event) for handler in handlers))


# Example handlers
async def handle_start(event):
    print(f"Handling start event: {event.data}")
    await asyncio.sleep(1)  # Simulate some work
    workflow.emit_event(Event("process", {"step": 1}))


async def handle_process(event):
    print(f"Handling process event: {event.data}")
    await asyncio.sleep(1)  # Simulate some work
    if event.data["step"] < 3:
        workflow.emit_event(Event("process", {"step": event.data["step"] + 1}))
    else:
        workflow.emit_event(Event("end", {"result": "success"}))


async def handle_end(event):
    print(f"Handling end event: {event.data}")


# Create workflow instance
workflow = Workflow()

# Register event handlers
workflow.register_handler("start", handle_start)
workflow.register_handler("process", handle_process)
workflow.register_handler("end", handle_end)

# Emit the initial event
workflow.emit_event(Event("start", {"task": "example_task"}))

# Run the event loop
asyncio.run(workflow.process_events())
