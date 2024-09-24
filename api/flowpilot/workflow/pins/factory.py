# ------------------------------------------------------------------------
# Copyright (c) 2017-present, Pvening. All Rights Reserved.
#
# Licensed under the BSD 2-Clause License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://opensource.org/licenses/BSD-2-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

from typing import Any, Optional, TypeVar

from flowpilot.common.registry import Registry

from .base import Direction, Pin

T = TypeVar("T", bound="Pin")

PIN_REGISTRY = Registry("PIN")
PIN_REGISTRY.__doc__ = """
Registry for operators, which extract feature maps from images

The registered object must be a callable that accepts two arguments:

1. A :class:`name`
2. A :class:`metadata`

Registered object must return instance of :class:`NodeBase`.
"""


def UPIN():

    def deco(pin_class: T) -> T:
        PIN_REGISTRY.register(pin_class)
        return pin_class

    return deco


def new_pin(
    pin_class: str,
    name: Optional[str] = None,
    direction: Direction = Direction.INPUT,
    *args,
    **kwargs
) -> T:
    """
    Build a operator from `pin_class`.

    Returns:
        an instance of :class:`GNode`
    """

    pin = PIN_REGISTRY.get(pin_class)(name, direction, *args, **kwargs)
    assert isinstance(pin, Pin)
    return pin
