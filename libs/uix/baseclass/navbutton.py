# -*- coding: utf-8 -*-

'''
VKroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty


class NavigationButton(Screen):

    _app = ObjectProperty()

    def on_enter(self):
        '''Вызывается при установке Activity на экран.'''

        self._app.screen.ids.action_bar.left_action_items = \
            [['menu', lambda x: self._app.nav_drawer._toggle()]]
        self._app.screen.ids.action_bar.title = self._app.title
