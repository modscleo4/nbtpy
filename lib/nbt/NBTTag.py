# A Python 3 NBT (Named Binary Tag) Parser
#
# Copyright 2022 Dhiego Cassiano Fogaça Barbosa <modscleo4@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from abc import abstractmethod

from lib.settings import settings
from lib.nbt import NBTTagType


class NBTTag:
    _type: NBTTagType

    def getType(self) -> NBTTagType:
        return self._type

    def getTypeName(self) -> str:
        return self._type.name

    @abstractmethod
    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        pass

    @abstractmethod
    def toBinary(self) -> bytes:
        pass

    def __str__(self):
        return self.toSNBT(settings.format)

    def getByteLength(self) -> int:
        return self._type.size()
