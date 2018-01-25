'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

# Сохраняет контент с сервера в указанный файл.

from urllib.request import urlopen

result = None


def retrieve_progress_load(url, path, _tick_callback=None):
    '''
    :type url: str;
    :param url: ссылка на контент;

    :type path: str;
    :param path: путь для сохранения контента;

    :type _tick_callback: function;
    :param _tick_callback: функция _tick_callback из модуля progressload
                           для отрисовки прогресса загрузки;

    '''

    global result

    content = urlopen(url)
    info = content.info()
    content_length = info['Content-Length']
    if not content_length:
        result = 'Fail'
        return
    total_size = int(content_length)
    try:
        fp = open(path, 'wb')
    except OSError:
        result = 'Fail'
        return
    block_size = 8192
    count = 0

    while True:
        chunk = content.read(block_size)
        if not chunk:
            break
        fp.write(chunk)
        count += 1
        if total_size > 0:
            percent = int(count * block_size * 100 // total_size)
            if percent < 100:
                _tick_callback(percent)
            else:
                result = 'Done'

    fp.flush()
    fp.close()
    if not total_size:
        result = 'Fail'
