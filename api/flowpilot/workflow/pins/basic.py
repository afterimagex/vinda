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

from .base import Pin
from .factory import UPIN


@UPIN()
class ExecPin(Pin):
    pass


@UPIN()
class AnyPin(Pin):
    pass


@UPIN()
class StringPin(Pin):
    pass


@UPIN()
class IntegerPin(Pin):
    pass


@UPIN()
class FloatPin(Pin):
    pass


@UPIN()
class BooleanPin(Pin):
    pass


@UPIN()
class ObjectPin(Pin):
    pass


@UPIN()
class ListPin(Pin):
    pass


@UPIN()
class DictPin(Pin):
    pass
