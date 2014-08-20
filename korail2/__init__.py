# -*- coding: utf-8 -*-
"""
    korail2
    ~~~~~~~

    Korail (www.letskorail.com) wrapper for Python.

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""
from .korail2 import Korail, AdultPassenger, ChildPassenger, SeniorPassenger
from .korail2 import KorailError, NeedToLoginError, SoldOutError

__version__ = '0.0.5'
__all__ = ['Korail', 'AdultPassenger', 'ChildPassenger', 'SeniorPassenger', 'KorailError', 'NeedToLoginError',
           'SoldOutError']
