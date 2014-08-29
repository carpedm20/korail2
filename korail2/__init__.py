# -*- coding: utf-8 -*-
"""
    korail2
    ~~~~~~~

    Korail (www.letskorail.com) wrapper for Python.

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""
from .korail2 import Korail, Passenger, AdultPassenger, ChildPassenger, SeniorPassenger, TrainType, ReserveOption
from .korail2 import KorailError, NeedToLoginError, SoldOutError, NoResultsError

__version__ = '0.0.6'
__all__ = ['Korail', 'Passenger', 'AdultPassenger', 'ChildPassenger', 'SeniorPassenger', 'TrainType', 'ReserveOption',
           'KorailError', 'NeedToLoginError', 'SoldOutError', 'NoResultsError']
