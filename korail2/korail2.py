# -*- coding: utf-8 -*-
"""
    korail2.korail2
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""
import re
import requests
import itertools
from datetime import datetime, timedelta
from pprint import pprint

try:
    # noinspection PyPackageRequirements
    import simplejson as json
except ImportError:
    import json

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
PHONE_NUMBER_REGEX = re.compile(r"(\d{3})-(\d{3,4})-(\d{4})")

SCHEME = "https"
KORAIL_HOST = "smart.letskorail.com"
KORAIL_PORT = "9443"

KORAIL_DOMAIN = "%s://%s:%s" % (SCHEME, KORAIL_HOST, KORAIL_PORT)
KORAIL_MOBILE = "%s/classes/com.korail.mobile" % KORAIL_DOMAIN

KORAIL_LOGIN = "%s.login.Login" % KORAIL_MOBILE
KORAIL_LOGOUT = "%s.common.logout" % KORAIL_MOBILE
KORAIL_SEARCH_SCHEDULE = "%s.seatMovie.ScheduleView" % KORAIL_MOBILE
KORAIL_TICKETRESERVATION = "%s.certification.TicketReservation" % KORAIL_MOBILE
KORAIL_REFUND = "%s.refunds.RefundsRequest" % KORAIL_MOBILE
KORAIL_MYTICKETLIST = "%s.myTicket.MyTicketList" % KORAIL_MOBILE
KORAIL_MYTICKET_SEAT = "%s.refunds.SelTicketInfo" % KORAIL_MOBILE

KORAIL_MYRESERVATIONLIST = "%s.reservation.ReservationView" % KORAIL_MOBILE
KORAIL_CANCEL = "%s.reservationCancel.ReservationCancelChk" % KORAIL_MOBILE

KORAIL_STATION_DB = "%s.common.stationinfo?device=ip" % KORAIL_MOBILE
KORAIL_STATION_DB_DATA = "%s.common.stationdata" % KORAIL_MOBILE
KORAIL_EVENT = "%s.common.event" % KORAIL_MOBILE
KORAIL_PAYMENT = "%s/ebizmw/PrdPkgMainList.do" % KORAIL_DOMAIN
KORAIL_PAYMENT_VOUCHER = "%s/ebizmw/PrdPkgBoucherView.do" % KORAIL_DOMAIN


def _get_utf8(data, key, default=None):
    v = data.get(key, default)
    if isinstance(v, basestring):
        return v.encode('utf-8')
    else:
        return v

class Schedule(object):
    """Korail train object. Highly inspired by `korail.py
    <https://raw.githubusercontent.com/devxoul/korail/master/korail/korail.py>`_
    by `Suyeol Jeon <http://xoul.kr/>`_ at 2014.
    """

    # : 기차 종류
    # : 00: KTX
    #: 01: 새마을호
    #: 02: 무궁화호
    #: 03: 통근열차
    #: 04: 누리로
    #: 05: 전체 (검색시에만 사용)
    #: 06: 공학직통
    #: 07: KTX-산천
    #: 08: ITX-새마을
    #: 09: ITX-청춘
    train_type = None  # h_trn_clsf_cd, selGoTrain

    train_group = None # h_trn_gp_cd

    #: 기차 종류 이름
    train_type_name = None  # h_trn_clsf_nm

    #: 기차 번호
    train_no = None  # h_trn_no

    #: 출발역 이름
    dep_name = None  # h_dpt_rs_stn_nm

    #: 출발역 코드
    dep_code = None  # h_dpt_rs_stn_cd

    #: 출발 날짜 (yyyyMMdd)
    dep_date = None  # h_dpt_dt

    #: 출발 시각 (hhmmss)
    dep_time = None  # h_dpt_tm

    #: 도착역 이름
    arr_name = None  # h_arv_rs_stn_nm

    #: 도착역 코드
    arr_code = None  # h_arv_rs_stn_cd

    #: 도착 날짜 (yyyyMMdd)
    arr_date = None  # h_arv_dt

    #: 도착 시각 (hhmmss)
    arr_time = None  # h_arv_tm

    #: 운행 날짜 (yyyyMMdd)
    run_date = None  # h_run_dt


    def __init__(self, data):

        self.train_type = _get_utf8(data, 'h_trn_clsf_cd')
        self.train_type_name = _get_utf8(data, 'h_trn_clsf_nm')
        self.train_group = _get_utf8(data, 'h_trn_gp_cd')
        self.train_no = _get_utf8(data, 'h_trn_no')
        self.delay_time = _get_utf8(data, 'h_expct_dlay_hr')

        self.dep_name = _get_utf8(data, 'h_dpt_rs_stn_nm')
        self.dep_code = _get_utf8(data, 'h_dpt_rs_stn_cd')
        self.dep_date = _get_utf8(data, 'h_dpt_dt')
        self.dep_time = _get_utf8(data, 'h_dpt_tm')

        self.arr_name = _get_utf8(data, 'h_arv_rs_stn_nm')
        self.arr_code = _get_utf8(data, 'h_arv_rs_stn_cd')
        self.arr_date = _get_utf8(data, 'h_arv_dt')
        self.arr_time = _get_utf8(data, 'h_arv_tm')

        self.run_date = _get_utf8(data, 'h_run_dt')

    def __repr__(self):
        dep_time = "%s:%s" % (self.dep_time[:2], self.dep_time[2:4])
        arr_time = "%s:%s" % (self.arr_time[:2], self.arr_time[2:4])

        dep_date = "%s월 %s일" % (int(self.dep_date[4:6]), int(self.dep_date[6:]))

        repr_str = '[%s] %s, %s~%s(%s~%s)' % (
            self.train_type_name,
            dep_date,
            self.dep_name,
            self.arr_name,
            dep_time,
            arr_time,
        )

        return repr_str


class Train(Schedule):
    # : 지연 시간 (hhmm)
    delay_time = None  # h_expct_dlay_hr

    # : 예약 가능 여부
    reserve_possible = False  # h_rsv_psb_flg ('Y' or 'N')

    #: 예약 가능 여부
    reserve_possible_name = None  # h_rsv_psb_nm

    #: 특실 예약가능 여부
    #: 00: 특실 없음
    #: 11: 예약 가능
    #: 13: 매진
    special_seat = None  # h_spe_rsv_cd

    #: 일반실 예약가능 여부
    #: 00: 일반실 없음
    #: 11: 예약 가능
    #: 13: 매진
    general_seat = None  # h_gen_rsv_cd

    def __init__(self, data):
        super(Train, self).__init__(data)
        self.reserve_possible = _get_utf8(data, 'h_rsv_psb_flg')
        self.reserve_possible_name = _get_utf8(data, 'h_rsv_psb_nm')

        self.special_seat = _get_utf8(data, 'h_spe_rsv_cd')
        self.general_seat = _get_utf8(data, 'h_gen_rsv_cd')

    def __repr__(self):
        repr_str = super(Train, self).__repr__()

        if self.reserve_possible_name is not None:
            seats = []
            if self.has_special_seat():
                seats.append("특실")

            if self.has_general_seat():
                seats.append("일반실")

            repr_str += " " + (",".join(seats)) + " " + self.reserve_possible_name.replace('\n', ' ')

        return repr_str

    def has_special_seat(self):
        return self.special_seat == '11'

    def has_general_seat(self):
        return self.general_seat == '11'

    def has_seat(self):
        return self.has_general_seat() or self.has_special_seat()


class Ticket(Train):
    """Ticket object"""

    # : 열차 번호
    car_no = None  # h_srcar_no

    # : 자리 갯수
    seat_no_count = None  # h_seat_cnt  ex) 001

    #: 자리 번호
    seat_no = None  # h_seat_no

    #: 자리 번호
    seat_no_end = None  # h_seat_no_end

    #: 구매자 성함
    buyer_name = None  # h_buy_ps_nm

    #: 구매 날짜 (yyyyMMdd)
    sale_date = None  # h_orgtk_sale_dt

    #: 구매 정보1
    sale_info1 = None  # h_orgtk_wct_no

    #: 구매 정보2
    sale_info2 = None  # h_orgtk_ret_sale_dt

    #: 구매 정보3
    sale_info3 = None  # h_orgtk_sale_sqno

    #: 구매 정보4
    sale_info4 = None  # h_orgtk_ret_pwd

    #: 구매 가격
    price = None  # h_rcvd_amt  ex) 00013900

    def __init__(self, data):
        super(Ticket, self).__init__(data)

        self.seat_no_end = _get_utf8(data, 'h_seat_no_end')
        self.seat_no_count = int(_get_utf8(data, 'h_seat_cnt'))

        self.buyer_name = _get_utf8(data, 'h_buy_ps_nm')
        self.sale_date = _get_utf8(data, 'h_orgtk_sale_dt')
        self.sale_info1 = _get_utf8(data, 'h_orgtk_wct_no')
        self.sale_info2 = _get_utf8(data, 'h_orgtk_ret_sale_dt')
        self.sale_info3 = _get_utf8(data, 'h_orgtk_sale_sqno')
        self.sale_info4 = _get_utf8(data, 'h_orgtk_ret_pwd')
        self.price = int(_get_utf8(data, 'h_rcvd_amt'))

        self.car_no = _get_utf8(data, 'h_srcar_no')
        self.seat_no = _get_utf8(data, 'h_seat_no')

    def __repr__(self):
        repr_str = super(Train, self).__repr__()

        repr_str += " => %s호" % self.car_no

        if int(self.seat_no_count) != 1:
            repr_str += " %s~%s" % (self.seat_no, self.seat_no_end)
        else:
            repr_str += " %s" % self.seat_no

        repr_str += ", %s원" % self.price

        return repr_str

    def get_ticket_no(self):
        return "-".join(map(str, (self.sale_info1, self.sale_info2, self.sale_info3, self.sale_info4)))


class Passenger:
    """승객. Passenger List를 검색과 예약에 쓰도록 한다."""
    typecode = None  # txtPsgTpCd1    : '1',   #손님 종류 (어른 1, 어린이 3)
    discount_type = '000'  # txtDiscKndCd1  : '000', #할인 타입 (경로, 동반유아, 군장병 등..)
    count = 1  # txtCompaCnt1   : '1',   #인원수
    card = ''  # txtCardCode_1  : '',    #할인카드 종류
    card_no = ''  # txtCardNo_1    : '',    #할인카드 번호
    card_pw = ''  # txtCardPw_1    : '',    #할인카드 비밀번호

    @staticmethod
    def reduce(passenger_list):
        """Reduce passenger's list."""
        if filter(lambda x: not isinstance(x, Passenger), passenger_list):
            raise TypeError("Passengers must be based on Passenger")

        groups = itertools.groupby(passenger_list, lambda x: x.group_key())
        return filter(lambda x: x.count > 0, [reduce(lambda a, b: a + b, g) for k, g in groups])

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Passenger is abstract class. Do not make instance.")

    def __init_internal__(self, typecode, count=1, discount_type='000', card='', card_no='', card_pw=''):
        self.typecode = typecode
        self.count = count
        self.discount_type = discount_type
        self.card = card
        self.card_no = card_no
        self.card_pw = card_pw

    def __add__(self, other):
        assert isinstance(other, self.__class__)
        if self.group_key() == other.group_key():
            return self.__class__(count=self.count + other.count, discount_type=self.discount_type, card=self.card,
                                  card_no=self.card_no, card_pw=self.card_pw)
        else:
            raise TypeError(
                "other's group_key(%s) is not equal to self's group_key(%s)." % (other.group_key(), self.group_key()))

    def group_key(self):
        """get group string from attributes except count"""
        return "%s_%s_%s_%s_%s" % (self.typecode, self.discount_type, self.card, self.card_no, self.card_pw)

    def get_dict(self, index):
        assert isinstance(index, int)
        index = str(index)
        return {
            'txtPsgTpCd' + index: self.typecode,
            'txtDiscKndCd' + index: self.discount_type,
            'txtCompaCnt' + index: self.count,
            'txtCardCode_' + index: self.card,
            'txtCardNo_' + index: self.card_no,
            'txtCardPw_' + index: self.card_pw,
        }


