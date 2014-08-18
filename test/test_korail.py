# -*- coding:utf-8 -*-
from unittest import TestCase
import os.path
from datetime import date, datetime, timedelta
from korail2 import *

__author__ = 'sng2c'


class TestKorail(TestCase):
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
        except Exception, e:
            self.fail(e)

    def test_logout(self):
        try:
            self.korail.logout()
            self.assertFalse(self.korail.logined, "로그아웃 성공 체크")
        except Exception, e:
            self.fail(e)

    def test__result_check(self):
        try:
            self.korail._result_check({})
        except KorailError:
            self.assertTrue(False)
        except Exception:
            self.assertTrue(True)

        try:
            self.korail._result_check({"strResult": "SUCC", "h_msg_cd": "P000", "h_msg_txt": "UNKNOWN"})
        except Exception:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P000", "h_msg_txt": "UNKNOWN"})
        except KorailError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P100", "h_msg_txt": "UNKNOWN"})
        except NoResultsError:
            self.assertTrue(True)
        except KorailError:
            self.assertTrue(False)
        except Exception:
            self.assertTrue(False)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P058", "h_msg_txt": "UNKNOWN"})
        except LoginError:
            self.assertTrue(True)
        except KorailError:
            self.assertTrue(False)
        except Exception:
            self.assertTrue(False)

    def test_search_train(self):
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")
        self.assertGreaterEqual(len(trains), 0, "tomorrow train search")

    # def test_reserve(self):
    #     self.skipTest("Same to test_cancel")

    def test_tickets(self):
        tickets = self.korail.tickets()
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
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")

        empty_seats = filter(lambda x: "11" in (x.special_seat, x.general_seat), trains)
        if len(empty_seats) > 0:
            rsv = self.korail.reserve(empty_seats[0])
            rsvlist = self.korail.reservations()
            matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
            self.assertEqual(len(matched), 1, "make a reservation")

            self.korail.cancel(rsv)
            rsvlist = self.korail.reservations()
            matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
            self.assertEqual(len(matched), 0, "cancel the reservation")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_cancel_all(self):
        for rsv in self.korail.reservations():
            res = self.korail.cancel(rsv)
            print repr(rsv) + "\n" + str(res)

        self.assertFalse(self.korail.reservations())
