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
from struct import unpack

from lib.nbt import NBTNamedTag, NBTTag, NBTTagType
from lib.nbt.tag import NBTTagByte, NBTTagByteArray, NBTTagCompound, NBTTagDouble, NBTTagEnd, NBTTagFloat, NBTTagInt, NBTTagIntArray, NBTTagList, NBTTagLong, NBTTagLongArray, NBTTagShort, NBTTagString
from lib.settings import settings
from lib.util import NBTException


class NBTParser:
    @staticmethod
    def parse(nbtData: bytes, iteration: int = 0) -> NBTTag:
        tagId = unpack('>B', nbtData[:1])[0]
        tag = NBTTagType(tagId)
        if tag == NBTTagType.TAG_End:
            return NBTTagEnd()

        nameLength = unpack('>H', nbtData[1:3])[0]
        name = nbtData[3:3 + nameLength].decode('utf-8')
        data = nbtData[3 + nameLength:]

        if settings.debug:
            print('> '.ljust(2 + iteration * 2, ' ') + f"Parsing tag [{tag}]" + (f" [name={name}]" if name else '') + "...")

        nbtTag = NBTParser.parseTag(tag, name, data, iteration)

        if settings.debug:
            print(('> '.ljust(2 + iteration * 2, ' ') + f"[{tag}] " + f"[name={name}] " if name else '') + "Done.")

        return nbtTag

    @staticmethod
    def parseTag(tag: NBTTagType, name: str, data: bytes, iteration: int = 0) -> NBTTag:
        payload = None

        match tag:
            # 1 byte / 8 bits, signed
            case NBTTagType.TAG_Byte:
                payload = unpack('>b', data[:1])[0]

                return NBTTagByte(name, payload)

            # 2 bytes / 16 bits, signed
            case NBTTagType.TAG_Short:
                payload = unpack('>h', data[:2])[0]

                return NBTTagShort(name, payload)

            # 4 bytes / 32 bits, signed
            case NBTTagType.TAG_Int:
                payload = unpack('>l', data[:4])[0]

                return NBTTagInt(name, payload)

            # 8 bytes / 64 bits, signed
            case NBTTagType.TAG_Long:
                payload = unpack('>q', data[:8])[0]

                return NBTTagLong(name, payload)

            # 4 bytes / 32 bits, signed, big endian, IEEE 754-2008, binary32
            case NBTTagType.TAG_Float:
                payload = unpack('>f', data[:4])[0]

                return NBTTagFloat(name, payload)

            # 8 bytes / 64 bits, signed, big endian, IEEE 754-2008, binary64
            case NBTTagType.TAG_Double:
                payload = unpack('>d', data[:8])[0]

                return NBTTagDouble(name, payload)

            # TAG_Int's payload size, then size TAG_Byte's payloads.
            case NBTTagType.TAG_Byte_Array:
                payload = []

                payloadLength = unpack('>l', data[:4])[0]

                for i in range(payloadLength):
                    payload.append(NBTParser.parseTag(NBTTagType.TAG_Byte, '', data[4 + i:4 + i + 1], iteration + 1))

                return NBTTagByteArray(name, payload)

            # A TAG_Short-like, but instead unsigned payload length, then a UTF-8 str resembled by length bytes.
            case NBTTagType.TAG_String:
                payloadLength = unpack('>H', data[:2])[0]
                payload = data[2:2 + payloadLength].decode('utf-8')

                return NBTTagString(name, payload)

            # TAG_Byte's payload tagId, then TAG_Int's payload size, then size tags' payloads, all of type tagId.
            case NBTTagType.TAG_List:
                payload = []

                subtagId = unpack('>b', data[:1])[0]
                subtag = NBTTagType(subtagId)
                payloadLength = unpack('>l', data[1:5])[0]
                payloadData = data[5:]

                j = 0
                for i in range(payloadLength):
                    data = payloadData[j:]
                    _tag = NBTParser.parseTag(subtag, '', data, iteration + 1)
                    payload.append(_tag)

                    j += _tag.getByteLength() - 1 - 2

                return NBTTagList(name, payload, {'listType': subtag})

            # Fully formed tags, followed by a TAG_End.
            case NBTTagType.TAG_Compound:
                payload = []

                i = 0
                while (_tag := NBTParser.parse(data[i:], iteration + 1)).getType() != NBTTagType.TAG_End:
                    #payload[_tag.getName()] = _tag
                    payload.append(_tag)
                    i += _tag.getByteLength()

                return NBTTagCompound(name, payload)

            # TAG_Int's payload size, then size TAG_Int's payloads.
            case NBTTagType.TAG_Int_Array:
                payload = []

                payloadLength = unpack('>l', data[:4])[0]
                for i in range(payloadLength):
                    payload.append(NBTParser.parseTag(NBTTagType.TAG_Int, '', data[4 + i * 4:4 + i * 4 + 4], iteration + 1))

                return NBTTagIntArray(name, payload)

            # TAG_Int's payload size, then size TAG_Long's payloads.
            case NBTTagType.TAG_Long_Array:
                payload = []

                payloadLength = unpack('>l', data[:4])[0]
                for i in range(payloadLength):
                    payload.append(NBTParser.parseTag(NBTTagType.TAG_Long, '', data[4 + i * 8:4 + i * 8 + 8], iteration + 1))

                return NBTTagLongArray(name, payload)

            case NBTTagType.TAG_End:
                raise NBTException("TAG_End is not a valid tag type.")

    @staticmethod
    def parseSNBT(snbtStr: str) -> NBTTag:
        snbtStr = snbtStr.strip()

        return NBTParser.parseSNBTTag(snbtStr)

    @staticmethod
    def parseSNBTTag(data: str, name: str = '', iteration: int = 0, forceType: NBTTagType | None = None) -> NBTNamedTag:
        '''
        Since this is parsing a SNBT, we can assume that no tag will be TAG_End.

        @param str data
        @param str name
        @param NBTTagType|null forceType

        @return NBTNamedTag
        '''

        length: int = len(data)

        if settings.debug:
            print('> '.ljust(2 + iteration * 2, ' ') + "Parsing tag" + (f" [name={name}]" if name else '') + "...")

        try:
            i = 0
            while data[i] == ' ' or data[i] == "\t" or data[i] == "\n" or data[i] == "\r":
                i += 1

            match (data[i]):
                case '[':
                    payload = []

                    j = i + 1
                    while (data[j] == ' ' or data[j] == "\t" or data[j] == "\n" or data[j] == "\r"):
                        j += 1

                    _tag = None
                    if ((data[j] == 'B' or data[j] == 'I' or data[j] == 'L') and data[j + 1] == ';'):
                        match (data[j]):
                            case 'B':
                                _tag = NBTTagType.TAG_Byte

                            case 'I':
                                _tag = NBTTagType.TAG_Int

                            case 'L':
                                _tag = NBTTagType.TAG_Long

                        j += 2

                    k = j
                    while data[k] != ']':
                        while (data[k] == ' ' or data[k] == "\t" or data[k] == "\n" or data[k] == "\r"):
                            k += 1

                        if data[k] == ']':
                            break

                        if data[k] == ',':
                            k += 1
                            continue

                        tag = NBTParser.parseSNBTTag(data[k:], '', iteration + 1, _tag)
                        k += tag.getAdditionalMetadata()['byteLength']

                        payload.append(tag)

                    match (data[i + 1:i + 1 + 2]):
                        case 'B':
                            return NBTTagByteArray(name, payload, {'byteLength': k - i + 4})

                        case 'I':
                            return NBTTagIntArray(name, payload, {'byteLength': k - i + 4})

                        case 'L':
                            return NBTTagLongArray(name, payload, {'byteLength': k - i + 4})

                    # Minecraft uses TAG_End for empty lists.
                    return NBTTagList(name, payload, {'listType': payload[0].getType() if len(payload) > 0 else NBTTagType.TAG_End, 'byteLength': k - i + 2})

                case '{':
                    payload = []

                    j = i + 1
                    while (data[j] != '}'):
                        while (data[j] == ' ' or data[j] == "\t" or data[j] == "\n" or data[j] == "\r"):
                            j += 1

                        if data[j] == '}':
                            break

                        if data[j] == ',':
                            j += 1
                            continue

                        if data[j] == '"':
                            j += 1
                            k = j
                            while (data[k] != '"'):
                                k += 1
                        else:
                            k = j
                            while (data[k] != ':'):
                                k += 1

                        tagName = data[j:k]
                        if data[k] == '"':
                            k += 1

                        j = k + 1
                        while (data[j] == ' ' or data[j] == "\t" or data[j] == "\n" or data[j] == "\r"):
                            j += 1

                        tag = NBTParser.parseSNBTTag(data[j:], tagName, iteration + 1)
                        j += tag.getAdditionalMetadata()['byteLength']

                        #payload[tag.getName()] = tag
                        payload.append(tag)

                    return NBTTagCompound(name, payload, {'byteLength': j - i + 2})

                case '"':
                    j = i + 1
                    while (data[j] != '"' or data[j - 1] == "\\"):
                        j += 1

                    return NBTTagString(name, data[i + 1:j], {'byteLength': j - 1 + 2})

                case "'":
                    j = i + 1
                    while (data[j] != "'" or data[j - 1] == "\\"):
                        j += 1

                    return NBTTagString(name, data[i + 1:j - 1], {'byteLength': j - 1 + 2})

                case _:
                    j = i

                    k = j + 1
                    while k < length and (data[k].isdigit() or data[k] == '-' or data[k] == '+' or data[k] == '.'):
                        k += 1

                    num = data[j:k]

                    if k < length:
                        match data[k]:
                            case 'b' | 'B':
                                return NBTTagByte(name, int(num), {'byteLength': k - j + 1})

                            case 's' | 'S':
                                return NBTTagShort(name, int(num), {'byteLength': k - j + 1})

                            case 'l' | 'L':
                                return NBTTagLong(name, int(num), {'byteLength': k - j + 1})

                            case 'f' | 'F':
                                return NBTTagFloat(name, float(num), {'byteLength': k - j + 1})

                            case 'd' | 'D':
                                return NBTTagDouble(name, float(num), {'byteLength': k - j + 1})

                    if forceType == NBTTagType.TAG_Int or forceType is None and re.match(r"[-+]?\d+$", num) is not None:
                        return NBTTagInt(name, int(num), {'byteLength': k - j})

                    return NBTTagDouble(name, float(num), {'byteLength': k - j})
        finally:
            if settings.debug:
                print('> '.ljust(2 + iteration * 2, ' ') + "" + (f"[name={name}] " if name else '') + "Done.")