# noinspection PyMissingConstructor
class AdultPassenger(Passenger):
    def __init__(self, count=1, discount_type='000', card='', card_no='', card_pw=''):
        Passenger.__init_internal__(self, '1', count, discount_type, card, card_no, card_pw)


# noinspection PyMissingConstructor
class ChildPassenger(Passenger):
    def __init__(self, count=1, discount_type='000', card='', card_no='', card_pw=''):
        Passenger.__init_internal__(self, '3', count, discount_type, card, card_no, card_pw)


# noinspection PyMissingConstructor
class SeniorPassenger(Passenger):
    def __init__(self, count=1, discount_type='131', card='', card_no='', card_pw=''):
        Passenger.__init_internal__(self, '1', count, discount_type, card, card_no, card_pw)


class TrainType:
    KTX = "100"  # "KTX, KTX-산천",
    SAEMAEUL = "101"  # "새마을호",
    MUGUNGHWA = "102"  # "무궁화호",
    TONGGUEN = "103"  # "통근열차",
    NURIRO = "102"  # "누리로",
    ALL = "109"  # "전체",
    AIRPORT = "105"  # "공항직통",
    KTX_SANCHEON = "100"  # "KTX-산천",
    ITX_SAEMAEUL = "101"  # "ITX-새마을",
    ITX_CHEONGCHUN = "104"  # "ITX-청춘",

    def __init__(self):
        raise NotImplementedError("Do not make instance.")


