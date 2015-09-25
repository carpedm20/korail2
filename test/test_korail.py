# -*- coding:utf-8 -*-
from unittest import TestCase
import os.path
from datetime import datetime, time, date, timedelta
from korail2 import *
import sys

import logging
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

__author__ = 'sng2c'


class TestKorail(TestCase):

    def thetime(self):
        return date.today() + timedelta(days=30)

    def setUp(self):

        if not (hasattr(self, "koid") and hasattr(self, "kopw")):
            filepath = "korail_idpw.txt"
            if os.path.exists(filepath):
                with open(filepath) as idpw:
                    self.koid = idpw.readline().strip()
                    self.kopw = idpw.readline().strip()
                self.korail = Korail(self.koid, self.kopw, auto_login=False)
            else:
                raise Exception("No file at %s" % filepath)

        if not self.korail.logined:
            if not self.korail.login():
                raise Exception("Invalid id/pw %s %s" % (self.koid, self.kopw))

    def test_login(self):
        try:
            self.korail.login()
            self.assertTrue(self.korail.logined, "로그인 성공 체크")
        except Exception:
            self.fail(sys.exc_info()[1])

    def test_logout(self):
        try:
            self.korail.logout()
            self.assertFalse(self.korail.logined, "로그아웃 성공 체크")
        except Exception:
            self.fail(sys.exc_info()[1])

    def test_passenger_reduce(self):
        try:
            Passenger()
        except NotImplementedError:
            self.assertTrue(True)
        else:
            self.fail("NotImplementedError must be raised")

        try:
            Passenger.reduce([AdultPassenger, "aaaa"])
        except TypeError:
            self.assertTrue(True)
        else:
            self.fail("TypeError must be raised")

        reduced = Passenger.reduce(
            [AdultPassenger(), AdultPassenger(), AdultPassenger(count=-1), ChildPassenger(count=0),
             SeniorPassenger(count=-1)])
        self.assertEqual(len(reduced), 1)
        for psgr in reduced:
            if isinstance(psgr, AdultPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, ChildPassenger):
                self.fail("ChildPassenger must not appear")
            if isinstance(psgr, SeniorPassenger):
                self.fail("SeniorPassenger must not appear")

        reduced = Passenger.reduce([AdultPassenger(), ChildPassenger(), SeniorPassenger()])
        self.assertEqual(len(reduced), 3)
        for psgr in reduced:
            if isinstance(psgr, AdultPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, ChildPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, SeniorPassenger):
                self.assertEqual(psgr.count, 1)

        reduced = Passenger.reduce(
            [AdultPassenger(), AdultPassenger(), ChildPassenger(), SeniorPassenger(), SeniorPassenger()])
        self.assertEqual(len(reduced), 3)
        for psgr in reduced:
            if isinstance(psgr, AdultPassenger):
                self.assertEqual(psgr.count, 2)
            if isinstance(psgr, ChildPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, SeniorPassenger):
                self.assertEqual(psgr.count, 2)


    def test__result_check(self):
        try:
            self.korail._result_check({})
        except KorailError, e:
            self.assertTrue(False)
        except Exception, e:
            self.assertTrue(True)

        try:
            self.korail._result_check({"strResult": "SUCC", "h_msg_cd": "P000", "h_msg_txt": "UNKNOWN"})
        except Exception, e:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P000", "h_msg_txt": "UNKNOWN"})
        except KorailError:
            self.assertTrue(True)
        except Exception, e:
            self.assertTrue(False)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P100", "h_msg_txt": "UNKNOWN"})
        except NoResultsError:
            self.assertTrue(True)
        except KorailError:
            self.assertTrue(False)
        except Exception, e:
            self.assertTrue(False)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P058", "h_msg_txt": "UNKNOWN"})
        except NeedToLoginError:
            self.assertTrue(True)
        except KorailError:
            self.assertTrue(False)
        except Exception, e:
            self.assertTrue(False)

    def test_search_train(self):
        trains = self.korail.search_train("서울", "부산", self.thetime().strftime("%Y%m%d"), "100000")
        self.assertGreaterEqual(len(trains), 0, "tomorrow train search")
        print trains

        alltrains = self.korail.search_train_allday("서울", "부산", self.thetime().strftime("%Y%m%d"), "100000")
        self.assertGreaterEqual(len(alltrains), len(trains), "tomorrow train search")
        print alltrains

    # def test_reserve(self):
    # self.skipTest("Same to test_cancel")

    def test_tickets(self):
        try:
            tickets = self.korail.tickets()
        except KorailError:
            self.skipTest("Sold out")
        self.assertIsInstance(tickets, list)

    def test_reservations(self):
        self.assertIn("P100", NoResultsError)

        try:
            reserves = self.korail.reservations()
            self.assertIsNotNone(reserves, "get reservation list")
            self.assertIsInstance(reserves, list)

            # print reserves
        except Exception, e:
            self.fail(e.message)
            # self.skipTest(e.message)

    def test_reserve_and_cancel(self):
        # self.skipTest("Not implemented")


        trains = self.korail.search_train("서울", "부산", self.thetime().strftime("%Y%m%d"), self.thetime().strftime("%H%M%S"))

        empty_seats = filter(lambda x: "11" in (x.special_seat, x.general_seat), trains)
        if len(empty_seats) > 0:
            try:
                rsv = self.korail.reserve(empty_seats[0])
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 1, "make a reservation")

                self.korail.cancel(rsv)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 0, "cancel the reservation")
            except SoldOutError:
                self.skipTest("Sold Out")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_reserve_and_cancel2(self):
        # self.skipTest("Not implemented")

        try:
            trains = self.korail.search_train("서울", "부산", self.thetime().strftime("%Y%m%d"), "100000")
        except NoResultsError:
            self.skipTest("Sold out")

        empty_seats = filter(lambda x: x.has_special_seat(), trains)
        if len(empty_seats) > 0:
            try:
                rsv = self.korail.reserve(empty_seats[0], option=ReserveOption.SPECIAL_ONLY)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 1, "make a reservation")

                self.korail.cancel(rsv)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 0, "cancel the reservation")
            except SoldOutError:
                self.skipTest("Sold Out")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_reserve_and_cancel_multi(self):
        # self.skipTest("Not implemented")

        passengers = (
            AdultPassenger(1),
            ChildPassenger(1),
            SeniorPassenger(1),
        )
        try:
            trains = self.korail.search_train("서울", "부산", self.thetime().strftime("%Y%m%d"), "100000", passengers=passengers)
        except NoResultsError:
            self.skipTest("Sold out")

        print trains
        empty_seats = filter(lambda x: "11" in (x.special_seat, x.general_seat), trains)
        if len(empty_seats) > 0:
            try:
                rsv = self.korail.reserve(empty_seats[0], passengers=passengers)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 1, "make a reservation")

                self.korail.cancel(rsv)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 0, "cancel the reservation")
            except SoldOutError:
                self.skipTest("Sold Out")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_cancel_all(self):
        for rsv in self.korail.reservations():
            res = self.korail.cancel(rsv)
            print(repr(rsv) + "\n" + str(res))

        self.assertFalse(self.korail.reservations())
