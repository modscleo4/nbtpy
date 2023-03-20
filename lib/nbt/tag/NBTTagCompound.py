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


from argparse import ArgumentError
from functools import reduce
import re

from lib.nbt import NBTNamedTag, NBTTagType
from lib.nbt.tag import NBTTagEnd
from lib.util import NBTException


class NBTTagCompound(NBTNamedTag):
    _type: NBTTagType = NBTTagType.TAG_Compound

    def getPayload(self) -> list[NBTNamedTag]:
        return super().getPayload()

    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        payload = self.getPayload()
        content = map(lambda tag: ('"' + tag.getName() + '"' if re.search(r'[ :]', tag.getName()) else tag.getName()) + ':' + (' ' if format else '') + tag.toSNBT(format, iteration + 1), payload)

        if not format:
            return '{' + ','.join(content) + '}'

        return "{\n" + ''.rjust(iteration * 2, ' ') + (",\n" + ''.rjust(iteration * 2, ' ')).join(content) + "\n" + ''.rjust((iteration - 1) * 2, ' ') + "}"

    def payloadAsBinary(self) -> bytes:
        payload = self.getPayload()
        return reduce(lambda acc, tagBytes: acc + tagBytes, map(lambda tag: tag.toBinary(), payload), b'') + NBTTagEnd().toBinary()

    def getPayloadSize(self) -> int:
        payload = self.getPayload()
        return reduce(lambda carry, tag: carry + tag.getByteLength(), payload, NBTTagEnd().getByteLength())

    def keys(self) -> list[dict[str, str]]:
        payload = self.getPayload()
        return [{"name": tag.getName(), "type": tag.getType().name} for tag in payload]

    def get(self, name: str) -> NBTNamedTag:
        if not name:
            raise ArgumentError(None, message="Invalid key.")

        payload = self.getPayload()

        if name in payload:
            tag = payload[name]

            return tag

        raise NBTException(f"Tag not found: {name}")

    def set(self, name: str, value: NBTNamedTag):
        if not name:
            raise ArgumentError(None, message="Invalid key.")
        elif value is None:
            raise ArgumentError(None, message="Invalid value.")

        payload = self.getPayload()

        for i in range(len(payload)):
            if payload[i].getName() == name:
                # Tag found, update its value
                payload[i] = value
                return

        raise NBTException(f"Tag not found: {name}")

    def has(self, name: str) -> bool:
        if not name:
            raise ArgumentError(None, message="Invalid key.")

        payload = self.getPayload()
        for tag in payload:
            if tag.getName() == name:
                return True

        return False

    def add(self, value: NBTNamedTag):
        if value is None:
            raise ArgumentError(None, message="Invalid value.")

        payload = self.getPayload()

        if value.getName() in payload:
            raise NBTException(f"Tag already exists: {value.getName()}")

        payload.append(value)

    def remove(self, name: str):
        if not name:
            raise ArgumentError(None, message="Invalid key.")

        payload = self.getPayload()

        for i in range(len(payload)):
            if payload[i].getName() == name:
                # Tag found, remove it
                del payload[i]
                return

        raise NBTException(f"Tag not found: {name}")
