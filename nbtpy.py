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
import dearpygui.dearpygui as imgui
import sys
import gzip

from lib.nbt import NBTNamedTag, NBTParser, NBTTagType
from lib.nbt.tag import NBTTagByte, NBTTagByteArray, NBTTagCompound, NBTTagDouble, NBTTagFloat, NBTTagInt, NBTTagIntArray, NBTTagList, NBTTagLong, NBTTagLongArray, NBTTagShort, NBTTagString

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
clipboard: NBTNamedTag | None = None


def handle_tab_change(sender: str, tab: str):
    global current_file
    current_file = tab


def handle_tab_close(tab: str):
    global open_files
    global current_file
    global can_save

    if tab == current_file:
        current_file = ''

    del open_files[tab]

    if len(open_files) == 0:
        can_save = False


def parse_file(filename_full: str, filename: str, snbt: bool):
    global open_files
    global current_file
    global can_save

    if filename_full in open_files:
        # Check if the tab is closed
        if imgui.is_item_visible(filename_full):
            return
        elif imgui.does_item_exist(filename_full):
            imgui.delete_item(filename_full)

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
        with imgui.child_window():
            parse_tag('<root>', nbt)

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
            file.write(gzip.compress(nbt.toBinary(), 7))


def handle_save_file_as(sender: str, app_data, user_data):
    file_name_full = app_data['file_path_name']
    file_name = app_data['file_name']

    if sender == 'save_file_dat':
        if not file_name_full.endswith('.dat'):
            file_name_full += '.dat'
        write_file(file_name_full, open_files[current_file].nbt, False)
    elif sender == 'save_file_snbt':
        if not file_name_full.endswith('.snbt'):
            file_name_full += '.snbt'
        write_file(file_name_full, open_files[current_file].nbt, True)


def input_callback(sender: int | str, value: str, data: tuple[NBTNamedTag, str]):
    tag, name = data

    if tag is None:
        return

    tag.setPayload(value)


def rename_tag(sender: int | str, __, data: tuple[NBTNamedTag, int | str, NBTNamedTag | None, int | str | None]):
    tag, container_tag, parent_tag, parent_id = data

    if not parent_tag:
        return
    elif not isinstance(parent_tag, NBTTagCompound):
        raise NBTException('Cannot rename tags not in a compound tag.')

    def do_rename(new_name):
        if not new_name:
            message_box('Error', 'Tag name cannot be empty.')
            return
        elif parent_tag.has(new_name):
            message_box('Error', f'A tag with the name "{new_name}" already exists.')
            return

        tag.setName(new_name)

        imgui.configure_item(container_tag, label=new_name)

    input_box('Rename Tag', 'New name:', do_rename, default_value=tag.getName())


def delete_tag(sender: int | str, __, data: tuple[NBTNamedTag, int | str, NBTNamedTag | None, int | str | None]):
    tag, container_tag, parent_tag, parent_id = data

    tag_name = imgui.get_item_label(container_tag)
    if not tag_name:
        return

    if isinstance(parent_tag, NBTTagCompound):
        parent_tag.remove(tag.getName())
    elif isinstance(parent_tag, NBTTagList) or isinstance(parent_tag, NBTTagByteArray) or isinstance(parent_tag, NBTTagIntArray) or isinstance(parent_tag, NBTTagLongArray):
        index = int(tag_name[1:-1])
        parent_tag.remove(index)
        if parent_id is not None:
            children = imgui.get_item_children(parent_id, slot=1)
            if children:
                for i in range(index, len(children)):
                    imgui.configure_item(children[i], label=f'[{i - 1}]')

    imgui.delete_item(container_tag)


def copy_clipboard(sender: int | str, __, data: tuple[NBTNamedTag]):
    global clipboard

    tag, = data

    print(f'Copying {tag.getName()} to clipboard...')

    clipboard = tag