class ReserveOption:
    GENERAL_FIRST = "GENERAL_FIRST"  # 일반실 우선
    GENERAL_ONLY = "GENERAL_ONLY"  # 일반실만
    SPECIAL_FIRST = "SPECIAL_FIRST"  # 특실 우선
    SPECIAL_ONLY = "SPECIAL_ONLY"  # 특실만

    def __init__(self):
        raise NotImplementedError("Do not make instance.")


class Reservation(Train):
    """Revervation object"""

    # : 예약번호
    rsv_id = None  # h_pnr_no

    # : 여정 번호
    journey_no = None  # txtJrnySqno

    #: 여정 카운트
    journey_cnt = None  # txtJrnyCnt

    #: 예약변경 번호?
    rsv_chg_no = "00000"

    #: 자리 갯수
    seat_no_count = None  # h_tot_seat_cnt  ex) 001

    #: 결제 기한 날짜
    buy_limit_date = None  # h_ntisu_lmt_dt

    #: 결제 기한 시간
    buy_limit_time = None  # h_ntisu_lmt_tm

    #: 예약 가격
    price = None  # h_rsv_amt  ex) 00013900

    #: 열차 번호 (Not implemented)
    car_no = None  # h_srcar_no

    #: 자리 번호 (Not implemented)
    seat_no = None  # h_seat_no

    #: 자리 번호 (Not implemented)
    seat_no_end = None  # h_seat_no_end

    def __init__(self, data):
        super(Reservation, self).__init__(data)
        # 이 두 필드가 결과에 빠져있음
        self.dep_date = _get_utf8(data, 'h_run_dt')
        self.arr_date = _get_utf8(data, 'h_run_dt')

        self.rsv_id = _get_utf8(data, 'h_pnr_no')
        self.seat_no_count = int(_get_utf8(data, 'h_tot_seat_cnt'))
        self.buy_limit_date = _get_utf8(data, 'h_ntisu_lmt_dt')
        self.buy_limit_time = _get_utf8(data, 'h_ntisu_lmt_tm')
        self.price = int(_get_utf8(data, 'h_rsv_amt'))
        self.journey_no = _get_utf8(data, 'txtJrnySqno', "001")
        self.journey_cnt = _get_utf8(data, 'txtJrnyCnt', "01")
        self.rsv_chg_no = _get_utf8(data, 'hidRsvChgNo', "00000")


        # 좌석정보 추가 업데이트 필요.
        # self.car_no = None
        # self.seat_no = None
        # self.seat_no_end = None



    def __repr__(self):
        repr_str = super(Reservation, self).__repr__()

        repr_str += ", %s원(%s석)" % (self.price, self.seat_no_count)

        buy_limit_time = "%s:%s" % (self.buy_limit_time[:2], self.buy_limit_time[2:4])

        buy_limit_date = "%s월 %s일" % (int(self.buy_limit_date[4:6]), int(self.buy_limit_date[6:]))

        repr_str += ", 구입기한 %s %s" % (buy_limit_date, buy_limit_time)

        return repr_str


