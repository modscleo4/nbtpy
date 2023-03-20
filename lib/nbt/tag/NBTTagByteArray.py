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

from lib.nbt import NBTNamedTag, NBTTagType
from lib.nbt.tag import NBTTagByte


class NBTTagByteArray(NBTNamedTag):
    _type: NBTTagType = NBTTagType.TAG_Byte_Array

    def getPayload(self) -> list[NBTTagByte]:
        return super().getPayload()

    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        if not format:
            return '[B;' + ','.join(map(lambda value: value.toSNBT(format, iteration), self.getPayload())) + ']'

        return "[B;\n" + ''.rjust(iteration * 2, ' ') + (",\n" + ''.rjust(iteration * 2, ' ')).join(map(lambda value: value.toSNBT(format, iteration), self.getPayload())) + "\n" + ''.rjust((iteration - 1) * 2, ' ') + "]"

    def payloadAsBinary(self) -> bytes:
        return (pack('>l', len(self.getPayload()))) + reduce(lambda acc, bin: acc + bin, map(lambda value: value.payloadAsBinary(), self.getPayload()), b'')

    def getPayloadSize(self) -> int:
        return 4 + len(self.getPayload())

    def get(self, index: int) -> NBTTagByte:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        return payload[index]

    def set(self, index: int, value: NBTTagByte) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        payload[index] = value
        self.setPayload(payload)

    def add(self, value: NBTTagByte) -> None:
        payload = self.getPayload()
        payload.append(value)
        self.setPayload(payload)

    def remove(self, index: int) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        payload.pop(index)
        self.setPayload(payload)

    def __len__(self) -> int:
        return len(self.getPayload())
