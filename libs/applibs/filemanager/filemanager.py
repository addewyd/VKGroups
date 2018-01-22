# -*- coding: utf-8 -*-

'''
filemanager.py

Простой тестовый менеджер для выбора директорий и файлов.
Разработан специально для проекта VKGroups -
<https://github.com/HeaTTheatR/VKGroups>.

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

import os
import sys

import kivy
kivy.require('1.9.2')

from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import get_color_from_hex, hex_colormap
from kivy.properties import ObjectProperty, StringProperty, ListProperty, \
                            BooleanProperty

try:
    from kivymd.list import ILeftBodyTouch
    from kivymd.toolbar import Toolbar
    from kivymd.button import MDFloatingActionButton, MDIconButton
    from kivymd.card import MDSeparator
except ImportError:
    raise ImportError('''Install package kivymd!''')

from . list import ModifiedOneLineIconListItem


__version__ = '2.1.5'

ACTIVITY_MANAGER = '''
<BodyManager@BoxLayout>:
    icon: 'folder'
    path: ''
    background_normal: ''
    background_down: ''
    dir_or_file_name: ''
    access_string: ''
    events_callback: lambda x: None
    orientation: 'vertical'

    ModifiedOneLineIconListItem:
        text: root.dir_or_file_name
        on_release: root.events_callback(root.path)
        IconFolder:
            disabled: True
            icon: root.icon

    MDSeparator:

<FileManager>:

    canvas:
        Rectangle:
            size: self.size
            pos: self.pos
            source: '%s/background.png' % root.home_path

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        y: root.height - toolbar.height
        spacing: dp(5)

        Toolbar:
            id: toolbar
            title: '%s' % root.current_path
            right_action_items: [['close-box', lambda x: root.exit_manager(1)]]
            elevation: 10
            md_bg_color: root.floating_button_color

    RecycleView:
        id: rv
        key_viewclass: 'viewclass'
        key_size: 'height'
        bar_width: dp(4)
        bar_color: root.floating_button_color
        y: -toolbar.height

        RecycleBoxLayout:
            default_size: None, dp(48)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

    AnchorLayout:
        anchor_x: 'right'
        anchor_y: 'bottom'
        size_hint_y: None
        height: dp(56)
        padding: dp(10)
        
        MDFloatingActionButton:
            size_hint: None, None
            size:dp(56), dp(56)
            icon: root.icon
            opposite_colors: True
            elevation: 8
            on_release: root.select_directory_on_press_button()
            md_bg_color: root.floating_button_color

'''


class IconFolder(ILeftBodyTouch, MDIconButton):
    pass


class FileManager(FloatLayout):
    home_path = StringProperty(os.path.split(__file__)[0])

    icon = StringProperty('check')
    '''Иконка, которая будет использована на кнопке выбора директории.'''

    exit_manager = ObjectProperty(lambda x: None)
    '''Функция, вызываемая при достижении пользователем
    корня дерева каталогов.'''
    
    select_path = ObjectProperty(lambda x: None)
    '''Функция, вызываемая при выборе файла/директории.'''

    ext = ListProperty()
    '''Список расширений файлов, которые будут отображаться
    в менеджере. Например, ['py', 'kv'] - отфильтрует все файлы,
    кроме python сценариев и Kv Language.'''

    search = StringProperty('all')
    '''Может принимать значения 'dirs' 'files' - отображение
    только директорий или только файлов. По умолчанию отображает
    и папки, и файлы.'''

    current_path = StringProperty('/')
    '''Текущий каталог.'''

    floating_button_color = ListProperty(
        get_color_from_hex(hex_colormap['teal'])
    )
    '''Цвет кнопки.'''

    use_access = BooleanProperty(True)
    '''Показывать ли права на файлы и директории.'''

    def __init__(self, **kwargs):
        super(FileManager, self).__init__(**kwargs)
        self.history = []   # история перемещения по дереву каталогов
        # Если False - не добавляем директорию в историю -
        # пользователь движется вниз по дереву.
        self.history_flag = True
        toolbar_label = self.ids.toolbar.children[1].children[0]
        toolbar_label.font_style = 'Subhead'

    def show(self, path):
        '''Формирует тело дерева каталогов.'''

        dirs, files = self.get_content(path)
        self.current_path = path
        manager_list = []

        if dirs == [] and files == []:  # выбранная директория
            pass
        elif not dirs and not files:  # директория недоступна
            return

        for name in dirs:
            _path = path + name if path == '/' else path + '/' + name
            access_string = self.get_access_string(_path)
            if 'r' not in access_string:
                icon = 'folder-lock'
            else:
                icon = 'folder'

            manager_list.append({
                'viewclass': 'BodyManager',
                'path': _path,
                'icon': icon,
                'dir_or_file_name': name,
                'access_string': access_string,
                'events_callback': self.select_dir_or_file
            })

        for name in files:
            _path = path + name if path == '/' else path + '/' + name
            manager_list.append({
                'viewclass': 'BodyManager',
                'path': _path,
                'icon': 'file-outline',
                'dir_or_file_name': name,
                'access_string': self.get_access_string(_path),
                'events_callback': self.select_dir_or_file
            })

        self.ids.rv.data = manager_list

    def get_access_string(self, path):
        access_string = ''
        if self.use_access:
            access_data = {'r': os.R_OK, 'w': os.W_OK, 'x': os.X_OK}
            for access in access_data.keys():
                access_string += access if os.access(path, access_data[access]) else '-'

        return access_string

    def get_content(self, path):
        ''' Возвращает список вида [[Список папок], [список файлов]].'''

        try:
            files = []
            dirs = []

            if self.history_flag:
                self.history.append(path)
            if not self.history_flag:
                self.history_flag = True

            for content in os.listdir(path):
                if os.path.isdir('%s/%s' % (path, content)):
                    if self.search == 'all' or self.search == 'dirs':
                        dirs.append(content)
                else:
                    if self.search == 'all' or self.search == 'files':
                        if len(self.ext) != 0:
                            try:
                                if content.split('.')[1].lower() in self.ext \
                                        or content.split('.')[1].upper() in self.ext:
                                    files.append(content)
                            except IndexError:
                                pass
                        else:
                            files.append(content)
            return dirs, files
        except OSError:
            self.history.pop()
            return None, None

    def select_dir_or_file(self, path):
        '''Вызывается при тапе по имени директории или файла.'''

        if os.path.isfile(path):
            self.history = []
            self.select_path(path)
            return

        self.current_path = path
        self.show(path)

    def back(self):
        '''Возврат на ветку вниз в дереве каталогов.'''

        if len(self.history) == 1:
            path, end = os.path.split(self.history[0])
            if end == '':
                self.exit_manager(1)
                return
            self.history[0] = path
        else:
            self.history.pop()
            path = self.history[-1]
        self.history_flag = False
        self.select_dir_or_file(path)

    def select_directory_on_press_button(self, *args):
        self.history = []
        self.select_path(self.current_path)


Builder.load_string(ACTIVITY_MANAGER)
