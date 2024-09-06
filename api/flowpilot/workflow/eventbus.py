import asyncio
from collections import defaultdict


class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)

    async def publish(self, event_type, data):
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                await handler(data)


# 事件处理函数
async def handle_order_created(data):
    print(f"Order Created: {data}")
    await asyncio.sleep(1)  # 模拟处理时间
    await event_bus.publish(
        "inventory_checked", {"order_id": data["order_id"], "inventory_ok": True}
    )


async def handle_inventory_checked(data):
    print(f"Inventory Checked: {data}")
    await asyncio.sleep(1)  # 模拟处理时间
    await event_bus.publish(
        "payment_processed", {"order_id": data["order_id"], "payment_success": True}
    )


async def handle_payment_processed(data):
    print(f"Payment Processed: {data}")
    await asyncio.sleep(1)  # 模拟处理时间
    await event_bus.publish(
        "order_confirmed", {"order_id": data["order_id"], "confirmed": True}
    )


async def handle_order_confirmed(data):
    print(f"Order Confirmed: {data}")


# 创建事件总线
event_bus = EventBus()

# 订阅事件
event_bus.subscribe("order_created", handle_order_created)
event_bus.subscribe("inventory_checked", handle_inventory_checked)
event_bus.subscribe("payment_processed", handle_payment_processed)
event_bus.subscribe("order_confirmed", handle_order_confirmed)


# 模拟订单创建事件
async def main():
    await event_bus.publish("order_created", {"order_id": 1})


# 运行事件循环
asyncio.run(main())
