'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

# Создаёт, компонует и выводит на экран список постов группы
# и комментариев к ним.

import time
import re

from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_hex_from_color
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, \
                            ListProperty, NumericProperty

from libs._thread import thread
from libs.utils.work_with_dataposts import mark_links_in_post, get_info_from_post

from kivymd.label import MDLabel


class BoxPosts(FloatLayout):
    _app = ObjectProperty()
    '''<class 'program.Program'>'''

    show_comments = BooleanProperty(False)
    '''Если True - выводим комментарии.'''

    count_issues_or_comments = StringProperty('0')
    '''Количество получаемых постов/комментариев.'''

    real_count_posts_on_page = NumericProperty(0)
    '''Количество постов на странице на текущий момент.'''

    post_id = StringProperty()
    '''id поста для которого выводится список комментариев.'''

    def __init__(self, **kwargs):
        super(BoxPosts, self).__init__(**kwargs)

        self.ids.rv.data = []
        self.profiles_dict = {}
        self.copy_posts_list = []
        self.items_list = []

        with self.canvas:
            self.color = Color(0, 0, 0, 0, mode='rgba')
            self.rec = Rectangle(pos=(0, 0), size=self.size)
            self.bind(size=self.check_size, pos=self.check_pos)

    @thread
    def get_and_set_json_info_for_post_or_comments(self):
        '''Получает и присваивает json с информацией о постах/комментариях
        атрибуту items_list.'''

        self.profiles_dict, self.items_list = \
            get_info_from_post(
                self.count_issues_or_comments, self.post_id, self.show_comments
            )

    def create_attach(self, data, posts_list):
        if 'attach' in data:
            attach_list_link = []  # список ссылок в аттаче
            attach_list_photo = []  # список изображений в аттаче
            for attach_data in data['attach']:
                if attach_data['type'] == 'link':
                    text_link = self.get_text_link_from_attach(attach_data)
                    attach_list_link.append(text_link)
                elif attach_data['type'] == 'photo':
                    attach_list_photo.append(attach_data['photo'])                            
            if attach_list_photo.__len__():
                posts_list.append({
                    'viewclass': 'AttachPhoto',
                    'attach_list': attach_list_photo,
                    'height': dp(100)
                })
            if attach_list_link.__len__():
                posts_list.append({
                    'viewclass': 'AttachLink',
                    'attach_list': attach_list_link,
                    'height': dp(100)
                }) 

    def create_post_and_comments(self, items_posts):
        '''Формирует список постов/комментариев.'''

        def create_post_and_comments():
            # Создание списка постов.
            if not self.show_comments:
                posts_list.append({
                    'viewclass': 'Post',
                    'index': index,
                    'author_date':
                        '[size=16][b]%s[/b][/size]\n[size=14]%s[/size]' % (
                            data['author_name'], data['date']),
                    'text_post': data['text_post'],
                    'user_id': data['author_id'],
                    'count_comments': data['count_comments'],
                    'link_on_avatar': data['link_on_avatar_author'],
                    'post_id': data['post_id'],
                    'status_user': data['status_user_icon'],
                    'instance_box_posts': self,
                    'height': dp(250)
                })
            # Создание списка комментариев к посту.
            else:
                self.real_count_posts_on_page += 1
                posts_list.append({
                    'index': index,
                    'viewclass': 'Comment',
                    'author_date':
                        '[size=16][b]%s[/b][/size]\n[size=14]%s[/size]' % (
                            data['author_name'], data['date']),
                    'text_post': data['text_post'],
                    'link_on_avatar': data['link_on_avatar_author'],
                    'comment_id': data['comment_id'],
                    'user_id': data['author_id'],
                    'whom_name': data['whom_name'],
                    'instance_box_posts': self,
                    'height': dp(250)
                })
            # Создание бокса с аттачами.
            self.create_attach(data, posts_list)

        if self.show_comments:
            posts_list = self.ids.rv.data
        else:
            posts_list = self.copy_posts_list
        for index, items_dict in enumerate(items_posts):
            data = self.get_info_for_post(items_dict)
            create_post_and_comments()

        if not self.show_comments:
            self.copy_rv_data = posts_list
        self.ids.rv.data = posts_list
        if self.show_comments:
            self.ids.rv.scroll_y = 1

    def get_text_link_from_attach(self, attach_data):
        '''Возвращает текст вида -

        'Описание ссылки
        https://адрес_ссылки'

        и аттачей типа "link".'''

        title_link = attach_data['link']['title']
        if title_link == '':
            if 'caption' in attach_data['link']:
                title_link = attach_data['link']['caption']
        title_link = '\n[b]%s[/b]\n' % title_link

        return title_link + mark_links_in_post(attach_data['link']['url'] + '\n', self._app.PATTERN_REPLACE_LINK)

    def get_info_for_post(self, items_dict=None, add_commented_post=False):
        '''Возвращает словарь с информацией о посте/комментарии.'''

        def get_text_comment_with_addressee(text_post):
            '''Возвращает и приводит текст комментария вида
            "[id12345|NameAuthor]Текст..." к виду "NameAuthor, Текст...".
            '''

            # Ищем в комментариях, кому адресовано -
            # подстроку вида '[id12345|NameAuthor]'.
            count = re.match(self._app.PATTERN_WHOM_COMMENT, text_post)
            if count:
                count = count.group()
                # id и имя автора, которому написан комментарий.
                whom_id, whom_name = \
                    count.replace('[', '').replace(']', '').split('|')
                text_post = text_post.replace(count, '')
                text_post = '[b][color=%s]\n%s[/b][/color]%s/n' % (
                    get_hex_from_color(self._app.theme_cls.primary_color),
                    whom_name, mark_links_in_post(text_post, self._app.PATTERN_REPLACE_LINK)
                )
            else:
                text_post = '\n' + text_post

            return text_post

        def set_name_avatar_date():
            '''Имя, аватар, дата поста/комментария.'''

            if not add_commented_post:  # для постов/комментариев
                data['author_id'] =  user_id
                data['author_name'] = \
                    self.profiles_dict[user_id]['author_name']
                data['link_on_avatar_author'] = \
                    self.profiles_dict[user_id]['avatar']
                data['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    items_dict['date']
                    )
                )

        def set_icon_status():
            '''Добавляет в словарь data иконку статуса пользователя:
            с компьютера/мобильного/offline.'''

            if not add_commented_post:
                if self.profiles_dict[
                        user_id]['author_online']:
                    data['status_user_icon'] = self._app.DEVISE_ONLINE[
                        self.profiles_dict[user_id]['device']
                    ]
                else:
                    data['status_user_icon'] = self._app.DEVISE_ONLINE[0]
            else:
                data['status_user_icon'] = self._app.DEVISE_ONLINE[0]

        if items_dict is None:
            items_dict = {}

        data = {}
        if items_dict['from_id'] not in self.profiles_dict:
            user_id = -items_dict['from_id']
        else:
            user_id = items_dict['from_id']

        # Для комментариев.
        if self.show_comments:
            text_post = get_text_comment_with_addressee(items_dict['text'])
            data['whom_name'] = \
                self.profiles_dict[items_dict['from_id']]['author_name']
            data['text_post'] = text_post

            if 'reply_to_comment' in items_dict:
                data['comment_id'] = str(items_dict['id'])
            else:
                data['comment_id'] = ''
        # Для поста.
        else:
            data['text_post'] = '%s\n' % mark_links_in_post(
                items_dict['text'], self._app.PATTERN_REPLACE_LINK
            )
            data['post_id'] = str(items_dict['id'])
            data['count_comments'] = str(items_dict['comments']['count'])

        if 'attachments' in items_dict:
            data['attach'] = items_dict['attachments']

        set_name_avatar_date()
        set_icon_status()

        return data

    def show_posts(self, open_screen_posts=False):
        '''Открывает вкладку с постами/комментариями группы.'''

        def check_posts_dict(interval):
            if len(self.items_list):
                #toast(str(self.real_count_posts_on_page + 20 ))
                #toast(str( self.items_list.__len__() ))
                self.create_post_and_comments(self.items_list)
                # Если экран для списка постов ещё не создан.
                if not open_screen_posts:
                    self._app.current_screen_tab.add_widget(self)
                    self._app.current_tab_manager.current = self._app.name_press_tab

                Clock.unschedule(check_posts_dict)
                self._app.load_dialog.dismiss()

        self._app.load_dialog.open()
        self.count_issues_or_comments = str(int(self.count_issues_or_comments) + 20)
        self.get_and_set_json_info_for_post_or_comments()
        Clock.schedule_interval(check_posts_dict, 0)

    def check_pos_scroll(self, pos_scroll):
        '''Вызывается при скроллинге списка постов/комментариев.
        Вызывает функцию обновления списка при достижении его конца.'''

        if pos_scroll == 0:
            # Если комментариев к посту меньше установленного количества, - выходим...
            if self._app.count_issues > self.items_list.__len__():
                return
            # ... иначе - подгружаем на страницу следующую порцию комментариев.
            else:
                self.show_posts(open_screen_posts=True)
                #toast(str( self.ids.rv.data.__len__()))

    def check_pos(self, instance, pos):
        self.rec.pos = pos

    def check_size(self, instance, size):
        self.rec.size = size
