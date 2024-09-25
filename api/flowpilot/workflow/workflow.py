class CustomNode:
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print(f"Executing {func.__name__} with args: {args} and kwargs: {kwargs}")
            result = func(*args, **kwargs)
            print(f"Result of {func.__name__}: {result}")
            return result

        return wrapper

    def execute(self, context, event):
        return


class Workflow:
    def __init__(self):
        pass

    @CustomNode()
    def retrive(ctx: Context, ev: StartEvent):
        if not ev.get("query"):
            return None

        return RetrieverEvent()
