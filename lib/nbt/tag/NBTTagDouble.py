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
from lib.nbt.NBTNamedTag import NBTNamedTag
from lib.nbt.NBTTagType import NBTTagType


class NBTTagDouble(NBTNamedTag):
    _type: NBTTagType = NBTTagType.TAG_Double

    def getPayload(self) -> float:
        return super().getPayload()


    def toSNBT(self, format: bool = True, iteration: int = 1) -> str:
        return f"{self.getPayload()}d"


    def payloadAsBinary(self) -> bytes:
        return pack('>d', self.getPayload())
