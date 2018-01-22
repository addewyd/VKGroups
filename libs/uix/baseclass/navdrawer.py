# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from kivy.properties import ObjectProperty

from kivymd.navigationdrawer import NavigationLayout


class NavDrawer(NavigationLayout):
    _app = ObjectProperty()

    def _toggle(self):
        # Не открываем NavigationDrawer, если идёт авторизация на сервере.
        if self._app.manager.current == 'load screen':
            return
        self.toggle_nav_drawer()