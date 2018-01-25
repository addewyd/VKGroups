'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

# Реализует вывод изображения с функцией слайда вниз для закрытия экрана просмотра.

import os
from kivy.uix.image import AsyncImage
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import hex_colormap, get_color_from_hex
from kivy.properties import StringProperty, ListProperty, ObjectProperty, \
                            BooleanProperty


Builder.load_string('''
#:import MDIconButton kivymd.button.MDIconButton
#:import MDFloatingActionButton kivymd.button.MDFloatingActionButton


<PreviousImage>:
    size_hint: None, None
    size: root.window_size

    FloatLayout:

        BoxLayout:
            id: action_box
            pos: (Window.width // 2) - (self.width // 2), Window.height - label_close.height
            size_hint_y: None
            height: dp(30)

            Widget:

            MDIconButton:
                id: action_button
                icon: 'arrow-down'
                theme_text_color: 'Custom'
                opacity: .0
                text_color: 1, 1, 1, 1

            Label:
                id: label_close
                text: root.label_release
                bold: True
                opacity: .0
                color: 1, 1, 1, 1
                text_size: self.width, None
                size_hint_y: None
                height: action_button.height
                valign: 'top'

            Widget:

        MovingImage:
            id: image
            previous_image: root
            size_hint: None, None
            source: root.link_on_image
            size: root.normalize_size_image(self.texture_size)
            pos: (Window.width // 2) - (self.width // 2), (Window.height // 2) - (self.height //2)

        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'bottom'
            size_hint_y: None
            height: dp(56)
            padding: dp(10)
        
            MDFloatingActionButton:
                id: button_save
                icon: root.icon_save
                # FIXME: Цвет иконки не меняется.
                opposite_colors: True  # иконка белого/чёрного цветов
                elevation: 8  # длинна тени
                md_bg_color: root.floating_button_color
                on_release: root.dismiss(); root.callback_on_button(self.id)
'''
)


class PreviousImage(ModalView):
    icon_save = StringProperty('content-save')
    '''Иконки, которая будет использована на кнопках.'''

    window_size = ListProperty([Window.width, Window.height])
    '''Размер окна.'''

    link_on_image = StringProperty('')
    '''Ссылка на файл.'''

    background = StringProperty(
        '%s/data/background.png' % os.path.split(__file__)[0]
    )
    '''Фоновое изображение окна.'''

    floating_button_color = ListProperty(
        get_color_from_hex(hex_colormap['teal'])
    )
    '''Цвет кнопки.'''

    callback_on_button = ObjectProperty(lambda x: None)
    '''Функция на событие кнопки.'''

    label_release = StringProperty('Pull to close')

    auto_dismiss = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(PreviousImage, self).__init__(**kwargs)

        self.previous_open = False  # закрыт или открыто превью
        self.new_pos = 0  # координаты подписей

    def show(self):
        self.previous_open = True
        self.open()

    def close(self):
        self.previous_open = False
        self.new_pos = 0
        self.dismiss()

    def animation_pull_image(self):
        if self.new_pos > 10:
            return
        elif self.new_pos > 7:
            self.ids.label_close.text = self.label_release
            self.ids.action_button.icon = 'close'

        self.new_pos += .4
        self.ids.action_box.center_y -= self.new_pos
        self.ids.label_close.opacity += .1
        self.ids.action_button.opacity += .1
        self.ids.image.opacity -= .05

    def normalize_size_image(self, image_size):
        '''Возвращает ширину и высоту изображения с разницей 50,
        если размеры изображения превышают размеры экрана.'''

        image_width, image_height = image_size
        
        return (image_width if image_width < Window.width else Window.width - 50, image_height if image_height < Window.height else Window.height - 50)


class MovingImage(AsyncImage):
    previous_image = ObjectProperty()

    def on_touch_move(self, touch):
        '''Вызывается при захвате изображения.'''

        if touch.grab_current is self:
            self.center_y -= 20
            self.previous_image.animation_pull_image()

    def on_touch_up(self, touch):
        '''Вызывается при снятии захвата с изображения.'''

        if touch.grab_current is self: 
            touch.ungrab(self)
            self.previous_image.close()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):     
            touch.grab(self)
