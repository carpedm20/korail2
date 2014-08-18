Korail2
=======

[![PyPi version](https://pypip.in/v/korail2/badge.png)](https://pypi.python.org/pypi/korail2)
[![PyPi downloads](https://pypip.in/d/korail2/badge.png)](https://pypi.python.org/pypi/korail2)

- **2014.08.11 ANNOUNCEMENT** : *Good* news! this library is working again right now! Thanks for [hyeshik](https://github.com/hyeshik)

Korail (www.letskorail.com) wrapper for Python.

This project was inspired from [korail](https://github.com/devxoul/korail) of [devxoul](https://github.com/devxoul).

[korail](https://github.com/devxoul/korail) is not working anymore becuase of a huge change in Korail API.


Documentation
-------------

The documentation is available at [here](http://carpedm20.github.io/korail2/)


Installing
----------

To install korail2, simply:

    $ pip install korail2

Or, you can use:

    $ easy_install korail2

Or, you can also install manually:

    $ git clone git://github.com/carpedm20/korail2.git
    $ cd korail2
    $ python setup.py install

Using
-----

### 1. Login ###

First, you need to create a Korail object.

    >>> from korail2 import Korail
    >>> korail = Korail("12345678", YOUR_PASSWORD) # with membership number
    >>> korail = Korail("carpedm20@gmail.com", YOUR_PASSWORD) # with email
    >>> korail = Korail("010-9964-xxxx", YOUR_PASSWORD) # with phone number

### 2. Search train ###

You can search train schedules `search_train` method. `search_train` method takes these arguments:

- dep : A departure station in Korean  ex) '서울'
- arr : A arrival station in Korean  ex) '부산'
- date : (optional) A departure date in `yyyyMMdd` format
- time : (optional) A departure time in `hhmmss` format
- train_type: (optional) A type of train
    - 00: KTX
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

### 3. Make a reservation ####

You can get your tickes with `tickets` method.

    >>> trains = korail.search_train(dep, arr, date, time)
    >>> seat = korail.reserve(trains[0])
    >>> seat
    [KTX] 8월 23일, 서울~동대구(15:30~17:19) [특실:0][일반실:0], 42500원, 구입기한 8월 18일 14:05

### 4. View reservations ####

You can get your tickes with `tickets` method.

    >>> reservations = korail.reservations()
    >>> reservations
    [[KTX] 8월 23일, 서울~동대구(14:55~16:45) [특실:0][일반실:0], 42500원, 구입기한 8월 18일 14:03,
     [무궁화호] 8월 23일, 서울~동대구(15:03~18:48) [특실:0][일반실:0], 21100원, 구입기한 8월 18일 14:03,
     [KTX] 8월 23일, 서울~동대구(15:30~17:19) [특실:0][일반실:0], 42500원, 구입기한 8월 18일 14:05]

### 5. Get tickets already paid ###

You can see your ticket list with `tickets` method.
You can get the list of paid tickes with `tickets` method.

    >>> tickets = korail.tickets()
    정상발매처리,정상발권처리
    >>> print tickets
    [[KTX] 8월 10일, 동대구~울산(09:26~09:54) => 5호 4A, 13900원]


How do I get the Korail API
---------------------------

1. Extract Korail apk from mobile phone
2. Decompile apk using [dex2jar](https://code.google.com/p/dex2jar/)
3. Read a jar code using [jdgui](http://jd.benow.ca/)
4. Edit a smaili code
5. Recompile a new Korail apk using [apktool](https://code.google.com/p/android-apktool/)
6. Key signing with `motizen-sign`
7. Upload and run a new Korail apk
8. Capture packets and analyze the API


Todo
----

1. Distinguish adult and child
2. Make an option to select special seat or general seat when reserving
3. Make an option to reserve multiple seats at a time
4. Implement payment API


License
-------

Source codes are distributed under BSD license.


Author
------

Taehoon Kim / [@carpedm20](http://carpedm20.github.io/about/)