def paste_clipboard(sender: int | str, __, data: tuple[NBTNamedTag, int | str]):
    global clipboard

    parent_tag, container_id = data

    if clipboard is None:
        message_box('Error', 'Nothing to paste')
        return

    tag_name = clipboard.getName()

    if isinstance(parent_tag, NBTTagByteArray):
        if not isinstance(clipboard, NBTTagByte):
            message_box('Error', f'Cannot paste {clipboard.getTypeName()} into byte array.')
            return

        parent_tag.add(clipboard)
        tag_name = f'[{len(parent_tag) - 1}]'
    elif isinstance(parent_tag, NBTTagIntArray):
        if not isinstance(clipboard, NBTTagInt):
            message_box('Error', f'Cannot paste {clipboard.getTypeName()} into int array.')
            return

        parent_tag.add(clipboard)
        tag_name = f'[{len(parent_tag) - 1}]'
    elif isinstance(parent_tag, NBTTagLongArray):
        if not isinstance(clipboard, NBTTagLong):
            message_box('Error', f'Cannot paste {clipboard.getTypeName()} into long array.')
            return

        parent_tag.add(clipboard)
        tag_name = f'[{len(parent_tag) - 1}]'
    elif isinstance(parent_tag, NBTTagList):
        if clipboard.getType() != parent_tag.getListType():
            message_box('Error', f'Cannot paste {clipboard.getTypeName()} into this tag.')
            return

        parent_tag.add(clipboard)
        tag_name = f'[{len(parent_tag) - 1}]'
    elif isinstance(parent_tag, NBTTagCompound):
        if parent_tag.has(clipboard.getName()):
            message_box('Error', f'Cannot paste {clipboard.getName()} into this tag. A tag with that name already exists.')
            return

        parent_tag.add(clipboard)

    parse_tag(tag_name, clipboard, isinstance(parent_tag, NBTTagCompound), parent_tag, container_id)


def add_tag(sender: int | str, __, data: tuple[NBTNamedTag, NBTTagType, int | str]):
    parent_tag, new_tag, container_id = data

    if settings.debug:
        print(f"Adding {new_tag.name} to '{parent_tag.getName()}'...")

    def create_tag(tag_name: str, tag_type: NBTTagType):
        match tag_type:
            case NBTTagType.TAG_Byte:
                return NBTTagByte(tag_name, 0)
            case NBTTagType.TAG_Short:
                return NBTTagShort(tag_name, 0)
            case NBTTagType.TAG_Int:
                return NBTTagInt(tag_name, 0)
            case NBTTagType.TAG_Long:
                return NBTTagLong(tag_name, 0)
            case NBTTagType.TAG_Float:
                return NBTTagFloat(tag_name, 0.0)
            case NBTTagType.TAG_Double:
                return NBTTagDouble(tag_name, 0.0)
            case NBTTagType.TAG_Byte_Array:
                return NBTTagByteArray(tag_name, [])
            case NBTTagType.TAG_String:
                return NBTTagString(tag_name, '')
            case NBTTagType.TAG_List:
                return NBTTagList(tag_name, [])
            case NBTTagType.TAG_Compound:
                return NBTTagCompound(tag_name, [])
            case NBTTagType.TAG_Int_Array:
                return NBTTagIntArray(tag_name, [])
            case NBTTagType.TAG_Long_Array:
                return NBTTagLongArray(tag_name, [])

        raise ValueError(f'Unknown tag type: {tag_type}')

    if isinstance(parent_tag, NBTTagCompound):
        def add_tag(tag: NBTNamedTag):
            print(f'Adding {tag.getName()} ({tag.getTypeName()}) to {parent_tag.getName()}...')
            parent_tag.add(tag)

            parse_tag(tag.getName(), tag, True, parent_tag, container_id)

        def do_add(new_name: str):
            if not new_name:
                message_box('Error', 'Tag name cannot be empty.')
                return
            elif parent_tag.has(new_name):
                message_box('Error', f'A tag with the name "{new_name}" already exists.')
                return

            if new_tag == NBTTagType.TAG_List:
                def do_list(list_type: str):
                    if not list_type:
                        message_box('Error', 'List type cannot be empty.')
                        return

                    tag = NBTTagList(new_name, [], {'listType': NBTTagType[list_type]})
                    add_tag(tag)

                combo_box('List Type', 'Select list type:', [t.name for t in NBTTagType if t != NBTTagType.TAG_End], do_list)
            else:
                tag = create_tag(new_name, new_tag)
                add_tag(tag)

        input_box('Add Tag', 'Tag name:', do_add)
    elif isinstance(parent_tag, NBTTagList):
        tag = create_tag('', new_tag)
        parent_tag.add(tag)

        parse_tag(f'[{len(parent_tag) - 1}]', tag, False, parent_tag, container_id)
    elif isinstance(parent_tag, NBTTagByteArray):
        tag = NBTTagByte('', 0)
        parent_tag.add(tag)

        parse_tag(f'[{len(parent_tag) - 1}]', tag, False, parent_tag, container_id)
    elif isinstance(parent_tag, NBTTagIntArray):
        tag = NBTTagInt('', 0)
        parent_tag.add(tag)

        parse_tag(f'[{len(parent_tag) - 1}]', tag, False, parent_tag, container_id)
    elif isinstance(parent_tag, NBTTagLongArray):
        tag = NBTTagLong('', 0)
        parent_tag.add(tag)

        parse_tag(f'[{len(parent_tag) - 1}]', tag, False, parent_tag, container_id)


