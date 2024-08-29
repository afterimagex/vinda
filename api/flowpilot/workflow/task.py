# from dataclasses import dataclass


# @dataclass
# class TaskSchema:
#     name: str = "Task"
#     description: str = ""
#     id: int = 0
#     status: bool = False
#     completed_at: str = None
#     created_at: str = None
#     updated_at: str = None
#     user_id: int = 0
#     project_id: int = 0
#     assigned_to: list = []
#     tags: list = []
#     due_date: str = None
#     reminder_time: str = None


from typing import Dict

from pydantic import BaseModel


class Test(BaseModel):

    name: Dict[str, int]

    # def __init__(self, **kwargs) -> None:
    #     super().__setattr__("name", kwargs)


if __name__ == "__main__":
    # a = Test(**{"a": 1})
    # b = Test(**{"b": 2})
    a = Test(name={"a": 1})

    # a.name = "C"
    # b.name = "123"
    print(a.__dict__)
    print("name" in a.__dict__)
    name = getattr(a, "name")
    print(name)

    # a.name_list.append("123")
    # b.name_list.append("456")

    # print(a.name_list)
    # print(b.name_list)
