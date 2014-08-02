Korail2
=======

Korail (www.letskorail.com) wrapper for Python.

Code structure is inspired by [korail](https://github.com/devxoul/korail) of [devxoul](http://xoul.kr)


Installing
----------

1. using pip:

    $ pip install line

1. using easy_install:

    $ easy_install line

1. using git

    $ git clone git://github.com/carpedm20/line.git
    $ cd line
    $ python setup.py install

Using
-----

First, you need to make a korail object.

    >>> from korail2 import Korail
    >>> korail = Korail("12345678", YOUR_PASSWORD) # with membership number
    >>> korail = Korail("carpedm20@gmail.com", YOUR_PASSWORD) # with email
    >>> korail = Korail("010-9964-xxxx", YOUR_PASSWORD) # with phone number



License
-------

Source codes are distributed under BSD license.


Author
------

Taehoon Kim / [@carpedm20](http://carpedm20.github.io/about/)
