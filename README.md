Korail2
=======

Korail (www.letskorail.com) wrapper for Python.

This project was inspired from [korail](https://github.com/devxoul/korail) of [devxoul](https://github.com/devxoul)


Installing
----------

1. using pip:
    $ pip install korail2
2. using easy_install:
    $ easy_install korail2
3. using git
    $ git clone git://github.com/carpedm20/korail2.git
    $ cd korail2
    $ python setup.py install

Using
-----

### 1. Login ###

First, you need to create a Korail object.

    from korail2 import Korail

    korail = Korail("12345678", YOUR_PASSWORD) # with membership number
    korail = Korail("carpedm20@gmail.com", YOUR_PASSWORD) # with email
    korail = Korail("010-9964-xxxx", YOUR_PASSWORD) # with phone number

### 2. Search train ###

You can search train schedules `search_train` method. `search_train` method takes these arguments:

- dep : A departure station in Korean  ex) '서울'
- arr : A arrival station in Korean  ex) '부산'
- date : (optional) A departure date in `yyyyMMdd` format
- time : (optional) A departure time in `hhmmss` format
- train_type: (optional) A type of train
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

    dep = '서울'
    arr = '동대구'
    date = '20140815'
    time = '144000'
    trains = korail.search_train(dep, arr, date, time)


License
-------

Source codes are distributed under BSD license.


Author
------

Taehoon Kim / [@carpedm20](http://carpedm20.github.io/about/)
