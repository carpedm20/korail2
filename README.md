Korail2
=======

[![PyPi version](https://pypip.in/v/korail2/badge.png?style=flat)](https://pypi.python.org/pypi/korail2)
[![PyPi downloads](https://pypip.in/d/korail2/badge.png?style=flat)](https://pypi.python.org/pypi/korail2)
[![PyPi status](https://pypip.in/status/korail2/badge.svg?style=flat)](https://pypi.python.org/pypi/korail2)
[![PyPi license](https://pypip.in/license/korail2/badge.svg?style=flat)](https://pypi.python.org/pypi/korail2)


Korail (www.letskorail.com) wrapper for Python.

This project was inspired from [korail](https://github.com/devxoul/korail) of [devxoul](https://github.com/devxoul).


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

```python
>>> from korail2 import Korail
>>> korail = Korail("12345678", YOUR_PASSWORD) # with membership number
>>> korail = Korail("carpedm20@gmail.com", YOUR_PASSWORD) # with email
>>> korail = Korail("010-9964-xxxx", YOUR_PASSWORD) # with phone number
```

If you do not want login automatically, 

```python
>>> korail = Korail("12345678", YOUR_PASSWORD, auto_login=False)
>>> korail.login()
True
```

When you want change ID using existing object,

```python
>>> korail.login(ANOTHER_ID, ANOTHER_PASSWORD)
True
```

### 2. Search train ###

You can search train schedules `search_train` method. `search_train` method takes these arguments:

- dep : A departure station in Korean  ex) '서울'
- arr : A arrival station in Korean  ex) '부산'
- date : (optional) A departure date in `yyyyMMdd` format
- time : (optional) A departure time in `hhmmss` format
- train_type: (optional) A type of train. You can use constants of TrainType class here.
    default value is TrainType.ALL.
    - 00: TrainType.KTX - KTX 
    - 01: TrainType.SAEMAEUL - 새마을호     
    - 02: TrainType.MUGUNGHWA - 무궁화호
    - 03: TrainType.TONGGEUN - 통근열차
    - 04: TrainType.NURIRO - 누리로
    - 05: TrainType.ALL - 전체 
    - 06: TrainType.AIRPORT - 공항직통
    - 07: TrainType.KTX_SANCHEON - KTX-산천
    - 08: TrainType.ITX_SAEMAEUL - ITX-새마을 
    - 09: TrainType.ITX_CHEONGCHUN - ITX-청춘
- (optional) passengers=None : List of Passenger Objects. None means 1 AdultPassenger.
- (optional) show_all=False : When True, a result includes trains which has no seats.

Below is a sample usage of `search_train`:

```python
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
```

When you want to see sold-out trains.

```python
>>> trains = korail.search_train(dep, arr, date, time, show_all=True)
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
```

#### 2-1. About `passengers` argument

`passengers` is a list(or tuple) of Passeger Objects.
By this, you can search for multiple passengers.
There are 3 types of Passengers now, AdultPassenger, ChildPassenger and SeniorPassenger.

```python
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
```

### 3. Make a reservation ####

You can get your tickets with `tickets` method.

```python
>>> trains = korail.search_train(dep, arr, date, time)
>>> seat = korail.reserve(trains[0])
>>> seat
[KTX] 8월 23일, 서울~동대구(15:30~17:19) 42500원(1석), 구입기한 8월 18일 14:05
```

Multiple.

```python
>>> trains = korail.search_train(dep, arr, date, time)
>>> seat = korail.reserve(trains[0], passengers=psgrs)
>>> seat
[KTX] 8월 23일, 서울~동대구(15:30~17:19) 42500원(3석), 구입기한 8월 18일 14:05
```

When tickets are not enough much for passengers, it raises SoldOutError.
    
If you want to select priority of seat grade, general or special,
There are 4 options in ReserveOption class.

- GENERAL_FIRST : Economic than Comfortable.
- GENERAL_ONLY  : Reserve only general seats. You are poorman ;-)
- SPECIAL_FIRST : Comfortable than Economic.
- SPECIAL_ONLY  : Richman.

```python
>>> korail.reserve(trains[0], psgrs, ReserveOption.GENERAL_ONLY)
```

### 4. Show reservations ####

You can get your tickes with `tickets` method.

```python
>>> reservations = korail.reservations()
>>> reservations
[[KTX] 8월 23일, 서울~동대구(14:55~16:45) 42500원(1석), 구입기한 8월 18일 14:03,
 [무궁화호] 8월 23일, 서울~동대구(15:03~18:48) 21100원(1석), 구입기한 8월 18일 14:03,
 [KTX] 8월 23일, 서울~동대구(15:30~17:19) 42500원(1석), 구입기한 8월 18일 14:05]
```

### 5. Cancel reservation ###

You can also cancel your reservation using Reservation Object from reservations() call.

```python
>>> korail.cancel(reservations[0])
```

### 6. Get tickets already paid ###

You can see your ticket list with `tickets` method.
You can get the list of paid tickes with `tickets` method.

```python
>>> korail = Korail("12345678", YOUR_PASSWORD, want_feedback=True)
>>> tickets = korail.tickets()
정상발매처리,정상발권처리  # You can see these feedbacks when `want_feedback` is True.
>>> print tickets
[[KTX] 8월 10일, 동대구~울산(09:26~09:54) => 5호 4A, 13900원]
```

How do I get the Korail API
---------------------------

1. Extract Korail apk from mobile phone
1. Decompile apk using [dex2jar](https://code.google.com/p/dex2jar/)
1. Read a jar code using [jdgui](http://jd.benow.ca/)
1. Edit a smaili code
1. Recompile a new Korail apk using [apktool](https://code.google.com/p/android-apktool/)
1. Key signing with `motizen-sign`
1. Upload and run a new Korail apk
1. Capture packets and analyze the API


Todo
----

1. Implement payment API


License
-------

Source codes are distributed under BSD license.


Author
------

Taehoon Kim / [@carpedm20](http://carpedm20.github.io/about/)
Hanson Kim / [@sng2c](https://github.com/sng2c)
