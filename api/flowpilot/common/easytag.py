from flowpilot.common.utils import SingletonMeta


class EasyTag:
    def __init__(self, tag_name: str):
        self.tag_name = tag_name
        assert self.is_valid(), f"Invalid tag name: {tag_name}"
        EasyTagManager().add_tag(self)  # 自动添加到 EasyTagManager

    def __eq__(self, other):
        if isinstance(other, EasyTag):
            return self.tag_name == other.tag_name
        return False

    def __hash__(self):
        return hash(self.tag_name)

    def __repr__(self):
        return f"EasyTag({self.tag_name})"

    def matches(self, other) -> bool:
        """Check if the tag matches another tag or a part of it."""
        return self.tag_name == other.tag_name or self.tag_name.startswith(
            other.tag_name + "."
        )

    def is_valid(self) -> bool:
        """Check if the tag is valid (non-empty and does not contain invalid characters)."""
        return (
            bool(self.tag_name)
            and ".." not in self.tag_name
            and not self.tag_name.startswith(".")
            and not self.tag_name.endswith(".")
        )

    def request_direct_parent(self):
        """Get the direct parent of the tag."""
        if "." in self.tag_name:
            parent_tag_name = self.tag_name.rsplit(".", 1)[0]
            return EasyTag(parent_tag_name)
        return None


class EasyTagContainer:
    def __init__(self, *tags):
        self.tags = set()
        for tag in tags:
            self.add_tag(tag)

    def add_tag(self, tag: EasyTag):
        self.tags.add(tag)

    def remove_tag(self, tag: EasyTag):
        self.tags.discard(tag)

    def has_tag(self, tag: EasyTag) -> bool:
        return any(existing_tag.matches(tag) for existing_tag in self.tags)

    def has_any_tags(self, tags: list[EasyTag]) -> bool:
        return any(self.has_tag(tag) for tag in tags)

    def has_all_tags(self, tags: list[EasyTag]) -> bool:
        return all(self.has_tag(tag) for tag in tags)

    def __repr__(self):
        return f"EasyTagContainer({list(self.tags)})"


class EasyTagQuery:
    def __init__(self, query_type: str, tags: list[EasyTag]):
        self.query_type = query_type
        self.tags = tags

    def matches(self, container: "EasyTagContainer") -> bool:
        if self.query_type == "ANY":
            return container.has_any_tags(self.tags)
        elif self.query_type == "ALL":
            return container.has_all_tags(self.tags)
        elif self.query_type == "NONE":
            return not container.has_any_tags(self.tags)
        else:
            raise ValueError(f"Unknown query type: {self.query_type}")

    def __repr__(self):
        return f"EasyTagQuery({self.query_type}, {self.tags})"


class EasyTagManager(metaclass=SingletonMeta):

    def __init__(self) -> None:
        if not hasattr(self, "_tags"):  # 确保只初始化一次
            self._tags = {}

    def add_tag(self, tag: EasyTag):
        if tag.tag_name not in self._tags:
            self._tags[tag.tag_name] = tag

    def get_tag(self, tag_name: str) -> EasyTag:
        return self._tags.get(tag_name, None)

    def __repr__(self):
        return f"EasyTagManager({list(self._tags.keys())})"


# Example Usage
if __name__ == "__main__":
    tag1 = EasyTag("Player.Status.Poisoned")
    tag2 = EasyTag("Player.Status.Burning")
    tag3 = EasyTag("Player.Status")
    tag4 = EasyTag("Player")

    container = EasyTagContainer()
    container.add_tag(tag1)
    container.add_tag(tag2)

    query_any = EasyTagQuery("ANY", [tag3, tag4])
    query_all = EasyTagQuery("ALL", [tag1, tag2])
    query_none = EasyTagQuery("NONE", [tag3])

    print(f"Container: {container}")
    print(
        f"Query ANY (Player.Status or Player): {query_any.matches(container)}"
    )  # Output: True
    print(
        f"Query ALL (Player.Status.Poisoned and Player.Status.Burning): {query_all.matches(container)}"
    )  # Output: True
    print(
        f"Query NONE (Player.Status): {query_none.matches(container)}"
    )  # Output: False

    print(f"All Tags: {EasyTagManager()}")
