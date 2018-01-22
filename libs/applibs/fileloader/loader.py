# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

# Прогрессбар загрузки файлов с сервера.

import os
import threading

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty

from kivymd.card import MDCard

from . import retrieveprogressload
from . retrieveprogressload import retrieve_progress_load


Builder.load_string('''
#:import MDSpinner kivymd.spinner.MDSpinner
#:import MDLabel kivymd.label.MDLabel


<ProgressLoader>:
    size_hint: None, None
    size: Window.size

    FloatLayout:

        MDCard:
            id: window_progress
            pos: (Window.width // 2) - (self.width // 2), (Window.height // 2) - (self.height // 2)
            size_hint_y: None
            size_hint_x: .8
            height: self.minimum_height
            spacing: dp(10)
            padding: dp(10)#, dp(50), dp(10), dp(20)

            MDSpinner
                id: spinner
                size_hint: None, None
                size: dp(46), dp(46)

            MDLabel:
                id: label_download
                shorten: True
                max_lines: 1
                halign: 'left'
                valign: 'top'
                text_size: self.width, None
                size_hint_y: None
                height: spinner.height
'''
)


class ProgressLoader(ModalView):
    path_to_file = StringProperty()
    '''Путь, куда будет сохранено загруженое изображение.'''

    url_on_image = StringProperty()
    '''Ссылка на загружаемое изображение.'''
    
    label_download = StringProperty('Download')
    '''Подпись загружаемого файла.'''

    background = StringProperty(
        '%s/data/background.png' % os.path.split(__file__)[0]
    )
    '''Фоновое изображение окна.'''

    download_complete = ObjectProperty()
    '''Функция, вызываемая после успешной загрузки файла.'''

    #download_cancel = ObjectProperty(lambda x: None)
    #'''Функция, вызываемая после отмены загрузки.'''

    download_hide = ObjectProperty(lambda x: None)
    '''Функция, вызываемая при закрытии окна загрузки.'''

    download_flag = BooleanProperty(False)
    '''Если True - идёт процесс загрузки.'''

    def __init__(self, **kwargs):
        super(ProgressLoader, self).__init__(**kwargs)

    def download_start(self, *args):
        self.download_flag = True
        self.thread_download = threading.Thread(
            target=retrieve_progress_load,
            args=(self.url_on_image, self.path_to_file,
                  self.draw_progress)
        )
        self.thread_download.start()
        self.open()
        Clock.schedule_once(self.animation_progress_to_fade, 2.5)
        Clock.schedule_interval(self.waiting_download_result, 0)

    def draw_progress(self, percent):
        '''
        :type percent: int;
        :param percent: процент загрузки;

        '''

        self.ids.label_download.text = '%s: %d %%' % (self.label_download, percent)

    def waiting_download_result(self, interval):
        if retrieveprogressload.result:
            self.dismiss()
            self.download_complete(retrieveprogressload.result)
            Clock.unschedule(self.waiting_download_result)
            retrieveprogressload.result = None
            self.download_flag = False

    def animation_progress_to_fade(self, interval):
        '''Анимация уплывающего в правый верхний угол окна прогресса.'''
        
        if not self.download_flag:
           return

        animation = Animation(
            center_y=Window.height, center_x=Window.width,
            opacity=0, d=0.2, t='out_quad'
        )
        animation.bind(on_complete=lambda x, y: self.download_hide(self, None))
        animation.start(self.ids.window_progress)

    def animation_progress_from_fade(self):
        '''Анимация всплывающего в правый верхний угол окна прогресса.'''
        
        animation = Animation(
            center_y=Window.height // 2, center_x=Window.width // 2,
            opacity=1, d=0.2, t='out_quad'
        )
        animation.start(self.ids.window_progress)
        Clock.schedule_once(self.animation_progress_to_fade, 2.5)