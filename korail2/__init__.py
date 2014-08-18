# -*- coding: utf-8 -*-
"""
    korail2
    ~~~~~~~

    Korail (www.letskorail.com) wrapper for Python.

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""
from .korail2 import Korail
from .korail2 import KorailError, NeedToLoginError, NoResultsError

__version__ = '0.0.5'
__all__ = ['Korail', 'KorailError', 'NeedToLoginError', 'NoResultsError']
