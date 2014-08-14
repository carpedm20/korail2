# -*- coding:utf-8 -*-
from unittest import TestCase
import os.path
from datetime import date, datetime, timedelta
from korail2 import Korail

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
            self.assertTrue(self.korail.logined,"로그인 성공 체크")
        except Exception, e:
            self.fail(e)

    def test_logout(self):
        try:
            self.korail.logout()
            self.assertFalse(self.korail.logined,"로그아웃 성공 체크")
        except Exception, e:
            self.fail(e)

    def test__result_check(self):
        self.skipTest("Not implemented")

    def test_search_train(self):
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")
        self.assertGreaterEqual(len(trains), 0, "tomorrow train search")

    def test_reserve(self):
        self.skipTest("Not implemented")

    def test_tickets(self):
        self.skipTest("Not implemented")

    def test_reservations(self):
        reserves = self.korail.reservations()
        self.assertIsNotNone(reserves, "success")
        print reserves

    def test_cancel(self):
        # self.skipTest("Not implemented")
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")
        for train in trains:
            print train
        empty_seats = filter(lambda x:"11" in (x.special_seat, x.general_seat), trains)
        if len(empty_seats) > 0:
            self.korail.reserve(empty_seats[0])
        else:
            self.skipTest("No Empty Seats tomorrow.")