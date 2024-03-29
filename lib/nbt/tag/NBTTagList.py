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


from struct import pack

from lib.nbt import NBTNamedTag
from lib.nbt import NBTTagType


class NBTTagList(NBTNamedTag[list[NBTNamedTag]]):
    _type: NBTTagType = NBTTagType.TAG_List
    _listType: NBTTagType = NBTTagType.TAG_End

    def __init__(self, name: str, payload: list[NBTNamedTag] = [], listType: NBTTagType = NBTTagType.TAG_End, additionalMetadata: dict = {}):
        super().__init__(name, list(payload), additionalMetadata)
        self._listType = listType

    def getListType(self) -> NBTTagType:
        return self._listType

    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        payload = self.getPayload()
        content = [tag.toSNBT(format, iteration + 1) for tag in payload]

        if not format:
            return '[' + ','.join(content) + ']'

        return "[\n" + ''.rjust(iteration * 2, ' ') + (",\n" + ''.rjust(iteration * 2, ' ')).join(content) + "\n" + ''.rjust((iteration - 1) * 2, ' ') + "]"

    def payloadAsBinary(self) -> bytes:
        payload = self.getPayload()
        return pack('>B', self.getListType().value) + pack('>l', len(payload)) + b''.join([value.payloadAsBinary() for value in payload])

    def getPayloadSize(self) -> int:
        payload = self.getPayload()
        return 1 + 4 + sum([item.getPayloadSize() for item in payload])

    def get(self, index: int) -> NBTNamedTag:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        return payload[index]

    def set(self, index: int, value: NBTNamedTag) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')
        elif (self.getListType() != value.getType()):
            raise TypeError('The list type is ' + self.getListType().name + ' but the value type is ' + value.getType().name)

        payload[index] = value

    def add(self, value: NBTNamedTag) -> None:
        if (self.getListType() != value.getType()):
            raise TypeError('The list type is ' + self.getListType().name + ' but the value type is ' + value.getType().name)

        payload = self.getPayload()
        payload.append(value)

    def remove(self, index: int) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        del payload[index]

    def __len__(self) -> int:
        return len(self.getPayload())

    def __getitem__(self, index: int) -> NBTNamedTag:
        return self.get(index)

    def __setitem__(self, index: int, value: NBTNamedTag) -> None:
        self.set(index, value)

    def __delitem__(self, index: int) -> None:
        self.remove(index)

    def __iadd__(self, value: NBTNamedTag):
        self.add(value)
        return self

    def __iter__(self):
        return iter(self.getPayload())

    def __reversed__(self):
        return reversed(self.getPayload())

    def __contains__(self, value: NBTNamedTag) -> bool:
        return value in self.getPayload()
