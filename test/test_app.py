'''
This file is responsible for testing Apps inside the VKGroups project.
'''

import unittest


class AppTest(unittest.TestCase):

    def test_vkgroups_app(self):
        from vkgroups import VKGroups
        vkgroups = VKGroups()
        vkgroups.run()
