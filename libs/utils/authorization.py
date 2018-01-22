# -*- coding: utf-8 -*-
 
import os
import threading

from kivy.core.window import Window
from kivy.clock import Clock

from libs.createpreviousportrait import create_previous_portrait
from libs import vkrequests as vkr
from toast import toast


class GetAndSaveLoginPassword(object):

    def get_fields_login_password(self):
        login = self.password_form.ids.login.text
        password = self.password_form.ids.password.text
        group_id = self.password_form.ids.group_id.text

        return login, password, group_id

    def check_fields_login_password(self):
        login, password, group_id = self.get_fields_login_password()

        if login == '' or login.isspace():
            toast(self.translation._('Field Login empty!'))
            return
        if password == '' or password.isspace():
            toast(self.translation._('Field Password empty!'))
            return
        if not group_id.isdigit():
            toast(self.translation._('ID group is didgest!'))
            return

        self.screen.ids.load_screen.remove_widget(self.password_form)
        self.screen.ids.load_screen.ids.spinner.active = True
        self.save_login_password(login, password, group_id)

    def save_login_password(self, login, password, group_id):
        # TODO: Сохранить access_token и зашифровать его.
        self.regdata['login'] = login
        self.regdata['password'] = password
        self.config.set('General', 'regdata', self.regdata)
        self.config.set('General', 'last_group', group_id)
        self.config.write()
        self._authorization_on_vk(login, password, group_id)


class AuthorizationOnVK(object):

    def _authorization_on_vk(self, login, password, group_id, from_fail_screen=False):
        '''Если from_fail_screen == True - функция была вызвана из экрана
        ошибки подключения к Интернет.'''

        def _authorization_on_vk(interval):
            thread_authorization = threading.Thread(
                target=self.authorization_on_vk, args=(login, password, group_id)
            )
            thread_authorization.start()

        if from_fail_screen:
            self.screen.ids.load_screen.remove_widget(
                 self.screen.ids.load_screen.children[0]
            )

        self.screen.ids.load_screen.ids.status.text = \
            self.translation._('Авторизация...')
        self.screen.ids.load_screen.ids.spinner.active = True
        
        Clock.schedule_once(_authorization_on_vk, 1)

    def authorization_on_vk(self, login, password, group_id):
        result, text_error = vkr.log_in(login=login, password=password, group_id=group_id)
        if not result:
           Clock.schedule_once(lambda x:  self.show_screen_connection_failed(text_error), .5)
        else:
            self.config.set('General', 'authorization', 1)
            self.config.write()

            if not os.path.exists(self.path_to_avatar):
                self.load_avatar()
            if self.user_name == 'User':
                self.set_user_name()

            self.set_issues_in_group()
            self.set_info_for_group()

            self.screen.ids.manager.current = 'navigation button'
            Window.softinput_mode = 'below_target'  # клавиатура будет приподнимать экран

    def load_avatar(self):
            self.screen.ids.load_screen.ids.status.text = \
                self.translation._('Загрузка аватара...')
            avatar, text_error = vkr.get_user_photo(size='max')

            if avatar:
                path_to_avatar_origin = \
                    os.path.join(self.directory, 'data', 'images', 'avatar_origin.png')
                path_to_avatar_portrait = self.path_to_avatar
                with open(path_to_avatar_origin, 'wb') as avatar_origin:
                    avatar_origin.write(avatar)

                create_previous_portrait(
                    path_to_avatar_origin, path_to_avatar_portrait
                )
                os.remove(path_to_avatar_origin)
                Clock.schedule_once(lambda x: self.set_avatar(
                    path_to_avatar_portrait), 1)

    def set_info_for_group(self):
        self.screen.ids.load_screen.ids.status.text = \
            self.translation._('Получение информации о группе...')
        self.group_info, text_error = vkr.get_group_info()

    def set_user_name(self):
        self.screen.ids.load_screen.ids.status.text = \
            self.translation._('Загрузка имени пользователя...')
        name, info = vkr.get_user_name()

        if name:
            self.config.set('General', 'user_name', name.encode('utf-8'))
            self.config.write()
            self.nav_drawer.ids.user_name.text = name

    def set_issues_in_group(self):
        self.screen.ids.load_screen.ids.status.text = \
            self.translation._('Загрузка кол-ва вопросов в группе...')
        issues_in_group, info = vkr.get_issue_count()

        if issues_in_group:
            if issues_in_group > self.issues_in_group:
                new_issues = str(issues_in_group - self.issues_in_group)
                self.screen.ids.action_bar.right_action_items = \
                    [['comment-plus-outline',
                      lambda x: self.manager.screens[2].show_posts(
                          new_issues)]]

            self.config.set('General', 'issues_in_group', issues_in_group)
            self.config.write()
            self.issues_in_group = issues_in_group

