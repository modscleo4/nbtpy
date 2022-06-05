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


from enum import Enum


class NBTTagType(Enum):
    TAG_End = 0
    TAG_Byte = 1
    TAG_Short = 2
    TAG_Int = 3
    TAG_Long = 4
    TAG_Float = 5
    TAG_Double = 6
    TAG_Byte_Array = 7
    TAG_String = 8
    TAG_List = 9
    TAG_Compound = 10
    TAG_Int_Array = 11
    TAG_Long_Array = 12

    def size(self) -> int:
        if self == NBTTagType.TAG_End:
            return 0
        elif self == NBTTagType.TAG_Byte:
            return 1
        elif self == NBTTagType.TAG_Short:
            return 2
        elif self == NBTTagType.TAG_Int:
            return 4
        elif self == NBTTagType.TAG_Long:
            return 8
        elif self == NBTTagType.TAG_Float:
            return 4
        elif self == NBTTagType.TAG_Double:
            return 8

        return -1
