# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

import os
import sys
import re
import ast
import time
import webbrowser

# FIXME: на мобильном устройстве при запуске приложения из исходных текстов
# не загружаются изображения в AsyncImage в виду ошибки [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed.
# Поэтому приходится отключить проверку сертификатов.
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp

from main import __version__

from libs.utils import ShowPlugins, AuthorizationOnVK, GetAndSaveLoginPassword
from libs.vkrequests import create_issue, create_comment, send_message, get_user_info
from libs._thread import thread
from libs.translation import Translation
from libs.createpreviousportrait import create_previous_portrait
from libs.uix.lists import Lists, IconItemAsync, SingleIconItem, Icon
from libs.uix.baseclass.startscreen import StartScreen
from libs.uix.baseclass.boxposts import BoxPosts
from libs.uix.baseclass.passwordform import PasswordForm
from libs.uix.baseclass.list_user_groups import ListUserGroups
from libs.uix.baseclass.boxattach import BoxAttach
from libs.uix.baseclass.boxattachfile import BoxAttachFile

from kivymd.theming import ThemeManager
from kivymd.button import MDFlatButton
from kivymd.label import MDLabel

from dialogs import card, dialog, input_dialog
from filemanager import FileManager
from toast import toast
from formformessages import FormForMessages


class VKGroups(App, AuthorizationOnVK, GetAndSaveLoginPassword):
    '''Функционал программы.'''

    title = 'VKGroups' 
    icon = 'icon.png'
    use_kivy_settings = False
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'BlueGrey'
    lang = StringProperty('ru')

    def __init__(self, **kvargs):
        super(VKGroups, self).__init__(**kvargs)

        Window.bind(on_keyboard=self.events_program)

        self.POSSIBLE_FILES = \
            ['.png', '.jpg', '.jpeg', '.gif', '.zip', '.txt']
        self.DEVISE_ONLINE = {
            'mobile': 'desktop-mac',
            'computer': 'laptop',
            0: 'power'
        }
        
        self.PATTERN_WHOM_COMMENT = pattern_whom_comment
        self.PATTERN_REPLACE_LINK = pattern_replace_link

        self.window = Window
        self.config = ConfigParser()
        # Окно прогресса.
        self.load_dialog = ModalView(
            size_hint=(None, None),
            pos_hint={'x': 5.0 / Window.width, 'y': 5.0 / Window.height},
            background_color=[0, 0, 0, .2], size=(dp(120), dp(50)),
            background=os.path.join('data', 'images', 'decorator.png'), auto_dismiss=False
        )
        # Экземпляр для вывода списка плагинов пользователя.
        self.instance_list_user_plugins = ShowPlugins(self)
        # Файловый менеджер.
        self.window_file_manager = ModalView(
            size_hint=(1, 1), auto_dismiss=False, on_open=lambda x: self.load_dialog.dismiss()
        )
        self.window_file_manager_open = False
        self.file_manager = FileManager(
            exit_manager=self.exit_manager,
            floating_button_color=self.theme_cls.primary_color
        )
        self.window_file_manager.add_widget(self.file_manager)

        # Текущие менеджер, экран и имя вкладок MDBottomNavigationItem.
        self.current_screen_tab = None
        self.current_tab_manager = None
        self.name_press_tab = ''

        self.file_manager_not_opening = True  # файловый менеджер ещё не открывался
        self.password_form = None
        self.box_posts = None
        self.attach_file = []
        self.attach_image = []
        self.box_for_attach_file = None
        self.box_for_attach_image = None
        self.group_info = None # словарь с информацией, полученной с сервера о группе
        self.result_sending_post = None
        self.exit_interval = False
        self.path_to_avatar = os.path.join(self.directory, 'data', 'images', 'avatar.png')
        self.dict_language = ast.literal_eval(
            open(os.path.join(self.directory, 'data', 'locales', 'locales')).read()
        )

        self.window_user_groups = None # окно со списком групп пользователя
        self.window_language = None # окно со списком локализаций

    def get_application_config(self):
        return super(VKGroups, self).get_application_config(
                        '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        '''Создаёт файл настроек приложения vkgroups.ini.'''

        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'ru')
        config.setdefault('General', 'theme', 'default')
        config.setdefault('General', 'authorization', 0)
        config.setdefault('General', 'issues_in_group', 0)
        config.setdefault('General', 'count_issues', 20)
        config.setdefault('General', 'user_name', 'User')
        config.setdefault('General', 'last_group', '99411738')
        config.setdefault(
            'General', 'regdata', "{'login': None, 'password': None}"
        )
        config.setdefault('General', 'last_screen', 'load screen')
        config.setdefault('General', 'last_path', '/')
        config.setdefault('General', 'show_dialog_on_download', 0)

    def set_value_from_config(self):
        '''Устанавливает значения переменных из файла настроек
        vkgroups.ini.'''

        self.config.read(os.path.join(self.directory, 'vkgroups.ini'))
        self.theme = self.config.get('General', 'theme')
        self.language = self.config.get('General', 'language')
        self.authorization = self.config.getint('General', 'authorization')
        self.last_path = self.config.get('General', 'last_path')
        self.last_screen = self.config.get('General', 'last_screen')
        self.regdata = \
            ast.literal_eval(self.config.get('General', 'regdata'))
        self.login = self.regdata['login']
        self.password = self.regdata['password']
        try:
            self.user_name = ast.literal_eval(self.config.get('General', 'user_name')).decode('utf-8')
        except ValueError:
            self.user_name = self.config.get('General', 'user_name')
        self.group_id = self.config.get('General', 'last_group')
        self.count_issues = self.config.getint('General', 'count_issues')
        self.issues_in_group = \
            self.config.getint('General', 'issues_in_group')
        self.show_dialog_on_download = \
            self.config.getint('General', 'show_dialog_on_download')

    def build(self):
        self.set_value_from_config()
        self.translation = Translation(
            self.language, 'kivyissues', '%s/data/locales' % self.directory)
        self.RELATION = {
            1: self.translation._('не женат/не замужем'),
            2: self.translation._('есть друг/подруга'),
            3: self.translation._('помолвлен'),
            4: self.translation._('женат/замужем'),
            5: self.translation._('всё сложно'),
            6: self.translation._('в активном поиске'),
            7: self.translation._('влюблён/влюблена'),
            8: self.translation._('в гражданском браке'),
            0: self.translation._('не указано')
        }
        self.message_about_files_mismatch = {
            'FILE': self.translation._('This file unsupported!'),
            'FOTO': self.translation._('This is not image!')
        }
        self.load_dialog.add_widget(
            MDLabel(text=self.translation._(' Загрузка...'))
        )
        self.load_all_kv_files(self.directory + '/libs/uix/kv')
        self.screen = StartScreen()  # главный экран программы
        self.navigation_button = self.screen.ids.navigation_button
        self.previous = self.navigation_button.ids.previous
        self.manager = self.screen.ids.manager
        self.nav_drawer = self.screen.ids.nav_drawer
        self.current_screen_tab = self.navigation_button.ids.home_page

        if not self.login or not self.password:
            self.show_screen_registration()
        else:  # авторизация на сервере
            self._authorization_on_vk(self.login, self.password, self.group_id)

        Clock.schedule_interval(self.wait_info_for_home_page_group, 1)
        return self.screen

    def wait_info_for_home_page_group(self, interval):
        '''Ожидает получения данных от сервера после чего устанавливает
        значения переменных для экрана Previous.'''

        if self.group_info:
            self.previous.ids.group_title.source = \
                self.group_info['photo_200']
            self.previous.ids.group_name.text = \
                '[size=17][b]%s[/b][/size]\n[size=14]%s[/size]' % (
                    self.group_info['name'], self.group_info['status']
                )
            self.previous.ids.group_link.text = \
                '[ref={link}]{link}[/ref]'.format(
                    link='https://vk.com/%s' % self.group_info['screen_name']
                )
            self.previous.ids.group_people.text = \
                '%s %s' % (
                    self.translation._('Участники'),
                    self.group_info['members_count']
                )
            self.previous.ids.description.text = \
                self.group_info['description']
            self.nav_drawer.ids.user_name.text = \
                '[b]%s[/b]\n[size=12]online[/size]\n' % self.user_name

            Clock.unschedule(self.wait_info_for_home_page_group)
            Clock.schedule_once(
                lambda kwargs: self.show_form_for_messages(whom_name=''), 1
            )
            self.check_groups_user(
                name_group=self.group_info['name'],
                info_group=self.group_info['status'] ,
                logo_group=self.group_info['photo_200']
            )

        if os.path.exists('%s/data/state.txt' % self.directory):
            os.remove('%s/data/state.txt' % self.directory)

    def check_state_fields(self, id_instance, text_field):
        '''Сохраняет содержимое формы регистрации.'''

        if text_field == '':
            return

        if os.path.exists('%s/data/state.txt' % self.directory):
            data_state = ast.literal_eval(open('%s/data/state.txt' % self.directory).read())
        else:
            data_state = {}

        data_state[id_instance] = text_field

        # TODO: добавить шифрование данных.
        with open('%s/data/state.txt' % self.directory, 'w') as state_form:
            state_form.write(str(data_state))

    def check_groups_user(self, **kwargs):
        '''Проверяет и добавляет в список новые группы пользователя, которые он посещал.
        Данные имеют вид:
        {'Имя группы': ['Описание группы', 'ссылка на логотип группы', 'id группы,]}.'''

        file_groups_path = '%s/data/groups_user.ini' % self.directory
        if not os.path.exists(file_groups_path):
            with open(file_groups_path, 'w') as file_groups_user:
                file_groups_user.write('{}')

        groups_user = ast.literal_eval(
            open('%s/data/groups_user.ini'  % self.directory).read()
        )
        if not kwargs['name_group'] in groups_user:
            groups_user[kwargs['name_group']] = \
                [kwargs['info_group'], kwargs['logo_group'], self.group_id]
            with open(file_groups_path, 'w') as file_groups_user:
                file_groups_user.write(str(groups_user))

    def show_login_and_password(self, selection):
        '''
        Устанавливает свойства текстовых полей для ввода логина и пароля.

        :type selection: <class 'int'>

        '''

        if selection:
            self.password_form.ids.login.password = False
            self.password_form.ids.password.password = False
        else:
            self.password_form.ids.login.password = True
            self.password_form.ids.password.password = True

    def show_groups_user(self, *args):
        '''Выводит окно со списком групп пользователя.'''

        def callback_on_button_click(**kwargs):
            def on_press(text_button):
                # TODO: добавить группу в словарь groups.ini.
                field.dismiss()
                toast(str(text_button))

            field = input_dialog(
                title=kwargs['title'], hint_text='',
                text_button_ok=self.translation._('Добавить'),
                text_button_cancel=self.translation._('Отмена'),
                events_callback=on_press
            )

        def callback_on_item_click(name_item, mode):
            description_group, logo_group, id_group = groups_user[name_item]
            dialog(
                title=name_item,
                text='%s\nID - %s' % (description_group, str(id_group))
            )

        if not self.window_user_groups:
            dict_groups_user = {}
            groups_user = ast.literal_eval(
                open('%s/data/groups_user.ini' % self.directory).read()
            )

            for name_group in groups_user.keys():
                description_group, logo_group, id_group = groups_user[name_group]
                dict_groups_user[name_group] = [description_group, logo_group]

            list_user_groups = ListUserGroups()
            _list = list_user_groups.ids.groups_list
            _list.events_callback = callback_on_item_click
            list_user_groups.ids.add_group.on_press = \
                lambda **kwargs: callback_on_button_click(
                    title=self.translation._('Введите ID группы:')
                )
            _list.two_list_custom_icon(dict_groups_user, IconItemAsync)

            self.window_user_groups = card(list_user_groups, size=(.85, .55))
        self.window_user_groups.open()

    def show_screen_registration(self, fail_registration=False):
        '''Окно с формой регистрации.'''

        if not self.password_form:
            self.password_form = \
                PasswordForm(callback=self.check_fields_login_password)
            self.password_form.ids.group_id.text = self.group_id

        self.screen.ids.load_screen.add_widget(self.password_form)

        # Если произошла ошибка регистрации, деактивируем спиннер и чистим
        # лейблы статуса авторизации.
        if fail_registration:
            self.screen.ids.load_screen.ids.spinner.active = False
            self.screen.ids.load_screen.ids.status.text = ''

    def show_screen_connection_failed(self, text_error):
        '''Выводит подпись о не активном соединении и кнопку для повторного
        подключения.'''

        self.screen.ids.load_screen.ids.spinner.active = False
        self.screen.ids.load_screen.ids.status.text = ''

        box = BoxLayout(
            orientation='vertical', spacing=dp(10),
            size_hint_y=None, height=dp(100), pos_hint={'center_y': .5}
        )
        texts_errors = {
            'OAuth2 authorization error':
                self.translation._('Повторите попытку позже…'),
            'Failed to establish a new connection':
                self.translation._('Соединение Интернет отсутствует')
        }

        _text_error = self.translation._('Неизвестная ошибка…')
        for name_error in texts_errors.keys():
            if name_error in text_error:
                _text_error = texts_errors[name_error]
  
        box.add_widget(
            MDLabel(
                text=_text_error, halign='center', font_style='Subhead'
            )
        )
        box.add_widget(
            MDFlatButton(
                text=self.translation._('Повторить попытку'),
                theme_text_color='Custom', pos_hint={'center_x': .5},
                text_color=self.theme_cls.primary_color,
                on_release=lambda x: self._authorization_on_vk(
                    self.login, self.password, self.group_id,  from_fail_screen=True
                )
            )
        )
        self.screen.ids.load_screen.add_widget(box)

    def clear_box_for_attach(self):
        self.box_for_attach_image = None
        self.box_for_attach_file = None
        self.attach_file = []
        self.attach_image = []

    @thread
    def send_post(self, text):
        self.result_sending_post, text_error = \
             create_issue(text, self.attach_file, self.attach_image)

    @thread
    def send_messages(self, text, user_id):
        self.result_sending_post, text_error = \
            send_message(
                user_id=user_id, 
                files=self.attach_file, 
                images=self.attach_image,
                text=text
            )

    @thread
    def send_comment(self, text, post_id, comment_id):
        self.result_sending_post, text_error = \
            create_comment(text, self.attach_file, self.attach_image, post_id, comment_id)

    def show_result_sending_posts(self, interval):
        def unschedule():
            Clock.unschedule(self.show_result_sending_posts)
            self.result_sending_post = None
            toast(message)
            self.clear_box_for_attach()

        message = self.translation._('Sent!')
        if self.result_sending_post:
            # TODO: добавить обновление постов.
            if self.manager.current != 'navigation button':
                pass
            unschedule()
        elif self.result_sending_post is False:
            message = self.translation._('Error while sending!')
            unschedule()

    def callback_for_input_text(self, **kwargs):
        '''Вызывается при событиях из формы ввода текста.'''

        self.flag_attach = kwargs.get('flag')
        data = kwargs.get('kwargs')
        comment_id = int(data.get('comment_id', 0))
        post_id = int(data.get('post_id', 0))
        user_id = int( data.get('kwargs').get('user_id')) if 'kwargs' in data else 0
        whom_name = data.get('whom_name', '')
        text = whom_name + ', ' + self.form_for_messages.ids.text_form.text if whom_name != '' else self.form_for_messages.ids.text_form.text

        if self.flag_attach in ('FILE', 'FOTO'):
            self.show_manager(self.last_path, self.tap_on_file_in_filemanager)
        elif self.flag_attach == 'SEND':
            if self.manager.current == 'navigation button' or self.manager.current == 'user info':
                self.form_for_messages.hide()

            if text.isspace() or text != '':
                if self.manager.current == 'navigation button' and self.name_press_tab == 'Wall_posts' :
                    self.send_comment(text, post_id, comment_id)
                elif self.manager.current == 'user info':
                    self.send_messages(text, user_id)
                else:
                    self.send_post(text)

                self.form_for_messages.clear()
                Clock.schedule_interval(
                    self.show_result_sending_posts, 0
                )

    def remove_attach(self, select_instance_attach):
        '''Удаляет превью файлов и изображений из формы для отправки сообщений.'''

        def _remove_attach(interval):
            parent_widget.remove_widget(instance_attach)

        if select_instance_attach in self.box_for_attach_file.children:
            parent_widget = self.box_for_attach_file
        else:
            parent_widget = self.box_for_attach_image

        for instance_attach in parent_widget.children:
            if instance_attach == select_instance_attach:
                Clock.schedule_once(_remove_attach, .25)
                break

    def add_preview_attached_image(self, path_to_attach):
        '''Добавляет превью файлов в форму для отправки сообщений.'''

        if os.path.splitext(path_to_attach)[1] not in self.POSSIBLE_FILES[-2:]:
            if not self.box_for_attach_image:
                self.box_for_attach_image = BoxAttach(spacing=dp(5))
                self.form_for_messages.add_widget(self.box_for_attach_image)
            self.box_for_attach_image.add_widget(
                Icon(
                    source=path_to_attach, size_hint=(None, None), size=(dp(60), dp(120)),
                    on_release=self.remove_attach
                )
            )

    def add_preview_attached_file(self, path_to_attach):
        if not self.box_for_attach_file:
            self.box_for_attach_file = BoxAttachFile(spacing=dp(5))
            self.form_for_messages.add_widget(self.box_for_attach_file)
        attach = SingleIconItem(icon='file', text=os.path.split(path_to_attach)[1], events_callback=self.remove_attach)
        attach.ids._lbl_primary.font_style = 'Caption'
        self.box_for_attach_file.add_widget(attach)

    def write_last_path_manager(self, path_to_file_folder, path_to_file):
        self.config.set('General', 'last_path', path_to_file_folder)
        self.config.write()
        self.last_path = path_to_file_folder

    def tap_on_file_in_filemanager(self, path_to_file):
        self.window_file_manager.dismiss()
        self.window_file_manager_open = False
        path_to_file_folder, name_file = os.path.split(path_to_file)
        self.write_last_path_manager(path_to_file_folder, path_to_file)
        if os.path.splitext(name_file)[1] not in self.POSSIBLE_FILES:
            toast(self.message_about_files_mismatch[self.flag_attach])
        else:
            if self.flag_attach == 'FILE':
                self.attach_file.append(path_to_file)
                self.add_preview_attached_file(path_to_file)
            else:
                self.attach_image.append(path_to_file)
            self.add_preview_attached_image(path_to_file)

    def set_avatar(self, path_to_avatar):
        self.nav_drawer.ids.avatar.source = path_to_avatar
        self.nav_drawer.ids.avatar.reload()

    def choice_avatar_user(self):
        '''Выводит файловый менеджер для выбора аватара
        и устанавливает его в качестве аватара пользователя.'''

        def on_select(path_to_avatar):
            self.window_file_manager.dismiss()

            if os.path.splitext(path_to_avatar)[1] \
                    not in self.POSSIBLE_FILES[:3]:
                toast(self.translation._('This is not image!'))
            else:
                new_path_to_avatar = \
                    self.directory + '/data/images/avatar.png'
                create_previous_portrait(path_to_avatar, new_path_to_avatar)
                self.set_avatar(new_path_to_avatar)
                toast(self.translation._('Аватар изменён'))
                self.nav_drawer.state = 'open'

        self.show_manager(self.last_path, on_select)

    def show_plugins(self, *args):
        self.instance_list_user_plugins.show_plugins()

    def show_manager(self, directory, callback=None):
        ''''Выводит на экран файловый менеджер.'''

        if self.file_manager_not_opening:
            self.load_dialog.open()
            self.file_manager_not_opening = False

        self.window_file_manager_open = True
        Clock.schedule_once(self.window_file_manager.open, .2)
        if callback:
                   self.file_manager.select_path = callback
        self.file_manager.show(directory)

    def show_posts(self, instance_tab=None):
        # Открываем ранее загруженный список постов.
        if self.box_posts:
            self.box_posts.show_comments = False
            self.box_posts.items_list = []
            self.box_posts.ids.rv.data = self.box_posts.copy_rv_data
            return

        if instance_tab:
            instance_tab.clear_widgets()
        else:
            self.current_screen_tab.clear_widgets()

        # Получаем список постов от сервера.
        self.box_posts = BoxPosts(_app=self)
        self.box_posts.show_posts()

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        '''Вызывается при нажатии кнопки Меню или Back Key
        на мобильном устройстве.'''

        if keyboard in (1001, 27):
            if self.nav_drawer.state == 'open':
                self.nav_drawer.toggle_nav_drawer()
            self.back_screen(keyboard)
        elif keyboard in (282, 319):
            pass

        return True

    def back_screen(self, event=None):
        '''Менеджер экранов. Вызывается при нажатии Back Key
        и шеврона "Назад" в ToolBar.'''

        current_screen = self.manager.current
        if not self.window_file_manager_open:
            self.clear_box_for_attach()
        # Нажата BackKey.
        if event in (1001, 27):
            # Если информация с сервера о группе ещё не получена -
            # идёт авторизация либо данные в процессе загрузки.
            if not self.group_info:
                return
            if self.name_press_tab == 'Wall_posts' and self.form_for_messages.visible and \
                    not self.window_file_manager_open:
                self.form_for_messages.hide()
                return
            if self.window_file_manager_open:
                self.file_manager.back()
                return
            if current_screen == 'navigation button':
                if hasattr(self, 'previous_image'):
                    if self.previous_image.previous_open:
                        self.previous_image.dismiss()
                        return
                if self.box_posts and self.box_posts.show_comments:
                    self.show_posts()
                    return
                self.dialog_exit()
                return
        if current_screen == 'show license':
            self.manager.current = self.manager.screens[-1].name
        elif current_screen == 'user info':
            self.manager.current = 'navigation button'
        else:
            if not self.login or not self.password:
                self.dialog_exit()
                return
            self.manager.current = self.manager.previous()

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)
            
        Clock.schedule_interval(check_interval_press, 1)
        toast(self.translation._('Нажмите еще раз для выхода'))

    def show_form_for_messages(self, **kwargs):
        '''Выводит форму для ввода комментариев.'''

        self.form_for_messages = FormForMessages(callback=self.callback_for_input_text, kwargs=kwargs)

        self.form_for_messages.show(
            parent_instance=self.current_screen_tab if self.manager.current == 'navigation button' \
            else self.screen.ids.user_info.ids.float_layout
        )
        if kwargs.get('whom_name') == '':
        	self.form_for_messages.visible = False

    def form_for_messages_hide(self):
        if self.form_for_messages.visible and not self.form_for_messages.ids.text_form.focus:
            self.form_for_messages.hide()

    def show_about(self, *args):
        self.nav_drawer.toggle_nav_drawer()
        self.screen.ids.load_screen.ids.status.text = \
            self.translation._(
                '[size=20][b]VKGroups[/b][/size]\n\n'
                '[b]Версия:[/b] {version}\n'
                '[b]Лицензия:[/b] MIT\n\n'
                '[size=20][b]Разработчики[/b][/size]\n\n'
                '[b]Backend:[/b] [ref=https://m.vk.com/fogapod]'
                '[color={link_color}]Евгений Ершов[/color][/ref]\n'
                '[b]Frontend:[/b] [ref=https://m.vk.com/heattheatr]'
                '[color={link_color}]Иванов Юрий[/color][/ref]\n\n'
                '[b]Исходный код:[/b] '
                '[ref=https://github.com/HeaTTheatR/VKGroups]'
                '[color={link_color}]GitHub[/color][/ref]').format(
                version=__version__,
                link_color=get_hex_from_color(self.theme_cls.primary_color)
            )
        self.screen.ids.load_screen.ids.spinner.active = False
        self.manager.current = 'load screen'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen()]]

    def show_license(self, *args):
        self.screen.ids.show_license.ids.text_license.text = \
            self.translation._('%s') % open(
                '%s/license/license_en.txt' % 
                    self.directory, encoding='utf-8').read()
        self.nav_drawer._toggle()
        self.manager.current = 'show license'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen()]]
        self.screen.ids.action_bar.title = \
            self.translation._('MIT LICENSE')

    def exit_manager(self, *args):
        '''Закрывает окно файлового менеджера.'''

        self.window_file_manager.dismiss()
        self.window_file_manager_open = False

    def select_locale(self, *args):
        '''Выводит окно со списком имеющихся языковых локализаций для
        установки языка приложения.'''

        def select_locale(name_locale):
            '''Устанавливает выбранную локализацию.'''

            for locale in self.dict_language.keys():
                if name_locale == self.dict_language[locale]:
                    self.lang = locale
                    self.config.set('General', 'language', self.lang)
                    self.config.write()

        dict_info_locales = {}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]] = \
                ['locale', locale == self.lang]

        if not self.window_language:
            self.window_language = card(
                Lists(
                    dict_items=dict_info_locales,
                    events_callback=select_locale, flag='one_select_check'
                ),
                size=(.85, .55)
            )
        self.window_language.open()

    def set_chevron_back_screen(self):
        '''Устанавливает шеврон возврата к предыдущему экрану в ToolBar.'''

        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(self.manager.current)]]

    def download_progress_hide(self, instance_progress, value):
        '''Скрывает виджет прогресса загрузки файлов.'''
 
        instance_progress.dismiss()
        self.screen.ids.action_bar.right_action_items = \
            [['download', lambda x: self.download_progress_show(instance_progress)]]

    def download_progress_show(self, instance_progress):
        self.screen.ids.action_bar.right_action_items = []
        instance_progress.open()
        instance_progress.animation_progress_from_fade()

    def download_complete(self, result):
        self.screen.ids.action_bar.right_action_items = []
        if result =='Done':
            toast(self.translation._('Загружено'))
        else:
            toast(self.translation._('Ошибка загрузки'))

    def tap_on_icon_user(self, user_id):
        '''Вызывается при тапе по иконке пользователя в списках постов/комментариев.
        Получает, устанавливает и выводит на экран информацию о выбранном пользователе.
        '''

        def unschedule(error=False):
            if error:
                toast(self.translation._('Данные не получены'))
            Clock.unschedule(wait_result)
            self.load_dialog.dismiss()

        def set_value_for_screen(instance_screen_user_info):
            '''Устанавливает значения подписей в экране информации о пользователе.'''

            instance_screen_user_info.ids.avatar.source = result['photo_200']
            instance_screen_user_info.ids.user_name.text = instance_screen_user_info.ids.user_name.text % (
                result['first_name'] + ' ' + result['last_name'],
                self.translation._('Последний раз был в сети в ') + time.strftime(
                    "%H:%M", time.localtime(result['last_seen']['time'])
                )
            )
            instance_screen_user_info.ids.label_user_status.text = \
                instance_screen_user_info.ids.label_user_status.text % result['status']
            instance_screen_user_info.ids.message_button.bind(
                on_release=lambda kwargs: self.show_form_for_messages(kwargs={'user_id': user_id})
            )

            data = {
                'bdate': {
                   'result': result['bdate'] if 'bdate' in result else None,
                   'bad_result': self.translation._('скрыта'), 
                   'label_instance': instance_screen_user_info.ids.label_bdate,
                   'label_text': self.translation._('Дата рождения')},

                'city': {
                    'result': result['city']['title'] if 'city' in result else None,
                    'bad_result': self.translation._('не указан'), 
                    'label_instance': instance_screen_user_info.ids.label_city,
                    'label_text': self.translation._('Город')},

                'relation': {
                    'result': self.RELATION[result['relation']] if 'relation' in result else None,
                    'bad_result': self.translation._('не указано'), 
                    'label_instance': instance_screen_user_info.ids.label_marital_status,
                    'label_text': self.translation._('Семейное положение')}
            }

            for key in data:
                text_for_label = data[key]['result'] if data[key]['result'] else data[key]['bad_result']
                data[key]['label_instance'].text = data[key]['label_instance'].text % (
                    data[key]['label_text'], text_for_label
                )
            unschedule()

        def wait_result(interval):
            '''Ожидает информации от сервера.'''

            if result:
                self.manager.current = 'user info'
                set_value_for_screen(self.screen.ids.user_info)

        result = None
        self.load_dialog.open()
        Clock.schedule_once(wait_result, 0)
        result, text_error = get_user_info(user_id=user_id)
        if text_error:
            unschedule(error=True)

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            with open(os.path.join(directory_kv_files, kv_file), encoding='utf-8') as kv:
                Builder.load_string(kv.read())

    def on_tab_press(self, instance_tab):
        '''Вызывается при выборе одного из пунктов BottomNavigation.'''

        self.clear_box_for_attach()
        self.name_press_tab = instance_tab.name
        self.current_screen_tab = instance_tab
        self.current_tab_manager = instance_tab.parent_widget.ids.tab_manager

        if self.current_tab_manager.current == self.name_press_tab:
            return

        # Вкладка 'Записи группы'.
        if self.name_press_tab == 'Wall_posts':
            self.show_posts(instance_tab)
            self.form_for_messages.hide()
        elif self.name_press_tab == 'Home_page':
            self.box_posts = None
            self.show_form_for_messages(whom_name='')

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)

    def on_pause(self):
        '''Ставит приложение на 'паузу' при сворачивании его в трей.'''
        
        self.config.set('General', 'last_screen', self.manager.current)
        self.config.write()

        return True

    def on_start(self):
        '''Вызывается при открытии стартового экрана приложения.'''

        # Восстанавливаем форму ввода логина и пароля.
        if self.last_screen == 'load screen' and \
                not self.login and not self.password:
            if os.path.exists('%s/data/state.txt' % self.directory):
                data_state = \
                    ast.literal_eval(open('%s/data/state.txt' % self.directory).read())
                self.password_form.ids.login.text = \
                    data_state['login'] if 'login' in data_state else ''
                self.password_form.ids.password.text = \
                    data_state['password'] if 'password' in data_state else ''
                self.password_form.ids.group_id.text = data_state['group']


pattern_whom_comment = re.compile(r'\[id\d+\|\w+\]', re.UNICODE)
pattern_replace_link = re.compile(r'(?#Protocol)(?:(?:ht|f)tp(' \
                             '?:s?)\:\/\/|~\/|\/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,'
                                  '*:=]|%[a-f\d]{2})*)?')
