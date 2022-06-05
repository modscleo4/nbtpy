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

from lib.nbt.NBTTag import NBTTag


class NBTNamedTag(NBTTag):
    _name: str = ''
    _payload: object = None
    _additionalMetadata: dict = {}

    def __init__(self, name: str = '', payload = None, additionalMetadata: dict = {}):
        self._name = name
        self._payload = payload
        self._additionalMetadata = additionalMetadata


    def getName(self):
        return self._name


    def setName(self, name: str):
        self._name = name


    def getPayload(self):
        return self._payload


    def setPayload(self, payload):
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
        return pack('>C', self.getType().value) + pack('>n', len(self.getName() or "")) + bytes(self.getName(), 'utf-8') + self.payloadAsBinary()