def move_tag(sender: int | str):
    pass


def parse_tag(name: str, tag: NBTNamedTag, allow_rename: bool = False, parent_tag: NBTNamedTag | None = None, parent_id: int | str | None = None):
    global open_files
    global current_file
    global clipboard

    enable_paste: bool = False
    valid_new_tags: list[NBTTagType | None] = []

    if isinstance(tag, NBTTagCompound):
        with imgui.tree_node(parent=parent_id if parent_id is not None else 0, label=name, selectable=True, default_open=parent_id is None, payload_type=tag.getTypeName(), drop_callback=move_tag):
            imgui_id = imgui.last_item()

            enable_paste = True
            valid_new_tags = [
                NBTTagType.TAG_Byte,
                NBTTagType.TAG_Short,
                NBTTagType.TAG_Int,
                NBTTagType.TAG_Long,
                NBTTagType.TAG_Float,
                NBTTagType.TAG_Double,
                NBTTagType.TAG_String,
                None,
                NBTTagType.TAG_List,
                NBTTagType.TAG_Compound,
                None,
                NBTTagType.TAG_Byte_Array,
                NBTTagType.TAG_Int_Array,
                NBTTagType.TAG_Long_Array,
            ]

            for value in tag.getPayload():
                parse_tag(value.getName(), value, allow_rename=True, parent_tag=tag, parent_id=imgui_id)
    elif isinstance(tag, NBTTagList) or isinstance(tag, NBTTagByteArray) or isinstance(tag, NBTTagIntArray) or isinstance(tag, NBTTagLongArray):
        with imgui.tree_node(parent=parent_id if parent_id is not None else 0, label=name, selectable=True, bullet=True, payload_type=tag.getTypeName()):
            imgui_id = imgui.last_item()

            enable_paste = True
            if isinstance(tag, NBTTagList):
                valid_new_tags = [tag.getListType()]
            elif isinstance(tag, NBTTagByteArray):
                valid_new_tags = [NBTTagType.TAG_Byte]
            elif isinstance(tag, NBTTagIntArray):
                valid_new_tags = [NBTTagType.TAG_Int]
            elif isinstance(tag, NBTTagLongArray):
                valid_new_tags = [NBTTagType.TAG_Long]

            for index, value in enumerate(tag.getPayload()):
                parse_tag(f"[{index}]", value, parent_tag=tag, parent_id=imgui_id)
    else:
        with imgui.tree_node(parent=parent_id if parent_id is not None else 0, label=name, selectable=True, leaf=True, payload_type=tag.getTypeName()):
            imgui_id = imgui.last_item()

            if isinstance(tag, NBTTagInt):
                imgui.add_input_int(label='', default_value=tag.getPayload(), width=250, user_data=(tag, name), callback=input_callback)
            elif isinstance(tag, NBTTagShort):
                imgui.add_input_int(label='', min_value=-32768, max_value=32767, min_clamped=True, max_clamped=True, default_value=tag.getPayload(), width=250, user_data=(tag, name), callback=input_callback)
            elif isinstance(tag, NBTTagByte):
                imgui.add_input_int(label='', min_value=-128, max_value=127, min_clamped=True, max_clamped=True, default_value=tag.getPayload(), width=250, user_data=(tag, name), callback=input_callback)
            elif isinstance(tag, NBTTagLong):
                imgui.add_input_text(label='', default_value=str(tag.getPayload()), width=250, hexadecimal=True, user_data=(tag, name), callback=input_callback)
            elif isinstance(tag, NBTTagFloat):
                imgui.add_input_float(label='', default_value=tag.getPayload(), width=250, user_data=(tag, name), callback=input_callback)
            elif isinstance(tag, NBTTagDouble):
                imgui.add_input_double(label='', default_value=tag.getPayload(), width=250, user_data=(tag, name), callback=input_callback)
            elif isinstance(tag, NBTTagString):
                imgui.add_input_text(label='', default_value=tag.getPayload(), width=250, multiline=tag.getPayloadSize() > 100, user_data=(tag, name), callback=input_callback)
            else:
                raise NBTException(f"Unknown tag type: {tag.__class__.__name__}")

    with imgui.popup(parent=imgui_id, mousebutton=imgui.mvMouseButton_Right):
        imgui.add_text(tag.getTypeName())
        imgui.add_separator()
        imgui.add_menu_item(label='Rename', user_data=(tag, imgui_id, parent_tag, parent_id), callback=rename_tag, enabled=allow_rename)
        imgui.add_menu_item(label='Delete', user_data=(tag, imgui_id, parent_tag, parent_id), callback=delete_tag)
        imgui.add_separator()
        imgui.add_menu_item(label='Copy', user_data=(tag,), callback=copy_clipboard)
        if enable_paste:
            imgui.add_menu_item(label='Paste', user_data=(tag, imgui_id), callback=paste_clipboard)
        if len(valid_new_tags) > 0:
            imgui.add_separator()
            with imgui.menu(label='New...'):
                for new_tag in valid_new_tags:
                    if new_tag is None:
                        imgui.add_separator()
                    else:
                        imgui.add_menu_item(label=new_tag.name, user_data=(tag, new_tag, imgui_id), callback=add_tag)

    #with imgui.tooltip(parent=imgui_id):
    #    imgui.add_text(tag.getTypeName())


