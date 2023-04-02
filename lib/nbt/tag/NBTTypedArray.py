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
from typing import TypeVar, Generic

from lib.nbt import NBTNamedTag


T = TypeVar('T', bound=NBTNamedTag)


class NBTTypedArray(NBTNamedTag[list[T]], Generic[T]):
    _prefix: str = ''

    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        payload = self.getPayload()

        if not format:
            return f'[{self._prefix};' + ','.join([value.toSNBT(format, iteration) for value in payload]) + ']'

        return f"[{self._prefix};\n" + ''.rjust(iteration * 2, ' ') + (",\n" + ''.rjust(iteration * 2, ' ')).join([value.toSNBT(format, iteration) for value in payload]) + "\n" + ''.rjust((iteration - 1) * 2, ' ') + "]"

    def payloadAsBinary(self) -> bytes:
        payload = self.getPayload()
        return pack('>l', len(payload)) + b''.join([value.payloadAsBinary() for value in payload])

    def getPayloadSize(self) -> int:
        return 4 + sum([value.getPayloadSize() for value in self.getPayload()])

    def get(self, index: int) -> T:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        return payload[index]

    def set(self, index: int, value: T) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        payload[index] = value

    def add(self, value: T) -> None:
        payload = self.getPayload()
        payload.append(value)

    def remove(self, index: int) -> None:
        payload = self.getPayload()
        if (index < 0 or index >= len(payload)):
            raise IndexError(f'Index out of bounds: {index}')

        payload.pop(index)

    def __len__(self) -> int:
        return len(self.getPayload())

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __setitem__(self, index: int, value: T) -> None:
        self.set(index, value)

    def __delitem__(self, index: int) -> None:
        self.remove(index)

    def __iadd__(self, value: T):
        self.add(value)
        return self

    def __iter__(self):
        return iter(self.getPayload())

    def __reversed__(self):
        return reversed(self.getPayload())

    def __contains__(self, value: T) -> bool:
        return value in self.getPayload()
