'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from libs.vkrequests import get_issues, get_comments


def mark_links_in_post(
    post: str, pattern: 'регулярное выражение для поиска ссылок в тексте постов/комментариев' ,
    link_color='78a5a3ff') -> str:
    '''Находит в тексте поста ссылки и маркирует их согласно
    форматированию ссылок в Kivy.

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


def get_info_from_post(count_issues: str, post_id: str, comments=False) -> tuple:
    '''
    :param count_issues: количество получаемых постов;
    :param post_id: id поста для которого получаем комментарии;
    :param comments: если True -получаем комментарии;

    Возвращает словарь с информацией об авторах постов:
        {20746979: {
            'avatar': 'https://pp.userapi.com/c625531/v625531979/1be93/McNUtQxqHWg.jpg', 
            'author_name': 'Стас Каблуков',
            'author_online': 0
            }, ... };

    Список словарей с информацией о постах:
        [
            {
                'id': 1229,
                'from_id': -99411738, 
                'owner_id': -99411738, 
                'date': 1516659416, 
                'marked_as_ads': 0, 
                'post_type': 'post', 
                'text': "Текст поста", 
                'can_delete': 1, 
                'can_pin': 1, 
                'attachments': [список словарей с информацией об аттачах], 
                'post_source': {'type': 'mvk'}, 
                'comments': {'count': 0, 'can_post': 1}, 
                'likes': {'count': 3, 
                'user_likes': 0, 
                'can_like': 1, 
                'can_publish': 1}, 
                'reposts': {'count': 0, 'user_reposted': 0}}, ...];

    Словарь с информацией о группе:
        {
            'id': 99411738,
            'name': 'Kivy :: Python :: Игры на Питоне', 
            'screen_name': 'kivy_ru', 
            'is_closed': 0, 
            'type': 'group', 
            'photo_50': 'https://pp.userapi.com/c841430/v841430630/55084/eCe860F1MEk.jpg',
            'photo_100': ..., 
            'photo_200': ... }.
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

    if not comments:
        post_dict = {}
        data_group = wall_posts['groups'][0]
        post_dict['avatar'] = data_group['photo_100']
        post_dict['author_name'] = data_group['name']
        post_dict['author_online'] = 1
        post_dict['device'] = 'computer'
        profiles_dict[data_group['id']] = post_dict

    return profiles_dict, wall_posts['items']
