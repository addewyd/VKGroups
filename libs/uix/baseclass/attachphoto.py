# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty

from kivymd.card import MDCard

from dialogs import dialog
from preimage import PreviousImage
from fileloader import ProgressLoader
from libs.uix.lists import LeftIconAsync


class AttachPhoto(MDCard):
    '''Бокс для аттачей типа "фото".'''

    _app = ObjectProperty()

    def get_link(self, dict_links):
        if 'photo_807' in dict_links:
            link = dict_links['photo_807']
        else:
            if 'photo_604' in dict_links:
                link = dict_links['photo_604']
            else:
                link = dict_links['photo_130']

        return link

    def add_attach(self, content_list):
        '''Добавляет в бокс изображения в аттаче.'''

        self.clear_widgets()
        for dict_links in content_list:
            self.add_widget(
                LeftIconAsync(
                    source=dict_links['photo_130'], size_hint_x=None, width=dp(100),
                    on_release=lambda x, dict_links=dict_links: self.tap_on_image_attach(dict_links=dict_links))
                )

    def tap_on_image_attach(self, dict_links):
        '''Выводит на экран изображение из аттача.'''

        link = self.get_link(dict_links)
        self.show_image_from_attach(callback=lambda x: self.save_attach_image(link), link=link)

    def save_attach_image(self, link):
        '''Выводит файловый менеджер для выбора директории
        с последующим сохранением изображения из аттача.'''

        def on_select(select_directory):
            self._app.window_file_manager.dismiss()
            self._app.window_file_manager_open = False
            self. dialog_download_attach(select_directory, link)

        self._app.file_manager.select_path = on_select
        self._app.file_manager.search = 'dirs'
        self._app.show_manager(self._app.last_path)

    def show_image_from_attach(self, callback=None, link=''):
        self._app.previous_image = PreviousImage(
            link_on_image=link, floating_button_color=self._app.theme_cls.primary_color
        )
        if callback:
            self._app.previous_image.callback_on_button=callback

        self._app.previous_image.show()

    def dialog_download_attach(self, select_directory, link):
        def on_buttons(instance_button):
            dlg.dismiss()
            if instance_button.text == self._app.translation._('Да'):
                self.download_attach(select_directory, link)

        def on_check(check_state):
            self._app.config.set('General', 'show_dialog_on_download', 1)
            self._app.config.write()
            self._app.show_dialog_on_download = check_state

        dlg = None
        if not self._app.show_dialog_on_download:
            dlg = dialog(
                text=self._app.translation._('Загрузить файл в %s' % select_directory), use_check=True,
                text_check=self._app.translation._('Больше не спрашивать'), title=self._app.title,
                check_callback=on_check,
                buttons=[
                    [self._app.translation._('Да'), on_buttons],
                    [self._app.translation._('Отмена'), on_buttons]
                ]
            )
        else:
            self.download_attach(select_directory, link)

    def download_attach(self, select_directory, link):
        progress = ProgressLoader(
            url_on_image=link,
            path_to_file=select_directory + '/6523.png',
            download_complete=self._app.download_complete,
            download_hide=self._app.download_progress_hide
        )
        Clock.schedule_once(progress.download_start, .1)
