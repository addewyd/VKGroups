# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

import webbrowser

from kivy.uix.screenmanager import Screen


class LoadScreen(Screen):
    def open_url(self, instance, url):
        webbrowser.open(url)