def center_to(id: int | str, base_component: int | str | None):
    if base_component is None:
        return

    base_x, base_y = imgui.get_item_pos(base_component)
    base_width, base_height = (imgui.get_item_width(base_component), imgui.get_item_height(base_component))

    x, y = imgui.get_item_pos(id)
    width, height = (imgui.get_item_width(id), imgui.get_item_height(id))

    if base_width is None or base_height is None:
        return
    elif width is None or height is None:
        return

    imgui.set_item_pos(id, [base_x + (base_width / 2) - (width / 2), base_y + (base_height / 2) - (height / 2)])
    pass


def handle_modal_close(id: int | str, callback):
    imgui.hide_item(id)
    while imgui.is_item_visible(id):
        pass
    callback()
    imgui.delete_item(id)


def message_box(title: str, message: str):
    def ok(id: int | str):
        handle_modal_close(id, lambda: None)

    with imgui.window(modal=True, no_resize=True, label=title, width=200):
        window_id = imgui.last_container()

        imgui.add_text(message, wrap=imgui.get_item_width(window_id) or -1)
        with imgui.group(horizontal=True):
            imgui.add_button(label='OK', callback=lambda: ok(window_id))

        center_to(window_id, 'main')


def input_box(title: str, message: str, callback, default_value: str = ''):
    def ok(id: int | str, value):
        handle_modal_close(id, lambda: callback(value))

    def cancel(id: int | str):
        handle_modal_close(id, lambda: None)

    with imgui.window(modal=True, no_resize=True, label=title, width=200):
        window_id = imgui.last_container()

        imgui.add_text(message, wrap=imgui.get_item_width(window_id) or -1)
        input_id = imgui.add_input_text(label='', width=150, default_value=default_value, on_enter=True, callback=lambda _, v: ok(window_id, v))
        with imgui.group(horizontal=True):
            imgui.add_button(label='OK', callback=lambda: ok(window_id, imgui.get_value(input_id)))
            imgui.add_button(label='Cancel', callback=lambda: cancel(window_id))

        center_to(window_id, 'main')
        imgui.focus_item(input_id)


def combo_box(title: str, message: str, options: list[str], callback):
    def ok(id: int | str, value):
        handle_modal_close(id, lambda: callback(value))

    def cancel(id: int | str):
        handle_modal_close(id, lambda: None)

    with imgui.window(modal=True, no_resize=True, label=title, width=200):
        window_id = imgui.last_container()

        imgui.add_text(message, wrap=imgui.get_item_width(window_id) or -1)
        combo_id = imgui.add_combo(label='', items=options, width=150)
        with imgui.group(horizontal=True):
            imgui.add_button(label='OK', callback=lambda: ok(window_id, imgui.get_value(combo_id)))
            imgui.add_button(label='Cancel', callback=lambda: cancel(window_id))

        center_to(window_id, 'main')
        imgui.focus_item(combo_id)


def open_file():
    imgui.show_item('open_file')


def save_file():
    global open_files
    global current_file
    global can_save

    if not can_save:
        message_box('Error', 'No file opened to save.')
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


def about():
    message_box('About', 'NBT.py\n\nA simple NBT editor written in Python using PyNBT and DearPyGui.')


def save_settings():
    imgui.save_init_file('nbtpy.ini')


def exit():
    imgui.destroy_context()
    sys.exit(0)


def main():
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
            with imgui.menu(label='Help'):
                imgui.add_menu_item(label='About', callback=about)

        with imgui.group(horizontal=True):
            imgui.add_button(label='Open', callback=open_file)
            imgui.add_button(label='Save', callback=save_file)

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
    try:
        main()
    except Exception as e:
        message_box('Unhandled Error', str(e))
        raise e
