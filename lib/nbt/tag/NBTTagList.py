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


from functools import reduce
from struct import pack

from lib.nbt import NBTNamedTag
from lib.nbt import NBTTagType


class NBTTagList(NBTNamedTag):
    _type: NBTTagType = NBTTagType.TAG_List

    def getPayload(self) -> list[NBTNamedTag]:
        return super().getPayload()

    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        content = map(lambda tag: tag.toSNBT(format, iteration + 1), self.getPayload())

        if not format:
            return '[' + ','.join(content) + ']'

        return "[\n" + ''.rjust(iteration * 2, ' ') + (",\n" + ''.rjust(iteration * 2, ' ')).join(content) + "\n" + ''.rjust((iteration - 1) * 2, ' ') + "]"

    def payloadAsBinary(self) -> bytes:
        listType = self.getAdditionalMetadata()['listType']

        return pack('>B', listType.value) + pack('>l', len(self.getPayload())) + reduce(lambda acc, bin: acc + bin, map(lambda value: value.payloadAsBinary(), self.getPayload()), b'')

    def getPayloadSize(self) -> int:

        return 1 + 4 + reduce(lambda carry, item:
                              # List elements don't have neither type nor name
                              carry + item.getPayloadSize(),
                              self.getPayload(), 0)

    def get(self, index: int) -> NBTNamedTag:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError('Index out of bounds')

        return payload[index]

    def set(self, index: int, value: NBTNamedTag) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError('Index out of bounds')

        payload[index] = value
        self.setPayload(payload)