class KorailError(Exception):
    """Korail Base Error Class"""
    codes = set()

    # noinspection PyPep8Naming,PyUnresolvedReferences
    class __metaclass__(type):
        def __contains__(cls, item):
            return item in cls.codes

    def __init__(self, msg, code):
        self.msg = msg
        self.code = code

    def __str__(self):
        return "%s (%s)" % (self.msg, self.code)


class NeedToLoginError(KorailError):
    """Korail NeedToLogin Error Class"""
    codes = {'P058'}

    def __init__(self, code=None):
        KorailError.__init__(self, "Need to Login", code)


class NoResultsError(KorailError):
    """Korail NoResults Error Class"""
    codes = {'P100',
             'WRG000000',
             'WRD000061',  # 직통열차는 없지만, 환승으로 조회 가능합니다.
    }

    def __init__(self, code=None):
        KorailError.__init__(self, "No Results", code)


class SoldOutError(KorailError):
    codes = {'ERR211161'}

    def __init__(self, code=None):
        KorailError.__init__(self, "Sold out", code)


# noinspection PyUnresolvedReferences,PyRedeclaration
class Korail(object):
    """Korail object"""
    _session = requests.session()

    _device = 'AD'
    _version = '150718001'
    _key = 'korail01234567890'

    membership_number = None
    name = None
    email = None

    def __init__(self, korail_id, korail_pw, auto_login=True, want_feedback=False):
        self.korail_id = korail_id
        self.korail_pw = korail_pw
        self.want_feedback = want_feedback
        self.logined = False
        if auto_login:
            self.login(korail_id, korail_pw)

    def login(self, korail_id=None, korail_pw=None):
        """Login to Korail server.
:param korail_id : `Korail membership number` or `phone number` or `email`
    membership   : xxxxxxxx (8 digits)
    phone number : xxx-xxxx-xxxx
    email        : xxx@xxx.xxx
:param korail_pw : Korail account korail_pw
:param auto_login=True :

First, you need to create a Korail object.

    >>> from korail2 import *
    >>> korail = Korail("12345678", YOUR_PASSWORD) # with membership number
    >>> korail = Korail("carpedm20@gmail.com", YOUR_PASSWORD) # with email
    >>> korail = Korail("010-9964-xxxx", YOUR_PASSWORD) # with phone number

If you do not want login automatically,

    >>> korail = Korail("12345678", YOUR_PASSWORD, auto_login=False)
    >>> korail.login()
    True

When you want change ID using existing object,

    >>> korail.login(ANOTHER_ID, ANOTHER_PASSWORD)
    True

"""
        if korail_id is None:
            korail_id = self.korail_id
        else:
            self.korail_id = korail_id

        if korail_pw is None:
            korail_pw = self.korail_pw
        else:
            self.korail_pw = korail_pw

        if EMAIL_REGEX.match(korail_id):
            txt_input_flg = '5'
        elif PHONE_NUMBER_REGEX.match(korail_id):
            txt_input_flg = '4'
        else:
            txt_input_flg = '2'

        url = KORAIL_LOGIN
        data = {
            'Device': self._device,
            'Version': self._version,
            # 2 : for membership number,
            # 4 : for phone number,
            # 5 : for email,
            'txtInputFlg': txt_input_flg,
            'txtMemberNo': korail_id,
            'txtPwd': korail_pw
        }

        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if j['strResult'] == 'SUCC':
            self._key = j['Key']

            self.membership_number = j['strMbCrdNo']
            self.name = j['strCustNm']
            self.email = j['strEmailAdr']
            self.logined = True
            return True
        else:
            self.logined = False
            return False

    def logout(self):
        """Logout from Korail server"""
        url = KORAIL_LOGOUT
        self._session.get(url)
        self.logined = False

    def _result_check(self, j):
        """Result data check"""
        if self.want_feedback:
            print j['h_msg_txt']

        if j['strResult'] == 'FAIL':
            h_msg_cd = _get_utf8(j, 'h_msg_cd')
            h_msg_txt = _get_utf8(j, 'h_msg_txt')
            # P058 : 로그인 필요
            matched_error = filter(lambda x: h_msg_cd in x, (NoResultsError, NeedToLoginError, SoldOutError))
            if matched_error:
                raise matched_error[0](h_msg_cd)
            else:
                raise KorailError(h_msg_txt, h_msg_cd)
        else:
            return True

    def search_train_allday(self, dep, arr, date=None, time=None, train_type=TrainType.ALL,
                            passengers=None, include_no_seats=False):
        """Search all trains for specific time and date."""
        min1 = timedelta(minutes=1)
        all_trains = []
        last_time = time
        for i in range(15):  # 최대 15번 호출
            try:
                trains = self.search_train(dep, arr, date, last_time, train_type, passengers, True)
                all_trains.extend(trains)
                # 마지막 열차시간에 1분 더해서 계속 검색.
                t = datetime.strptime(all_trains[-1].dep_time, "%H%M%S") + min1
                last_time = t.strftime("%H%M%S")
            except NoResultsError:
                break

        if not include_no_seats:
            all_trains = filter(lambda x: x.has_seat(), all_trains)

        if len(all_trains) == 0:
            raise NoResultsError()

        return all_trains

    def search_train(self, dep, arr, date=None, time=None, train_type=TrainType.ALL,
                     passengers=None, include_no_seats=False):
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
:param passengers=None: (optional) List of Passenger Objects. None means 1 AdultPassenger.
:param include_no_seats=False: (optional) When True, a result includes trains which has no seats.

