import asyncio
import concurrent.futures
import functools
import json
import time
import uuid
import weakref
from abc import ABCMeta, abstractmethod
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple
from weakref import ReferenceType

from flowpilot.workflow.node import NodeBase


def get_reverse_dependencies(nodes: Iterable[NodeBase]) -> Dict[str, List[str]]:
    dependents = defaultdict(list)

    if not nodes:
        return dependents

    for node in nodes:
        for deps_node in node.get_dependencies():
            dependents[deps_node.id].append(node.id)

    return dependents


def topological_sort(nodes: Iterable[NodeBase]) -> List[str]:

    sorted_nodes = []

    if not nodes:
        return sorted_nodes

    in_degree = {node.id: len(node.get_dependencies()) for node in nodes}

    reverse_dependencies = get_reverse_dependencies(nodes)

    no_dependency_nodes = deque(
        [node_id for node_id, degree in in_degree.items() if degree == 0]
    )

    while no_dependency_nodes:
        current_node_id = no_dependency_nodes.popleft()
        sorted_nodes.append(current_node_id)

        for dependent_id in reverse_dependencies[current_node_id]:
            in_degree[dependent_id] -= 1
            if in_degree[dependent_id] == 0:
                no_dependency_nodes.append(dependent_id)

    if len(sorted_nodes) != len(nodes):
        raise ValueError("Cyclic dependency detected!")

    return sorted_nodes
