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
from struct import pack
from typing import TypeVar, Generic

from lib.nbt import NBTTag


T = TypeVar('T')


class NBTNamedTag(NBTTag, Generic[T]):
    def __init__(self, name: str = '', payload: T = None, additionalMetadata: dict = {}):
        self._name = name
        self._payload = payload
        self._additionalMetadata = dict(additionalMetadata)

    def getName(self) -> str:
        return self._name

    def setName(self, name: str):
        self._name = name

    def getPayload(self) -> T:
        return self._payload

    def setPayload(self, payload: T):
        self._payload = payload

    def getAdditionalMetadata(self) -> dict:
        return self._additionalMetadata

    def getPayloadSize(self) -> int:
        return self.getType().size()

    def getByteLength(self) -> int:
        return 1 + 2 + len(self.getName() or "") + self.getPayloadSize()

    @abstractmethod
    def payloadAsBinary(self) -> bytes:
        pass

    def toBinary(self) -> bytes:
        nameEncoded = self.getName().encode('utf-8') or b''
        return pack('>B', self.getType().value) + pack('>H', len(nameEncoded)) + nameEncoded + self.payloadAsBinary()
