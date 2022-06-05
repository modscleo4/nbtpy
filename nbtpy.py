#!/usr/bin/python3

# A Python 3 NBT (Named Binary Tag) Parser
#
# Copyright 2022 Dhiego Cassiano Fogaça Barbosa <modscleo4@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

from __future__ import annotations

from dataclasses import dataclass
from os.path import exists
import re
import dearpygui.dearpygui as imgui
from os import path, unlink
import sys
import gzip

from lib.nbt.NBTNamedTag import NBTNamedTag
from lib.nbt.NBTParser import NBTParser
from lib.nbt.NBTUtils import NBTUtils
from lib.nbt.tag.NBTTagByte import NBTTagByte
from lib.nbt.tag.NBTTagByteArray import NBTTagByteArray
from lib.nbt.tag.NBTTagCompound import NBTTagCompound
from lib.nbt.tag.NBTTagDouble import NBTTagDouble
from lib.nbt.tag.NBTTagFloat import NBTTagFloat
from lib.nbt.tag.NBTTagInt import NBTTagInt
from lib.nbt.tag.NBTTagIntArray import NBTTagIntArray
from lib.nbt.tag.NBTTagList import NBTTagList
from lib.nbt.tag.NBTTagLong import NBTTagLong
from lib.nbt.tag.NBTTagLongArray import NBTTagLongArray
from lib.nbt.tag.NBTTagShort import NBTTagShort
from lib.nbt.tag.NBTTagString import NBTTagString

from lib.util import NBTException, __version__
from lib.settings import settings

class OpenFile:
    def __init__(self, filename: str, nbt: NBTTagCompound, snbt: bool):
        self.filename = filename
        self.nbt = nbt
        self.tags = {}
        self.snbt = snbt

open_files: dict[str, OpenFile] = {}
current_file: str = ''
can_save: bool = False

def handle_tab_change(sender: str, tab: str):
    global current_file
    current_file = tab

def parse_file(filename_full: str, filename: str, snbt: bool):
    global open_files
    global current_file
    global can_save

    if filename_full in open_files:
        return

    if snbt:
        with open(filename_full, 'r') as file:
            nbt = NBTParser.parseSNBT("\n".join(file.readlines()))
    else:
        with open(filename_full, 'rb') as file:
            nbt = NBTParser.parse(gzip.decompress(file.read()))

    if not isinstance(nbt, NBTTagCompound):
        raise NBTException("Invalid NBT file")

    open_files[filename_full] = OpenFile(filename, nbt, snbt)
    current_file = filename_full

    with imgui.tab(label=filename, tag=filename_full, parent='tab_bar', closable=True):
        parse_tag('<root>', [], nbt)

    can_save = True


def handle_open_file(sender: str, app_data, user_data):
    file_name_full = app_data['file_path_name']
    file_name = app_data['file_name']
    filter = app_data['current_filter']

    if filter == 'NBT File (*.dat) ':
        parse_file(file_name_full, file_name, False)
    elif filter == 'SNBT File (*.snbt) ':
        parse_file(file_name_full, file_name, True)


def write_file(filename_full: str, nbt: NBTTagCompound, snbt: bool):
    if snbt:
        with open(filename_full, 'w') as file:
            file.write(nbt.toSNBT())
    else:
        with open(filename_full, 'wb') as file:
            file.write(gzip.compress(nbt.toBytes(), 7))


def handle_save_file_as(sender: str, app_data, user_data):
    file_name_full = app_data['file_path_name']
    file_name = app_data['file_name']

    if sender == 'save_file_dat':
        write_file(file_name_full, open_files[current_file].nbt, False)
    elif sender == 'save_file_snbt':
        write_file(file_name_full, open_files[current_file].nbt, True)


def input_callback(id: int, b):
    global open_files
    global current_file

    tag_name = open_files[current_file].tags[id]

    nbt = open_files[current_file].nbt

    tag = NBTUtils.getWalking(nbt, tag_name)
    tag.setPayload(b)
    NBTUtils.setWalking(nbt, tag_name, tag)

    open_files[current_file].nbt = nbt


