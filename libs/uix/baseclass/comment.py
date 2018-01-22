# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from kivy.uix.boxlayout import BoxLayout

from libs.utils._recycledataviewbehavior import _RecycleDataViewBehavior


class Comment(BoxLayout):
    def tap_on_answer_comment(self, comment_id, whom_name):
        '''Вызывается при тапе на строку "Ответить" комментария.

        :comment_id: id комментария, которому отвечают;
        :type comment_id: type int;

        :whom_name: имя автора комментария, которому отвечают;
        :type whom_name: type str;

        '''

        self.instance_box_posts.background_to_black = True
        self.instance_box_posts._app.show_form_for_messages(
            comment_id=comment_id,
            post_id=self.get_post_id(),
            whom_name=whom_name
        )

    def get_post_id(self):
        '''Возвращает id поста, чьи комментарии в данный момент открыты.'''

        rv = self.instance_box_posts.ids.rv
        opts = rv.layout_manager.view_opts
        instance_commented_post = rv.view_adapter.get_view(1, rv.data[1], opts[1]['viewclass'])
        return instance_commented_post.post_id


class CommentedPost(_RecycleDataViewBehavior):
    pass
