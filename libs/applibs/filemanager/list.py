# -*- coding: utf-8 -*-
#
# Modified module list.py from package KivyMD
#

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, \
    ListProperty, OptionProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout

try:
    import kivymd.material_resources as m_res
    from kivymd.ripplebehavior import RectangularRippleBehavior
    from kivymd.theming import ThemableBehavior
    from kivymd.list import BaseListItem, IRightBody, IRightBodyTouch, ILeftBody, ILeftBodyTouch
except ImportError:
    raise ImportError('Install package kivymd')


Builder.load_string('''
#:import m_res kivymd.material_resources


<ModifiedBaseListItem>:
    size_hint_y: None

    canvas:
        Color:
            rgba: self.theme_cls.divider_color if root.divider is not None else (0, 0, 0, 0)

        Line:
            points: (root.x ,root.y, root.x+self.width, root.y)\
                    if root.divider == 'Full' else\
                    (root.x+root._txt_left_pad, root.y,\
                    root.x+self.width-root._txt_left_pad-root._txt_right_pad,\
                    root.y)

    BoxLayout:
        id: _text_container
        orientation: 'vertical'
        pos: root.pos
        padding: root._txt_left_pad, root._txt_top_pad, root._txt_right_pad, root._txt_bot_pad

        MDLabel:
            id: _lbl_primary
            text: root.text
            font_style: root.font_style
            theme_text_color: root.theme_text_color
            text_color: root.text_color
            size_hint_y: None
            shorten: True
            max_lines: 1
            height: self.texture_size[1]

        MDLabel:
            id: _lbl_secondary
            text: '' if root._num_lines == 1 else root.secondary_text
            font_style: root.secondary_font_style
            theme_text_color: root.secondary_theme_text_color
            text_color: root.secondary_text_color
            size_hint_y: None
            height: 0 if root._num_lines == 1 else self.texture_size[1]
            shorten: True if root._num_lines == 2 else False

<ModifiedOneLineIconListItem>:
    BoxLayout:
        id: _left_container
        size_hint: None, None
        x: root.x + dp(16)
        y: root.y + root.height/2 - self.height/2
        size: dp(48), dp(48)
''')


class ModifiedBaseListItem(ThemableBehavior, RectangularRippleBehavior,
                   ButtonBehavior, FloatLayout):
    '''Base class to all ListItems. Not supposed to be instantiated on its own.
    '''

    text = StringProperty()
    '''Text shown in the first line.

    :attr:`text` is a :class:`~kivy.properties.StringProperty` and defaults
    to "".
    '''
    
    text_color = ListProperty(None)
    ''' Text color used if theme_text_color is set to 'Custom' '''

    font_style = OptionProperty(
        'Subhead', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                            'Headline', 'Display1', 'Display2', 'Display3',
                            'Display4', 'Button', 'Icon'])
    
    theme_text_color = StringProperty('Primary',allownone=True)
    ''' Theme text color for primary text '''

    secondary_text = StringProperty()
    '''Text shown in the second and potentially third line.

    The text will wrap into the third line if the ListItem's type is set to
    \'one-line\'. It can be forced into the third line by adding a \\n
    escape sequence.

    :attr:`secondary_text` is a :class:`~kivy.properties.StringProperty` and
    defaults to "".
    '''
    
    secondary_text_color = ListProperty(None)
    ''' Text color used for secondary text if secondary_theme_text_color 
    is set to 'Custom' '''
    
    secondary_theme_text_color = StringProperty('Secondary',allownone=True)
    ''' Theme text color for secondary primary text '''
    
    secondary_font_style = OptionProperty(
        'Body1', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                          'Headline', 'Display1', 'Display2', 'Display3',
                          'Display4', 'Button', 'Icon'])

    divider = OptionProperty('Full', options=['Full', 'Inset', None], allownone=True)

    _txt_left_pad = NumericProperty(dp(16))
    _txt_top_pad = NumericProperty()
    _txt_bot_pad = NumericProperty()
    _txt_right_pad = NumericProperty(m_res.HORIZ_MARGINS)
    _num_lines = 2

class ModifiedOneLineListItem(ModifiedBaseListItem):
    '''
    A one line list item
    '''
    _txt_top_pad = NumericProperty(dp(16))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 1

    def __init__(self, **kwargs):
        super(ModifiedOneLineListItem, self).__init__(**kwargs)
        self.height = dp(48)


class ContainerSupport:
    '''Overrides add_widget in a ListItem to include support for I*Body
    widgets when the appropiate containers are present.
    '''
    _touchable_widgets = ListProperty()

    def add_widget(self, widget, index=0):
        if issubclass(widget.__class__, ILeftBody):
            self.ids['_left_container'].add_widget(widget)
        elif issubclass(widget.__class__, ILeftBodyTouch):
            self.ids['_left_container'].add_widget(widget)
            self._touchable_widgets.append(widget)
        elif issubclass(widget.__class__, IRightBody):
            self.ids['_right_container'].add_widget(widget)
        elif issubclass(widget.__class__, IRightBodyTouch):
            self.ids['_right_container'].add_widget(widget)
            self._touchable_widgets.append(widget)
        else:
            return super(ModifiedBaseListItem, self).add_widget(widget)

    def remove_widget(self, widget):
        super(ModifiedBaseListItem, self).remove_widget(widget)
        if widget in self._touchable_widgets:
            self._touchable_widgets.remove(widget)

    def on_touch_down(self, touch):
        if self.propagate_touch_to_touchable_widgets(touch, 'down'):
            return
        super(ModifiedBaseListItem, self).on_touch_down(touch)

    def on_touch_move(self, touch, *args):
        if self.propagate_touch_to_touchable_widgets(touch, 'move', *args):
            return
        super(ModifiedBaseListItem, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch):
        if self.propagate_touch_to_touchable_widgets(touch, 'up'):
            return
        super(ModifiedBaseListItem, self).on_touch_up(touch)

    def propagate_touch_to_touchable_widgets(self, touch, touch_event, *args):
        triggered = False
        for i in self._touchable_widgets:
            if i.collide_point(touch.x, touch.y):
                triggered = True
                if touch_event == 'down':
                    i.on_touch_down(touch)
                elif touch_event == 'move':
                    i.on_touch_move(touch, *args)
                elif touch_event == 'up':
                    i.on_touch_up(touch)
        return triggered


class ModifiedOneLineIconListItem(ContainerSupport, ModifiedOneLineListItem):
    _txt_left_pad = NumericProperty(dp(72))
