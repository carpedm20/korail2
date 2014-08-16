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

KORAIL_LOGIN             = "%s.login.Login" % KORAIL_MOBILE
KORAIL_LOGOUT            = "%s.common.logout" % KORAIL_MOBILE
KORAIL_SEARCH_SCHEDULE   = "%s.seatMovie.ScheduleView" % KORAIL_MOBILE
KORAIL_TICKETRESERVATION = "%s.certification.TicketReservation" % KORAIL_MOBILE
KORAIL_REFUND            = "%s.refunds.RefundsRequest" % KORAIL_MOBILE
KORAIL_MYTICKETLIST      = "%s.myTicket.MyTicketList" % KORAIL_MOBILE

KORAIL_MYRESERVATIONLIST = "%s.reservation.ReservationView" % KORAIL_MOBILE
KORAIL_CANCEL            = "%s.reservationCancel.ReservationCancel" % KORAIL_MOBILE

KORAIL_STATION_DB       = "%s.common.stationinfo?device=ip" % KORAIL_MOBILE
KORAIL_STATION_DB_DATA  = "%s.common.stationdata" % KORAIL_MOBILE
KORAIL_EVENT            = "%s.common.event" % KORAIL_MOBILE
KORAIL_PAYMENT          = "%s/ebizmw/PrdPkgMainList.do" % KORAIL_DOMAIN
KORAIL_PAYMENT_VOUNCHER = "%s/ebizmw/PrdPkgBoucherView.do" % KORAIL_DOMAIN


class Schedule(object):
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


    #: 출발역 이름
    dep_name = None # h_dpt_rs_stn_nm

    #: 출발역 코드
    dep_code = None # h_dpt_rs_stn_cd

    #: 출발 날짜 (yyyyMMdd)
    dep_date = None # h_dpt_dt

    #: 출발 시각 (hhmmss)
    dep_time = None # h_dpt_tm

    #: 도착역 이름
    arr_name = None # h_arv_rs_stn_nm

    #: 도착역 코드
    arr_code = None # h_arv_rs_stn_cd

    #: 도착 날짜 (yyyyMMdd)
    dep_date = None # h_arv_dt

    #: 도착 시각 (hhmmss)
    arr_time = None # h_arv_tm

    #: ???? 시각 (yyyyMMdd)
    run_date = None # h_run_dt

    def __repr__(self):
        dep_time = "%s:%s" % (self.dep_time[:2], self.dep_time[2:4])
        arr_time = "%s:%s" % (self.arr_time[:2], self.arr_time[2:4])

        dep_date = "%s월 %s일" % (int(self.dep_date[4:6]),
                                  int(self.dep_date[6:]))

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
    #: 지연 시간 (hhmm)
    delay_time = None # h_expct_dlay_hr

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
        repr_str = super(Train, self).__repr__() + " "

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


class Ticket(Train):
    """Ticket object"""

    #: 열차 번호
    car_no = None # h_srcar_no

    #: 자리 갯수
    seat_no_count = None # h_seat_cnt  ex) 001

    #: 자리 번호
    seat_no = None # h_seat_no

    #: 자리 번호
    seat_no_end = None # h_seat_no_end

    #: 구매자 성함
    buyer_name = None # h_buy_ps_nm

    #: 구매 날짜 (yyyyMMdd)
    sale_date = None # h_orgtk_sale_dt

    #: 구매 정보1
    sale_info1 = None # h_orgtk_wct_no

    #: 구매 정보2
    sale_info2 = None # h_orgtk_ret_sale_dt

    #: 구매 정보3
    sale_info3 = None # h_orgtk_sale_sqno

    #: 구매 정보4
    sale_info4 = None # h_orgtk_ret_pwd

    #: 구매 가격
    price = None # h_rcvd_amt  ex) 00013900

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
        return "%s-%s-%s-%s" % (self.sale_info1,
                                self.sale_info2,
                                self.sale_info3,
                                self.sale_info4)


class Reservation(Train):
    """Revervation object"""

    #: 예약번호
    rsv_id = None # h_pnr_no

    #: 여정 번호
    journey_no = None

    #: 여정 카운트
    journey_cnt = None

    #: 예약변경 번호?
    rsv_chg_no = None

    #: 자리 갯수
    seat_no_count = None # h_tot_seat_cnt  ex) 001

    #: 결제 기한 날짜
    buy_limit_date = None # h_ntisu_lmt_dt

    #: 결제 기한 시간
    buy_limit_time = None # h_ntisu_lmt_tm

    #: 예약 가격
    price = None # h_rsv_amt  ex) 00013900

    def __repr__(self):
        repr_str = super(Train, self).__repr__()

        repr_str += ", %s원" % self.price

        buy_limit_time = "%s:%s" % (self.buy_limit_time[:2], self.buy_limit_time[2:4])

        buy_limit_date = "%s월 %s일" % (int(self.buy_limit_date[4:6]),
                                  int(self.buy_limit_date[6:]))

        repr_str += ", 구입기한 %s %s" % (buy_limit_date, buy_limit_time)

        return repr_str