def parse_tag(name: str, full_name: list[str], tag: NBTNamedTag):
    global open_files
    global current_file

    if isinstance(tag, NBTTagCompound):
        with imgui.tree_node(label=name, selectable=True):
            for key, value in tag.getPayload().items():
                parse_tag(key, full_name + ['"' + key + '"'], value)
    elif isinstance(tag, NBTTagList) or isinstance(tag, NBTTagByteArray) or isinstance(tag, NBTTagIntArray) or isinstance(tag, NBTTagLongArray):
        with imgui.tree_node(label=name, selectable=True, bullet=True):
            for index, value in enumerate(tag.getPayload()):
                parse_tag(f"[{index}]", full_name + ['[' + str(index) + ']'], value)
    else:
        if isinstance(tag, NBTTagInt):
            tag_id = imgui.add_input_int(label=name, default_value=tag.getPayload(), width=250, callback=input_callback)
        elif isinstance(tag, NBTTagShort):
            tag_id = imgui.add_input_int(label=name, min_value=-32768, max_value=32767, min_clamped=True, max_clamped=True, default_value=tag.getPayload(), width=250, callback=input_callback)
        elif isinstance(tag, NBTTagByte):
            tag_id = imgui.add_input_int(label=name, min_value=-128, max_value=127, min_clamped=True, max_clamped=True, default_value=tag.getPayload(), width=250, callback=input_callback)
        elif isinstance(tag, NBTTagLong):
            tag_id = imgui.add_input_text(label=name, default_value=str(tag.getPayload()), width=250, hexadecimal=True, callback=input_callback)
        elif isinstance(tag, NBTTagFloat):
            tag_id = imgui.add_input_float(label=name, default_value=tag.getPayload(), width=250, callback=input_callback)
        elif isinstance(tag, NBTTagDouble):
            tag_id = imgui.add_input_double(label=name, default_value=tag.getPayload(), width=250, callback=input_callback)
        elif isinstance(tag, NBTTagString):
            tag_id = imgui.add_input_text(label=name, default_value=tag.getPayload(), width=250, callback=input_callback)
        else:
            raise NBTException(f"Unknown tag type: {tag.__class__.__name__}")

        open_files[current_file].tags[tag_id] = full_name


def open_file():
    imgui.show_item('open_file')


def save_file():
    global open_files
    global current_file
    global can_save

    if not can_save:
        return

    file = open_files[current_file]

    write_file(current_file, file.nbt, file.snbt)


def save_file_as_dat():
    global can_save

    if not can_save:
        return

    imgui.show_item('save_file_dat')


def save_file_as_snbt():
    global can_save

    if not can_save:
        return

    imgui.show_item('save_file_snbt')


def save_settings():
    imgui.save_init_file('nbtpy.ini')


def exit():
    imgui.destroy_context()
    sys.exit(0)


def main() -> int:
    global can_save

    imgui.create_context()
    if exists('nbtpy.ini'):
        imgui.configure_app(init_file='nbtpy.ini')

    imgui.create_viewport(title='NBT.py', width=800, height=600)

    with imgui.window(tag='main'):
        with imgui.menu_bar():
            with imgui.menu(label='File'):
                imgui.add_menu_item(label='Open', callback=open_file, shortcut='Ctrl+O')
                imgui.add_menu_item(label='Save', callback=save_file, shortcut='Ctrl+S')
                with imgui.menu(label='Save as...'):
                    imgui.add_menu_item(label='NBT', callback=save_file_as_dat)
                    imgui.add_menu_item(label='SNBT', callback=save_file_as_snbt)

                imgui.add_separator()
                imgui.add_menu_item(label='Exit', callback=exit, shortcut='Ctrl+Q')

        with imgui.tab_bar(tag='tab_bar', callback=handle_tab_change, reorderable=True):
            pass

    with imgui.file_dialog(directory_selector=False, show=False, default_filename='', callback=handle_open_file, modal=True, height=400, id="open_file"):
        imgui.add_file_extension("NBT File (*.dat) {.dat}")
        imgui.add_file_extension("SNBT File (*.snbt) {.snbt}")

    with imgui.file_dialog(directory_selector=False, show=False, default_filename='', callback=handle_save_file_as, modal=True, height=400, id="save_file_dat"):
        imgui.add_file_extension("NBT File (*.dat) {.dat}")

    with imgui.file_dialog(directory_selector=False, show=False, default_filename='', callback=handle_save_file_as, modal=True, height=400, id="save_file_snbt"):
        imgui.add_file_extension("SNBT File (*.snbt) {.snbt}")

    imgui.setup_dearpygui()
    imgui.show_viewport()
    imgui.set_primary_window('main', True)
    imgui.set_exit_callback(save_settings)
    imgui.start_dearpygui()

    exit()


if __name__ == '__main__':
    main()