Below is a sample usage of `search_train`:

    >>> dep = '서울'
    >>> arr = '동대구'
    >>> date = '20140815'
    >>> time = '144000'
    >>> trains = korail.search_train(dep, arr, date, time)
    [[KTX] 8월 3일, 서울~부산(11:00~13:42) 특실,일반실 예약가능,
     [ITX-새마을] 8월 3일, 서울~부산(11:04~16:00) 일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:00~14:43) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:30~15:13) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:40~15:45) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:55~15:26) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(13:00~15:37) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(13:10~15:58) 특실,일반실 예약가능]

When you want to see trains which has no seats.

    >>> trains = korail.search_train(dep, arr, date, time, include_no_seats=True)
    [[KTX] 8월 3일, 서울~부산(11:00~13:42) 특실,일반실 예약가능,
     [ITX-새마을] 8월 3일, 서울~부산(11:04~16:00) 일반실 예약가능,
     [무궁화호] 8월 3일, 서울~부산(11:08~16:54) 입석 역발매중,
     [ITX-새마을] 8월 3일, 서울~부산(11:50~16:50) 입석 역발매중,
     [KTX] 8월 3일, 서울~부산(12:00~14:43) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:30~15:13) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:40~15:45) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(12:55~15:26) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(13:00~15:37) 특실,일반실 예약가능,
     [KTX] 8월 3일, 서울~부산(13:10~15:58) 특실,일반실 예약가능]