class Seat(Schedule):
    """Ticket object"""
    #: Schedule
    schedule = None

    #: 열차 번호
    car_no = None # h_srcar_no

    #: 자리 번호
    seat_no = None # h_seat_no

    #: 자리 갯수
    seat_no_count = None # h_seat_cnt  ex) 001

    def __repr__(self):
        repr_str = self.schedule.__repr__()
        repr_str += " %s호 %s" % (self.car_no, self.seat_no)

        return repr_str

    def get_ticket_no(self):
        return "%s-%s-%s-%s" % (self.sale_info1,
                                self.sale_info2,
                                self.sale_info3,
                                self.sale_info4)


class Korail(object):
    """Korail object"""
    _session = requests.session()

    _device  = 'AD'
    _version = '140801001'
    _key     = 'korail01234567890'

    membership_number = None
    name = None
    email = None

    def __init__(self, id, password, auto_login=True, want_feedback=False):
        self.id = id
        self.password = password
        self.want_feedback = want_feedback
        self.logined = False
        if auto_login:
            self.login(id, password)

    def login(self, id=None, password=None):
        """Login to Korail server.
:param id: `Korail membership number` or `phone number` or `email`
    membership   : xxxxxxxx (8 digits)
    phone number : xxx-xxxx-xxxx
    email        : xxx@xxx.xxx
:param password: Korail account password

First, you need to create a Korail object.

    >>> from korail2 import Korail
    >>> korail = Korail("12345678", YOUR_PASSWORD) # with membership number
    >>> korail = Korail("carpedm20@gmail.com", YOUR_PASSWORD) # with email
    >>> korail = Korail("010-9964-xxxx", YOUR_PASSWORD) # with phone number
        """
        if id is None:
            id = self.id
        else:
            self.id = id

        if password is None:
            password = self.password
        else:
            self.password = password

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
            h_msg_cd  = j['h_msg_cd'].encode('utf-8')
            h_msg_txt = j['h_msg_txt'].encode('utf-8')
            # P058 : 로그인 필요
            raise Exception("%s (%s)" % (h_msg_txt, h_msg_cd))
        else:
            return True

    def search_train(self, dep, arr, date=None, time=None, train_type='05',
                     adult=1):
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

