# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

# Форма для ввода текста, используемая в мессаджерах.

from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.widget import WidgetException
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty, \
                            ObjectProperty, StringProperty, DictProperty
from kivy.metrics import dp

try:
    from kivymd.card import MDCard
except ImportError:
    raise ImportError('Install package KivyMD')


Builder.load_string('''
#:import MDTextField kivymd.textfields.MDTextField
#:import MDIconButton kivymd.button.MDIconButton


<FormForMessages>:
    padding: dp(10), dp(50), dp(10), dp(20)
    spacing: dp(10)
    size_hint: 1, None
    height: self.minimum_height
    orientation: 'vertical'

    canvas:
        Color:
            rgba:
                root.background
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:

        MDIconButton:
            id: add_foto
            size_hint: None, None
            size: dp(42), dp(42)
            icon: 'camera'
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
            on_release: root.callback(flag='FOTO', kwargs=root.kwargs)

        MDTextField:
            id: text_form
            font_size: '12sp'
            size_hint_y: None
            height: dp(100)
            on_focus: root._focus = True if not root._focus else False
            message_mode: 'persistent'
            # TODO: при мультистроковом режиме текст выходит за границы
            # высоты текстового поля.
            # multiline: True

        BoxLayout:
            size_hint_x: None
            width: dp(94)
            spacing: dp(10)

            MDIconButton:
                id: add_file
                size_hint: None, None
                size: dp(42), dp(42)
                theme_text_color: 'Custom'
                text_color: app.theme_cls.primary_color
                icon: 'pill'
                on_release: root.callback(flag='FILE', kwargs=root.kwargs)

            MDIconButton:
                id: send
                size_hint: None, None
                size: dp(42), dp(42)
                icon: 'near-me'
                theme_text_color: 'Custom'
                text_color: app.theme_cls.primary_color
                on_release: root.callback(flag='SEND', kwargs=root.kwargs)
''')


class FormForMessages(MDCard):
    visible = BooleanProperty(False)
    '''Если True - окно с формой открыто.'''

    callback = ObjectProperty()
    '''Функция обрабатываемая события формы.'''

    background = ListProperty([0.9686274509803922, 0.9686274509803922, 0.9686274509803922, .9])
    '''Фон формы.'''

    text_from_form = StringProperty()
    '''Текст формы.'''

    kwargs = DictProperty()
    '''Словарь аргументов для функции callback.'''

    _parent_instance = ObjectProperty()

    _color_parent_instance = ObjectProperty()

    _focus = BooleanProperty(False)
    '''True, если фокус поля ввода текста установлен.'''

    def __init__(self, **kwargs):
        super(FormForMessages, self).__init__(**kwargs)
        self.window_width = Window.width
        Window.softinput_mode = 'below_target'

    def clear(self):
        '''Очищает форму.'''

        self.ids.text_form.text = ''
        self.ids.text_form.hint_text = ''

    def show(self, **kwargs):
        '''Выводит форму для ввода текста.

        :parent_instance: виджет, на который будет выведена форма;
                          должен быть наследником от FloatLayout;
        :type parent_instance: <type 'kivy.weakproxy.WeakProxy'>
        :text_form: текст, который будет добавлен в форму;
        :type text_form: str;

        '''

        try:
            self.text_from_form = kwargs.get('text_form', '')
            self._parent_instance = kwargs['parent_instance']

            if not self._color_parent_instance:
                with self._parent_instance.canvas:
                    self._color_parent_instance = Color(0, 0, 0, 0, mode='rgba')
                    self.rec = Rectangle(pos=self.pos, size=Window.size)
                    self._parent_instance.bind(size=self.check_size, pos=self.check_pos)

            self.visible = True
            self.ids.text_form.hint_text = self.text_from_form

            animation = Animation(
                size=(self.window_width, 120), duration=1, t='out_bounce'
            )
            animation &= Animation(y=dp(10), duration=.5, t='in_quad')
            animation += Animation(size=(self.window_width, 120), duration=1)
            self._parent_instance.add_widget(self)
            animation.start(self)
        except WidgetException:
            self.hide()

    def hide(self):
        '''Скрывает форму.'''

        self.visible = False
        self.clear()

        animation = Animation(
            size=(self.window_width, 120), duration=.1, t='out_bounce'
        )
        animation &= Animation(y=dp(.1), duration=.1, t='in_quad')
        animation.start(self)
        animation.bind(on_complete=self.remove)
      
    def remove(self, *args):
        self._parent_instance.remove_widget(self)

    def on_visible(self, instance, value):
        '''Затемняет фон родительского виджета при открытии формы.'''

        for obj in self._parent_instance.canvas.children:
            if obj == self._color_parent_instance:
                self._color_parent_instance.rgba[3] = 0 if not value else .5
                break
 
    def check_pos(self, instance, pos):
        self.rec.pos = pos

    def check_size(self, instance, size):
        self.rec.size = size
