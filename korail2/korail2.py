# -*- coding: utf-8 -*-
"""
    korail2.korail2
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""

class Korail(object):
    """Korail object"""
    _session = requests.session()

    def __init__(self, id, password):
        self.id = id
        self.password = password

    def _login(self, id, password):
        """Login to Korail server.

        :param id: Korail membership number or phone number or email.
                   membership   : xxxxxxxx (8 digits)
                   phone number : xxx-xxxx-xxxx
                   email        : xxx@xxx.xxx
        :param password: Korail account password

