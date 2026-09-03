# -*- coding: utf-8 -*-
from unittest import TestCase

from korail2 import AdultPassenger, ChildPassenger, Korail, Passenger


class FakeResponse(object):
    def __init__(self, text):
        self.text = text


class RecordingSession(object):
    def __init__(self, response_text='{"strResult": "SUCC"}'):
        self.response = FakeResponse(response_text)
        self.get_calls = []
        self.post_calls = []

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self.response

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return self.response


class PassengerTests(TestCase):
    def test_reduce_combines_non_adjacent_groups(self):
        passengers = Passenger.reduce([
            AdultPassenger(2),
            ChildPassenger(),
            AdultPassenger(-1),
        ])

        self.assertEqual(
            [(type(passenger), passenger.count) for passenger in passengers],
            [(AdultPassenger, 1), (ChildPassenger, 1)],
        )

    def test_reduce_accepts_one_shot_iterables(self):
        passengers = Passenger.reduce(
            passenger for passenger in [AdultPassenger(), ChildPassenger()]
        )

        self.assertEqual(len(passengers), 2)


class KorailTests(TestCase):
    def test_each_instance_owns_its_session(self):
        first = Korail('first', 'password', auto_login=False)
        second = Korail('second', 'password', auto_login=False)

        self.assertIsNot(first._session, second._session)

    def test_reserve_rejects_invalid_option_before_request(self):
        korail = Korail('member', 'password', auto_login=False)
        session = RecordingSession()
        korail._session = session

        with self.assertRaises(ValueError):
            korail.reserve(None, option='TYPO')

        self.assertEqual(session.get_calls, [])
        self.assertEqual(session.post_calls, [])

    def test_cancel_rejects_invalid_objects(self):
        korail = Korail('member', 'password', auto_login=False)

        with self.assertRaises(TypeError):
            korail.cancel(object())
