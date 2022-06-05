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
from lib.nbt.NBTNamedTag import NBTNamedTag
from lib.nbt.NBTTagType import NBTTagType
from lib.nbt.tag.NBTTagEnd import NBTTagEnd
from lib.util import NBTException
import re


class NBTTagCompound(NBTNamedTag):
    _type: NBTTagType = NBTTagType.TAG_Compound

    def getPayload(self) -> dict[str, NBTNamedTag]:
        return super().getPayload()


    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        payload = self.getPayload()
        content = map(lambda name: ('"' + payload[name].getName() + '"' if re.search(r'[ :]', payload[name].getName()) else payload[name].getName()) + ':' + (' ' if format else '') + payload[name].toSNBT(format, iteration + 1), payload)

        if not format:
            return '{' + ','.join(content) + '}'


        return "{\n" + ''.rjust(iteration * 2, ' ') + (",\n" + ''.rjust(iteration * 2, ' ')).join(content) + "\n" + ''.rjust((iteration - 1) * 2, ' ') + "}"


    def payloadAsBinary(self) -> bytes:
        payload = self.getPayload()
        return reduce(lambda acc, tagBytes: acc + tagBytes, map(lambda name: payload[name].toBinary(), payload), b'') + NBTTagEnd().toBinary()


    def getPayloadSize(self) -> int:
        payload = self.getPayload()
        return reduce(lambda carry, name: carry + payload[name].getByteLength(), self.getPayload(), NBTTagEnd().getByteLength())


    def keys(self) -> list:
        payload = self.getPayload()
        return map(lambda name: {"name": payload[name].getName(), "type": payload[name].getType().asString()}, payload)


    def get(self, name: str) -> NBTNamedTag:
        if not name:
            raise ArgumentError("Invalid key.")

        payload = self.getPayload()

        if name in payload:
            tag = payload[name]

            return tag

        raise NBTException(f"Tag not found: {name}")


    def set(self, name: str, value: NBTNamedTag):
        if not name:
            raise ArgumentError("Invalid key.")

        payload = self.getPayload()

        if name in payload:
            # Tag found, update its value
            payload[name] = value
            self.setPayload(payload)
            return

        # Tag not found, create a new one
        value.setName(name)
        payload[name] = value
        self.setPayload(payload)
