# A Python 3 NBT (Named Binary Tag) Parser
#
# Copyright 2022 Dhiego Cassiano Fogaça Barbosa <modscleo4@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re

from lib.nbt import NBTNamedTag
from lib.nbt.tag import NBTTagByteArray, NBTTagCompound, NBTTagIntArray, NBTTagList, NBTTagLongArray
from lib.settings import settings


class NBTUtils:
    @staticmethod
    def getWalking(tag: NBTTagCompound | NBTTagList | NBTTagByteArray | NBTTagIntArray | NBTTagLongArray, key: str) -> NBTNamedTag:
        if isinstance(key, str):
            parts = list(filter(None, re.split(r'(\[[^\]]*\])|("[^"]*")|\.+', key)))
        else:
            parts = key

        current = tag

        for part in parts:
            part = part.strip('"')

            if settings.debug:
                print(f"Part: {part}")

            if re.match(r'^\[(\d+)\]$', part):
                if not part[1:-1].isdigit():
                    raise ValueError(f"Invalid index: '{part}'")

                index = int(part[1:-1])

                if not isinstance(current, NBTTagList) and not isinstance(current, NBTTagByteArray) and not isinstance(current, NBTTagIntArray) and not isinstance(current, NBTTagLongArray):
                    raise ValueError(f"Cannot access index '{index}' on non-list tag")

                current = current.get(index)
            else:
                if not isinstance(current, NBTTagCompound):
                    raise ValueError(f"Cannot access key '{part}' on non-compound tag")

                current = current.get(part)

        return current

    @staticmethod
    def setWalking(tag: NBTTagCompound | NBTTagList | NBTTagByteArray | NBTTagIntArray | NBTTagLongArray, key: str | list[str], value: NBTNamedTag) -> NBTNamedTag:
        if isinstance(key, str):
            parts = list(filter(None, re.split(r'(\[[^\]]*\])|("[^"]*")|\.+', key)))
        else:
            parts = key

        last = parts[-1].strip('"')
        parts = parts[:-1]

        current = tag

        for part in parts:
            part = part.strip('"')

            if settings.debug:
                print(f"Part: {part}")

            if re.match(r'^\[(\d+)\]$', part):
                if not part[1:-1].isdigit():
                    raise ValueError(f"Invalid index: '{part}'")

                index = int(part[1:-1])

                if not isinstance(current, NBTTagList) and not isinstance(current, NBTTagByteArray) and not isinstance(current, NBTTagIntArray) and not isinstance(current, NBTTagLongArray):
                    raise ValueError(f"Cannot access index '{index}' on non-list tag")

                current = current.get(index)
            else:
                if not isinstance(current, NBTTagCompound):
                    raise ValueError(f"Cannot access key '{part}' on non-compound tag")

                current = current.get(part)

        if re.match(r'^\[(\d+)\]$', last):
            if not part[1:-1].isdigit():
                raise ValueError(f"Invalid index: '{part}'")

            index = int(last[1:-1])

            if not isinstance(current, NBTTagList) and not isinstance(current, NBTTagByteArray) and not isinstance(current, NBTTagIntArray) and not isinstance(current, NBTTagLongArray):
                raise ValueError(f"Cannot access index '{index}' on non-list tag")

            current = current.set(index, value)
        else:
            if not isinstance(current, NBTTagCompound):
                raise ValueError(f"Cannot access key '{last}' on non-compound tag")

            current = current.set(last, value)
