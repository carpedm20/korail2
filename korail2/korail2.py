# -*- coding: utf-8 -*-
"""
    korail2.korail2
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""

import re
import requests
from datetime import datetime
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
    """Korail train object. Highly inspired by `korail.py
    <https://raw.githubusercontent.com/devxoul/korail/master/korail/korail.py>`_
    by `Suyeol Jeon <http://xoul.kr/>`_ at 2014.
    """

    #: 기차 종류
    #: 00: KTX
    #: 01: 새마을호
    #: 02: 무궁화호
    #: 03: 통근열차
    #: 04: 누리로
    #: 05: 전체 (검색시에만 사용)
    #: 06: 공학직통
    #: 07: KTX-산천
    #: 08: ITX-새마을
    #: 09: ITX-청춘
    train_type = None # h_trn_clsf_cd, selGoTrain

    #: 기차 종류 이름
    train_type_name = None # h_trn_clsf_nm

    #: 기차 번호
    train_no = None # h_trn_no

    #: 지연 시간 (hhmm)
    delay_time = None # h_expct_dlay_hr

    #: 출발역 이름
    dep_name = None # h_dpt_rs_stn_nm

    #: 출발역 코드
    dep_code = None # h_dpt_rs_stn_cd

    #: 출발날짜 (yyyyMMdd)
    dep_date = None # h_dpt_dt

    #: 출발 시각1 (hhmmss)
    dep_time = None # h_dpt_tm

    #: 출발 시각2 (hh:mm)
    dep_time_qb = None # h_dpt_tm_qb

    #: 도착역 이름
    arr_name = None # h_arv_rs_stn_nm

    #: 도착역 코드
    arr_code = None # h_arv_rs_stn_cd

    #: 도착날짜 (yyyyMMdd)
    dep_date = None # h_arv_dt

    #: 도착 시각1 (hhmmss)
    arr_time = None # h_arv_tm

    #: 도착 시각2 (hh:mm)
    arr_time_qb = None # h_arv_tm_qb

    #: 예약 가능 여부
    reserve_possible = False # h_rsv_psb_flg ('Y' or 'N')

    #: 예약 가능 여부
    reserve_possible_name = None # h_rsv_psb_nm

    #: 특실 예약가능 여부
    #: 00: 특실 없음
    #: 11: 예약 가능
    #: 13: 매진
    special_seat = False # h_spe_rsv_cd

    #: 일반실 예약가능 여부
    #: 00: 일반실 없음
    #: 11: 예약 가능
    #: 13: 매진
    general_seat = False # h_gen_rsv_cd

    def __repr__(self):
        repr_str = '[%s #%s] %s~%s(%s~%s) ' % (
            self.train_type_name,
            self.train_no,
            self.dep_name,
            self.arr_name,
            self.dep_time_qb,
            self.arr_time_qb,
        )

        if self.special_seat != '00':
            if  self.special_seat == '11':
                special_seat = True
            else:
                special_seat = False
            repr_str += '[특실:%d]' % special_seat

        if self.general_seat != '00':
            if  self.general_seat == '11':
                general_seat = True
            else:
                general_seat = False
            repr_str += '[일반실:%d]' % general_seat

        return repr_str + " " + self.reserve_possible_name.replace('\n',' ')


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

    def search_train(self, dep, arr, date=None, time=None, train_type='05'):
        """Search trains for specific time and date.

        :param dep: A departure station in Korean  ex) '서울'
        :param arr: A arrival station in Korean  ex) '부산'
        :param date: (optional) A departure date in `yyyyMMdd` format
        :param time: (optional) A departure time in `hhmmss` format
        :param train_type: (optional) A type of train
                           - 00: KTX, KTX-산천
                           - 01: 새마을호
                           - 02: 무궁화호
                           - 03: 통근열차
                           - 04: 누리로
                           - 05: 전체 (기본값)
                           - 06: 공학직통
                           - 07: KTX-산천
                           - 08: ITX-새마을
                           - 09: ITX-청춘
        """
        if date == None:
            date = datetime.now().strftime("%Y%m%d")
        if time == None:
            time = datetime.now().strftime("%H%M%S")

        url  = KORAIL_SEARCH_SCHEDULE
        data = {
            'Device'         : self._device,
            'Version'        : self._version,
            'Key'            : self._key,
            'radJobId'       : '1',
            'txtMenuId'      : '11',
            'selGoTrain'     : train_type,
            'txtGoAbrdDt'    : date, #'20140803',
            'txtGoStart'     : dep,
            'txtGoEnd'       : arr,
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

        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if j['strResult'] == 'FAIL':
            h_msg_cd  = j['h_msg_cd'].encode('utf-8')
            h_msg_txt = j['h_msg_txt'].encode('utf-8')

            raise Exception("%s (%s)" % (h_msg_txt, h_msg_cd))
        else:
            train_infos = j['trn_infos']['trn_info']

            trains = []

            for info in train_infos:
                for i in info:
                    info[i] = info[i].encode('utf-8')

                train = Train()
                train.train_type      = info['h_trn_clsf_cd']
                train.train_type_name = info['h_trn_clsf_nm']
                train.train_no        = info['h_trn_no']
                train.delay_time      = info['h_expct_dlay_hr']

                train.dep_name    = info['h_dpt_rs_stn_nm']
                train.dep_code    = info['h_dpt_rs_stn_cd']
                train.dep_date    = info['h_dpt_dt']
                train.dep_time_qb = info['h_dpt_tm_qb']

                train.arr_name    = info['h_arv_rs_stn_nm']
                train.arr_code    = info['h_arv_rs_stn_cd']
                train.arr_date    = info['h_arv_dt']
                train.arr_time    = info['h_arv_tm']
                train.arr_time_qb = info['h_arv_tm_qb']

                train.reserve_possible      = info['h_rsv_psb_flg']
                train.reserve_possible_name = info['h_rsv_psb_nm']

                train.special_seat = info['h_spe_rsv_cd']
                train.general_seat = info['h_gen_rsv_cd']

                trains.append(train)

            return trains
