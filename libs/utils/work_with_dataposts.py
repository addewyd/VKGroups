# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from libs.vkrequests import get_issues, get_comments


def mark_links_in_post(post, pattern, link_color='78a5a3ff'):
    '''Находит в тексте поста ссылки и маркирует их согласно
    форматированию ссылок в Kivy.

    :param pattern: регулярное выражение для поиска ссылок в тексте постов/комментариев;
    :type pattern: <type '_sre.SRE_Pattern'>;

    '''

    def replace(mo):
        if mo:
            link = mo.group()
            marker = \
                f'[ref={link}][color={link_color}]{link}[/color][/ref]'

            if link.startswith('http') or link.startswith('https'):
                return marker

    mark_text = pattern.sub(replace, post)
    return mark_text


def get_info_from_post(count_issues, post_id='', comments=False):
    '''
    :type count_issues: str;
    :param count_issues: количество получаемых постов;
    :param post_id: id поста для которого получаем комментарии;
    :param comments: если True -получаем комментарии;

    Возвращает словарь:
    {'Имя автора поста':
        {'text': 'Текст поста', 'date': '2016-11-14 16:21:20',
         'attachments': ['', 'https://p.vk.me/c9/v60/36fe/ylDQ.jpg', ...],
         'avatar': 'https://pp.vk.me/c17/v6760/1/FdjA4ho.jpg',
         'comments': 4}, ...
    }

    '''

    if not comments:
        wall_posts, info = get_issues(offset='0', count=count_issues)
    else:
        wall_posts, info = get_comments(id=post_id, count=count_issues)

    profiles_dict = {}

    if not wall_posts:
        print(info)
        return

    for data_post in wall_posts['profiles']:
        post_dict = {}
        first_name = data_post['first_name']
        last_name = data_post['last_name']
        author_online = data_post['online']
        author_name = '%s %s' % (first_name, last_name)
        post_dict['avatar'] = data_post['photo_100']
        post_dict['author_name'] = author_name
        post_dict['author_online'] = author_online

        if author_online:
            if 'online_mobile' in data_post:
                post_dict['device'] = 'mobile'
            else:
                post_dict['device'] = 'computer'

        profiles_dict[data_post['id']] = post_dict

    return profiles_dict, wall_posts['items']
    