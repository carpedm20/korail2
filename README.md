Korail2
=======

Korail (www.letskorail.com) wrapper for Python.

This project was inspired from [korail](https://github.com/devxoul/korail) of [devxoul](https://github.com/devxoul)


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
    [[KTX #145] 서울~동대구(14:00~15:54) [특실:1][일반실:1] 예약가능,
     [ITX-새마을 #1063] 서울~동대구(14:07~17:47) [일반실:1] 예약가능,
     [KTX #147] 서울~동대구(14:15~16:04) [특실:1][일반실:1] 예약가능,
     [무궁화호 #1215] 서울~동대구(14:25~18:15) [일반실:1] 예약가능,
     [KTX #149] 서울~동대구(14:30~16:18) [특실:1][일반실:1] 예약가능,
     [KTX #307] 서울~동대구(14:40~16:29) [특실:1][일반실:1] 예약가능,
     [KTX #153] 서울~동대구(15:00~16:53) [특실:1][일반실:1] 예약가능,
     [무궁화호 #1217] 서울~동대구(15:03~18:48) [일반실:1] 예약가능,
     [KTX #155] 서울~동대구(15:30~17:19) [특실:1][일반실:1] 예약가능,
     [무궁화호 #1303] 서울~동대구(15:35~19:40) [일반실:1] 예약가능]

### 3. Get tickets###

You can get your tickes with `tickets` method.

    >>> k.tickets()
    [[KTX #113] 동대구~울산(09:26~09:54)  => 5호 4A, 13900원]


License
-------

Source codes are distributed under BSD license.


Author
------

Taehoon Kim / [@carpedm20](http://carpedm20.github.io/about/)