Below is a sample code of `search_train`:

    >>> dep = '서울'
    >>> arr = '동대구'
    >>> date = '20140815'
    >>> time = '144000'
    >>> trains = korail.search_train(dep, arr, date, time)
    [[KTX] 8월 3일, 서울~부산(11:00~13:42) [특실:1][일반실:1] 예약가능,
     [ITX-새마을] 8월 3일, 서울~부산(11:04~16:00) [일반실:1] 예약가능,
     [무궁화호] 8월 3일, 서울~부산(11:08~16:54) [일반실:0] 입석 역발매중,
     [ITX-새마을] 8월 3일, 서울~부산(11:50~16:50) [일반실:0] 입석 역발매중,
     [KTX] 8월 3일, 서울~부산(12:00~14:43) [특실:1][일반실:1] 예약가능,
     [KTX] 8월 3일, 서울~부산(12:30~15:13) [특실:1][일반실:1] 예약가능,
     [KTX] 8월 3일, 서울~부산(12:40~15:45) [특실:1][일반실:1] 예약가능,
     [KTX] 8월 3일, 서울~부산(12:55~15:26) [특실:1][일반실:1] 예약가능,
     [KTX] 8월 3일, 서울~부산(13:00~15:37) [특실:1][일반실:1] 예약가능,
     [KTX] 8월 3일, 서울~부산(13:10~15:58) [특실:1][일반실:1] 예약가능]
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
            'txtPsgFlg_1'    : str(adult),  #일반인
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

        if self._result_check(j):
            train_infos = j['trn_infos']['trn_info']

            trains = []

            for info in train_infos:
                for i in info:
                    try: info[i] = info[i].encode('utf-8')
                    except: pass

                train = Train()
                train.train_type      = info['h_trn_clsf_cd']
                train.train_type_name = info['h_trn_clsf_nm']
                train.train_no        = info['h_trn_no']
                train.delay_time      = info['h_expct_dlay_hr']

                train.dep_name = info['h_dpt_rs_stn_nm']
                train.dep_code = info['h_dpt_rs_stn_cd']
                train.dep_date = info['h_dpt_dt']
                train.dep_time = info['h_dpt_tm']

                train.arr_name = info['h_arv_rs_stn_nm']
                train.arr_code = info['h_arv_rs_stn_cd']
                train.arr_date = info['h_arv_dt']
                train.arr_time = info['h_arv_tm']

                train.run_date = info['h_run_dt']

                train.reserve_possible      = info['h_rsv_psb_flg']
                train.reserve_possible_name = info['h_rsv_psb_nm']

                train.special_seat = info['h_spe_rsv_cd']
                train.general_seat = info['h_gen_rsv_cd']

                trains.append(train)

            return trains

    def reserve(self, train):
        """Reserve a train.

:param train: An instance of `Train`.

You can get your tickes with `tickets` method.

    >>> trains = korail.search_train(dep, arr, date, time)
    >>> seat = korail.reserve(trains[0])
    정상처리되었습니다
    동일시간대 예약발매내역이 있습니다.
    >>> seat
    [KTX] 8월 3일, 서울~부산(11:00~:) 16호 6A
        """
        # train : 예약을 위한 차량의 필수 정보를 가진 모든 객체를 이용할 수 있어야 한다.

        url = KORAIL_TICKETRESERVATION
        data = {
            'Device'         : self._device,
            'Version'        : self._version,
            'Key'            : self._key,
            'txtGdNo'        : '',
            'txtTotPsgCnt'   : '',
            'txtSeatAttCd1'  : '00',
            'txtSeatAttCd2'  : '00',
            'txtSeatAttCd3'  : '00',
            'txtSeatAttCd4'  : '15',
            'txtSeatAttCd5'  : '00',
            'hidFreeFlg'     : '',
            'txtStndFlg'     : '',
            'txtMenuId'      : '11',
            'txtSrcarCnt'    : '0',
            'txtJrnyCnt'     : '1',
            'txtPsgTpCd1'    : '1',
            'txtDiscKndCd1'  : '000',
            'txtCompaCnt1'   : '1',
            'txtCardCode_1'  : '',
            'txtCardNo_1'    : '',
            'txtCardPw_1'    : '',
            'txtJrnySqno1'   : '001',
            'txtJrnyTpCd1'   : '11',
            'txtDptDt1'      : train.dep_date,
            'txtDptRsStnCd1' : train.dep_code,
            'txtDptTm1'      : train.dep_time,
            'txtArvRsStnCd1' : train.arr_code,
            'txtTrnNo1'      : train.train_no,
            'txtRunDt1'      : train.run_date,
            'txtTrnClsfCd1'  : train.train_type,
            'txtPsrmClCd1'   : '1',
            'txtChgFlg1'     : '',
            'txtJrnySqno2'   : '',
            'txtJrnyTpCd2'   : '',
            'txtDptDt2'      : '',
            'txtDptRsStnCd2' : '',
            'txtDptTm2'      : '',
            'txtArvRsStnCd2' : '',
            'txtTrnNo2'      : '',
            'txtRunDt2'      : '',
            'txtTrnClsfCd2'  : '',
            'txtPsrmClCd2'   : '',
            'txtChgFlg2'     : '',
        }

        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if self._result_check(j):
            journey_infos = j['jrny_infos']['jrny_info']

            seats = []

            for info in journey_infos:
                for i in info:
                    try: info[i] = info[i].encode('utf-8')
                    except: pass

                # Seat 상속을 이용할 것
                schedule = Schedule()

                schedule.train_type      = info['h_trn_clsf_cd']
                schedule.train_type_name = info['h_trn_clsf_nm']
                schedule.train_no        = info['h_trn_no']

                schedule.dep_name = info['h_dpt_rs_stn_nm']
                schedule.dep_code = info['h_dpt_rs_stn_cd']
                schedule.dep_date = info['h_dpt_dt']
                schedule.dep_time = info['h_dpt_tm']

                schedule.arr_name = info['h_arv_rs_stn_nm']
                schedule.arr_code = info['h_arv_rs_stn_cd']
                schedule.arr_date = ''
                schedule.arr_time = ''

                seat_infos = info['seat_infos']['seat_info']

                for s_info in seat_infos:
                    for i in s_info:
                        try: s_info[i] = s_info[i].encode('utf-8')
                        except: pass
                    seat = Seat()

                    seat.schedule      = schedule
                    seat.car_no        = s_info['h_srcar_no']
                    seat.seat_no       = s_info['h_seat_no']
                    seat.seat_no_count = s_info['h_cont_seat_cnt']

                    seats.append(seat)

            return seats[0]
    
    def tickets(self):
        """Get list of tickets

You can see your ticket list with `tickets` method.
You can get the list of paid tickes with `tickets` method.

    >>> tickets = korail.tickets()
    정상발매처리,정상발권처리
    >>> print tickets
    [[KTX] 8월 10일, 동대구~울산(09:26~09:54) => 5호 4A, 13900원]

"""
        url = KORAIL_MYTICKETLIST
        data = {
            'Device'         : self._device,
            'Version'        : self._version,
            'Key'            : self._key,
            'txtIndex'       : '1',
            'h_page_no'      : '1',
            'txtDeviceId'    : '',
            'h_abrd_dt_from' : '',
            'h_abrd_dt_to'   : '',
        }

        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if self._result_check(j):
            ticket_infos = j['tk_infos']['tk_info']

            tickets = []

            for info in ticket_infos:
                for i in info:
                    try: info[i] = info[i].encode('utf-8')
                    except: pass

                ticket = Ticket()
                ticket.train_type      = info['h_trn_clsf_cd']
                ticket.train_type_name = info['h_trn_clsf_nm']
                ticket.train_no        = info['h_trn_no']

                ticket.dep_name = info['h_dpt_rs_stn_nm']
                ticket.dep_code = info['h_dpt_rs_stn_cd']
                ticket.dep_date = info['h_dpt_dt']
                ticket.dep_time = info['h_dpt_tm']

                ticket.arr_name = info['h_arv_rs_stn_nm']
                ticket.arr_code = info['h_arv_rs_stn_cd']
                ticket.arr_date = info['h_arv_dt']
                ticket.arr_time = info['h_arv_tm']

                ticket.car_no        = info['h_srcar_no']
                ticket.seat_no       = info['h_seat_no']
                ticket.seat_no_end   = info['h_seat_no_end']
                ticket.seat_no_count = int(info['h_seat_cnt'])

                ticket.buyer_name = info['h_buy_ps_nm']
                ticket.sale_date  = info['h_orgtk_sale_dt']
                ticket.sale_info1 = info['h_orgtk_wct_no']
                ticket.sale_info2 = info['h_orgtk_ret_sale_dt']
                ticket.sale_info3 = info['h_orgtk_sale_sqno']
                ticket.sale_info4 = info['h_orgtk_ret_pwd']
                ticket.price      = int(info['h_rcvd_amt'])

                tickets.append(ticket)

            return tickets

    def reservations(self):
        """ Get My Reservations """
        url = KORAIL_MYRESERVATIONLIST
        data = {
            'Device'         : self._device,
            'Version'        : self._version,
            'Key'            : self._key,
        }
        r = self._session.post(url, data=data)
        j = json.loads(r.text)
        if self._result_check(j):
            rsv_infos = j['jrny_infos']['jrny_info']

            reserves = []

            for info in rsv_infos:
                for i in info:
                    try: info[i] = info[i].encode('utf-8')
                    except: pass

                rsv = Reservation()
                rsv.train_type      = info['h_trn_clsf_cd']
                rsv.train_type_name = info['h_trn_clsf_nm']
                rsv.train_no        = info['h_trn_no']

                rsv.dep_name = info['h_dpt_rs_stn_nm']
                rsv.dep_code = info['h_dpt_rs_stn_cd']
                rsv.dep_date = info['h_run_dt']
                rsv.dep_time = info['h_dpt_tm']

                rsv.arr_name = info['h_arv_rs_stn_nm']
                rsv.arr_code = info['h_arv_rs_stn_cd']
                rsv.arr_date = info['h_run_dt']
                rsv.arr_time = info['h_arv_tm']

                rsv.rsv_id         = info['h_pnr_no']
                rsv.seat_no_count  = int(info['h_tot_seat_cnt'])
                rsv.buy_limit_date = info['h_ntisu_lmt_dt']
                rsv.buy_limit_time = info['h_ntisu_lmt_tm']
                rsv.price          = int(info['h_rsv_amt'])

                reserves.append(rsv)

            return reserves

    def cancel(self, rsv_id):
        """ Cancel Reservation : Canceling is for reservation, for ticket would be Refunding """
        url = KORAIL_CANCEL
        pass