`passengers` is a list(or tuple) of Passeger Objects.
By this, you can search for multiple passengers.
There are 3 types of Passengers now, AdultPassenger, ChildPassenger and SeniorPassenger.

    # for 1 adult, 1 child
    >>> psgrs = [AdultPassenger(), ChildPassenger()]

    # for 2 adults, 1 child
    >>> psgrs = [AdultPassenger(2), ChildPassenger(1)]
    # ditto. They are being added each other by same group.
    >>> psgrs = [AdultPassenger(), AdultPassenger(), ChildPassenger()]

    # for 2 adults, 1 child, 1 senior
    >>> psgrs = [AdultPassenger(2), ChildPassenger(), SeniorPassenger()]

    # for 1 adult, It supports negative count or zero count.
    # But it uses passengers which the sum is greater than zero.
    >>> psgrs = [AdultPassenger(2), AdultPassenger(-1)]
    >>> psgrs = [AdultPassenger(), SeniorPassenger(0)]

    # Nothing
    >>> psgrs = [AdultPassenger(0), SeniorPassenger(0)]

    # then search or reserve train
    >>> trains = korail.search_train(dep, arr, date, time, passengers=psgrs)
    ...
    >>> korail.reserve(trains[0], psgrs)
    ...

"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        if time is None:
            time = datetime.now().strftime("%H%M%S")

        if passengers is None:
            passengers = [AdultPassenger()]

        passengers = Passenger.reduce(passengers)

        adult_count = reduce(lambda a, b: a + b.count, filter(lambda x: isinstance(x, AdultPassenger), passengers), 0)
        child_count = reduce(lambda a, b: a + b.count, filter(lambda x: isinstance(x, ChildPassenger), passengers), 0)
        senior_count = reduce(lambda a, b: a + b.count, filter(lambda x: isinstance(x, SeniorPassenger), passengers), 0)

        url = KORAIL_SEARCH_SCHEDULE
        data = {
            'Device': self._device,
            'radJobId': '1',
            'selGoTrain': train_type,
            'txtCardPsgCnt': '0',
            'txtGdNo': '',
            'txtGoAbrdDt': date,  # '20140803',
            'txtGoEnd': arr,
            'txtGoHour': time,  # '071500',
            'txtGoStart': dep,
            'txtJobDv': '',
            'txtMenuId': '11',
            'txtPsgFlg_1': adult_count,  # 어른
            'txtPsgFlg_2': child_count,  # 어린이
            'txtPsgFlg_3': senior_count,  # 경로
            'txtPsgFlg_4': '0',  # 장애인1
            'txtPsgFlg_5': '0',  # 장애인2
            'txtSeatAttCd_2': '000',
            'txtSeatAttCd_3': '000',
            'txtSeatAttCd_4': '015',
            'txtTrnGpCd': train_type,

            'Version': self._version,
        }


        r = self._session.get(url, params=data)
        j = json.loads(r.text)

        if self._result_check(j):
            train_infos = j['trn_infos']['trn_info']

            trains = []

            for info in train_infos:
                trains.append(Train(info))

            if not include_no_seats:
                trains = filter(lambda x: x.has_seat(), trains)

            if len(trains) == 0:
                raise NoResultsError()

            return trains

    def reserve(self, train, passengers=None, option=ReserveOption.GENERAL_FIRST):
        """Reserve a train.

:param train: An instance of `Train`.
:param passengers=None: (optional) List of Passenger Objects. None means 1 AdultPassenger.
:param option=ReserveOption.GENERAL_FIRST : (optional)

When tickets are not enough much for passengers, it raises SoldOutError.

If you want to select priority of seat grade, general or special,
There are 4 options in ReserveOption class.

- GENERAL_FIRST : Economic than Comfortable.
- GENERAL_ONLY  : Reserve only general seats. You are poorman ;-)
- SPECIAL_FIRST : Comfortable than Economic.
- SPECIAL_ONLY  : Richman.

        """

        # 좌석 선택 옵션에 따라 결정.
        seat_type = None
        if train.has_seat() is False:  # 자리가 둘다 없는 경우는 SoldOutError발생
            raise SoldOutError()
        elif option == ReserveOption.GENERAL_ONLY:  # 이후 일반석, 특실 중 하나는 무조건 있는 조건
            if train.has_general_seat():
                seat_type = '1'
            else:
                raise SoldOutError()
        elif option == ReserveOption.SPECIAL_ONLY:
            if train.has_special_seat():
                seat_type = '2'
            else:
                raise SoldOutError()
        elif option == ReserveOption.GENERAL_FIRST:
            if train.has_general_seat():
                seat_type = '1'
            else:
                seat_type = '2'
        elif option == ReserveOption.SPECIAL_FIRST:
            if train.has_special_seat():
                seat_type = '2'
            else:
                seat_type = '1'

        if passengers is None:
            passengers = [AdultPassenger()]

        print train

        passengers = Passenger.reduce(passengers)
        cnt = reduce(lambda x,y: x + y.count, passengers, 0)
        url = KORAIL_TICKETRESERVATION
        data = {
            'Device': self._device,
            'Version': self._version,
            'Key': self._key,
            'txtGdNo': '',
            'txtJobId': '1101',
            'txtTotPsgCnt': cnt,
            'txtSeatAttCd1': '000',
            'txtSeatAttCd2': '000',
            'txtSeatAttCd3': '000',
            'txtSeatAttCd4': '015',
            'txtSeatAttCd5': '000',
            'hidFreeFlg': 'N',
            'txtStndFlg': 'N',
            'txtMenuId': '11',
            'txtSrcarCnt': '0',
            'txtJrnyCnt': '1',

            # 이하 여정정보1
            'txtJrnySqno1': '001',
            'txtJrnyTpCd1': '11',
            'txtDptDt1': train.dep_date,
            'txtDptRsStnCd1': train.dep_code,
            'txtDptTm1': train.dep_time,
            'txtArvRsStnCd1': train.arr_code,
            'txtTrnNo1': train.train_no,
            'txtRunDt1': train.run_date,
            'txtTrnClsfCd1': train.train_type,
            'txtPsrmClCd1': seat_type,
            'txtTrnGpCd1': train.train_group,
            'txtChgFlg1': '',

            # 이하 여정정보2
            'txtJrnySqno2': '',
            'txtJrnyTpCd2': '',
            'txtDptDt2': '',
            'txtDptRsStnCd2': '',
            'txtDptTm2': '',
            'txtArvRsStnCd2': '',
            'txtTrnNo2': '',
            'txtRunDt2': '',
            'txtTrnClsfCd2': '',
            'txtPsrmClCd2': '',
            'txtChgFlg2': '',

            # 이하 txtTotPsgCnt 만큼 반복
            # 'txtPsgTpCd1'    : '1',   #손님 종류 (어른, 어린이)
            # 'txtDiscKndCd1'  : '000', #할인 타입 (경로, 동반유아, 군장병 등..)
            # 'txtCompaCnt1'   : '1',   #인원수
            # 'txtCardCode_1'  : '',
            # 'txtCardNo_1'    : '',
            # 'txtCardPw_1'    : '',
        }

        index = 1
        for psg in passengers:
            data.update(psg.get_dict(index))
            index += 1

        r = self._session.get(url, params=data)
        j = json.loads(r.text)
        if self._result_check(j):
            rsv_id = j['h_pnr_no']
            rsvlist = filter(lambda x: x.rsv_id == rsv_id, self.reservations())
            if len(rsvlist) == 1:
                return rsvlist[0]

    def tickets(self):
        """Get list of tickets"""
        url = KORAIL_MYTICKETLIST
        data = {
            'Device': self._device,
            'Version': self._version,
            'Key': self._key,
            'txtIndex': '1',
            'h_page_no': '1',
            'txtDeviceId': '',
            'h_abrd_dt_from': '',
            'h_abrd_dt_to': '',
        }

        r = self._session.get(url, params=data)
        j = json.loads(r.text)

        if self._result_check(j):
            ticket_infos = j['tk_infos']['tk_info']

            tickets = []

            for info in ticket_infos:
                ticket = Ticket(info)
                url = KORAIL_MYTICKET_SEAT
                data = {
                    'Device': self._device,
                    'Version': self._version,
                    'Key': self._key,
                    'h_orgtk_wct_no': ticket.sale_info1,
                    'h_orgtk_ret_sale_dt': ticket.sale_info2,
                    'h_orgtk_sale_sqno': ticket.sale_info3,
                    'h_orgtk_ret_pwd': ticket.sale_info4,
                }
                r = self._session.get(url, params=data)
                j = json.loads(r.text)
                if self._result_check(j):
                    seat = j['seat_infos']['seat_info'][0]
                    ticket.seat_no = _get_utf8(seat, 'h_seat_no')
                    ticket.seat_no_end = None

                tickets.append(ticket)

            return tickets

    def reservations(self):
        """ Get My Reservations """
        url = KORAIL_MYRESERVATIONLIST
        data = {
            'Device': self._device,
            'Version': self._version,
            'Key': self._key,
        }
        r = self._session.get(url, params=data)
        j = json.loads(r.text)
        try:
            if self._result_check(j):
                rsv_infos = j['jrny_infos']['jrny_info']

                reserves = []

                for info in rsv_infos:
                    for tinfo in info['train_infos']['train_info']:
                        reserves.append(Reservation(tinfo))
                return reserves
        except NoResultsError:
            return []

    def cancel(self, rsv):
        """ Cancel Reservation : Canceling is for reservation, for ticket would be Refunding """
        assert isinstance(rsv, Reservation)
        url = KORAIL_CANCEL
        data = {
            'Device': self._device,
            'Version': self._version,
            'Key': self._key,
            'txtPnrNo': rsv.rsv_id,
            'txtJrnySqno': rsv.journey_no,
            'txtJrnyCnt': rsv.journey_cnt,
            'hidRsvChgNo': rsv.rsv_chg_no,
        }
        r = self._session.get(url, data=data)
        j = json.loads(r.text)
        if self._result_check(j):
            return True
