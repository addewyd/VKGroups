'''
This file is responsible for testing Apps inside the VKGroups project.
'''

import os
import sys
import unittest

from kivy.clock import Clock


class AppTest(unittest.TestCase):

    def test_creator_app(self):
        print(os.path.abspath(sys.argv[0])[0])
        from vkgroups import VKGroups
        test = VKGroups
        Clock.schedule_once(test.stop, 1)
        test.run()
