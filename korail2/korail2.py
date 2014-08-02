# -*- coding: utf-8 -*-
"""
    korail2.korail2
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""

import re
import requests
from urllib import quote
try:
    import simplejson as json
except ImportError:
    import json

EMAIL_REGEX        = re.compile(r"[^@]+@[^@]+\.[^@]+")
PHONE_NUMBER_REGEX = re.compile(r"(\d{3})-(\d{3,4})-(\d{4})")

SCHEME      = "https"
KORAIL_HOST = "smart.letskorail.com"
KORAIL_PORT = "443"

KORAIL_DOMAIN = "%s://%s:%s" % (SCHEME, KORAIL_HOST, KORAIL_PORT)
KORAIL_MOBILE = "%s/classes/com.korail.mobile" % KORAIL_DOMAIN

KORAIL_LOGIN            = "%s.login.Login" % KORAIL_MOBILE
KORAIL_LOGOUT           = "%s.common.logout" % KORAIL_MOBILE
KORAIL_STATION_DB       = "%s.common.stationinfo?device=ip" % KORAIL_MOBILE
KORAIL_STATION_DB_DATA  = "%s.common.stationdata" % KORAIL_MOBILE
KORAIL_EVENT            = "%s.common.event" % KORAIL_MOBILE
KORAIL_SEARCH_SCHEDULE  = "%s.seatMovie.ScheduleView" % KORAIL_MOBILE
KORAIL_PAYMENT          = "%s/ebizmw/PrdPkgMainList.do" % KORAIL_DOMAIN
KORAIL_PAYMENT_VOUNCHER = "%s/ebizmw/PrdPkgBoucherView.do" % KORAIL_DOMAIN


class Train(object):

    #: 기차 종류
    #: 00: KTX
    #: 01: 새마을호
    #: 02: 무궁화호
    #: 03: 통근열차
    #: 04: 누리로
    #: 05: 전체 (검색시에만 사용)
    #: 06: 공학직통
    #: 07: KTX-산천
    #: 09: ITX-청춘
    train_type = None

    #: 출발역 코드
    dep_code = None

    #: 출발날짜 (yyyyMMdd)
    dep_date = None

    #: 출발시각 (hhmmss)
    dep_time = None

    #: 도착역 코드
    arr_code = None

    #: 도착 시각
    arr_time = None

    #: 인원
    count = 0

    #: 특실 예약가능 여부
    first_class = False

    #: 일반실 예약가능 여부
    general_admission = False

    def __repr__(self):
        return '[%s] %s~%s(%s~%s) [특실:%d][일반실:%d]' % (
            self.train_type.encode('utf-8'),
            self.dep_code.encode('utf-8'),
            self.dep_time.encode('utf-8'),
            self.arr_code.encode('utf-8'),
            self.arr_time.encode('utf-8'),
            self.first_class,
            self.general_admission,
        )


class Korail(object):
    """Korail object"""
    _session = requests.session()

    _device  = 'AD'
    _version = '130607001'
    _key     = 'korail1234567890'

    def __init__(self, id, password):
        self.id = id
        self.password = password

        self.login(id, password)

    def login(self, id, password):
        """Login to Korail server.

        :param id: `Korail membership number` or `phone number` or `email`
                   membership   : xxxxxxxx (8 digits) 
                   phone number : xxx-xxxx-xxxx
                   email        : xxx@xxx.xxx
        :param password: Korail account password
        """
        if EMAIL_REGEX.match(id):
            txtInputFlg = '5'
        elif PHONE_NUMBER_REGEX.match(id):
            txtInputFlg = '4'
        else:
            txtInputFlg = '2'

        url  = KORAIL_LOGIN
        data = {
            'Device'      : self._device,
            'Version'     : self._version,
            # 2 : for membership number,
            # 4 : for phone number,
            # 5 : for email,
            'txtInputFlg' : txtInputFlg,
            'txtMemberNo' : id,
            'txtPwd'      : password
        }

        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if j['strResult'] == 'SUCC':
            return True

        return False

    def logout(self):
        url = KORAIL_LOGOUT
        self._session.get(url)

    def search_trian(self, start, end, date, time, train_type='05'):
        """Search trains for specific time and date.

        :param start: A departure station  ex) 서울
        :param end: A arrival station  ex) 부산
        :param date: A departure date in `yyyyMMdd` format
        :param time: A departure time in `hhmmss` format
        :param train_type: A type of train
                           - 00: KTX, KTX-산천
                           - 01: 새마을호
                           - 02: 무궁화호
                           - 03: 통근열차
                           - 04: 누리로
                           - 05: 전체 (기본값)
                           - 06: 공학직통
                           - 09: ITX-청춘
        """
        url  = KORAIL_SEARCH_SCHEDULE
        data = {
            'Version'        : self._version,
            'Key'            : self._key,
            'radJobId'       : '1',
            'txtMenuId'      : '11',
            'selGoTrain'     : train_type,
            'txtGoAbrdDt'    : date, #'20140803',
            'txtGoStart'     : quote(start),
            'txtGoEnd'       : quote(end),
            'txtGoHour'      : time, #'071500',
            'txtPsgFlg_1'    : '1',
            'txtPsgFlg_2'    : '0',
            'txtPsgFlg_3'    : '0',
            'txtPsgFlg_4'    : '0',
            'txtPsgFlg_5'    : '0',
            'txtCardPsgCnt'  : '0',
            'txtSeatAttCd_2' : '00',
            'txtSeatAttCd_3' : '00',
            'txtSeatAttCd_4' : '15',
            'h_cert_no'      : '',
            'h_pwd'          : '',
            'txtJobDv'       : ''
        }
        print data
        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if j['strResult'] == 'FAIL':
            h_msg_cd  = j['h_msg_cd'].encode('utf-8')
            h_msg_txt = j['h_msg_txt'].encode('utf-8')

            raise Exception("%s (%s)" % (h_msg_txt, h_msg_cd))
        return j
