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
import webbrowser

from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from kivymd.label import MDLabel
from kivymd.button import MDIconButton
from kivy.properties import ObjectProperty


class AttachLink(BoxLayout):
    '''Бокс для аттачей типа "ссылка".'''

    _app = ObjectProperty()

    def add_attach(self, attach_list):
        self.ids.box_attach.clear_widgets()

        for text_link in attach_list:
            box_attach = BoxLayout(spacing=dp(10))
            box_attach.add_widget(
                MDIconButton(
                    icon='link', size_hint=(None, None),
                    size=(dp(50), dp(50)), pos_hint={'center_y': .5},
                    disabled=True
                )
            )
            box_attach.add_widget(
                MDLabel(
                    text=text_link, theme_text_color='Primary', markup=True,
                    on_ref_press=self.tap_on_link
                )
            )

        self.ids.box_attach.add_widget(box_attach)
        self.height = dp(100 * attach_list.__len__())

    def tap_on_link(self, instance, text_url):
        '''Открывает ссылку в стандартном браузере
        или запускает процесс скачвания, если ссылка указывает на файл.'''

        name_file = os.path.split(text_url)[1]
        if os.path.splitext(name_file)[1] == '':
            webbrowser.open(text_url)
        else:
            self._app.dialog_download_attach(name_file)

