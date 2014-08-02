Korail2
=======

Korail (www.letskorail.com) wrapper for Python.

This project was inspired from [korail](https://github.com/devxoul/korail) of [devxoul](https://github.com/devxoul)


Installing
----------

1. using pip:

    $ pip install korail2

1. using easy_install:

    $ easy_install korail2

1. using git

    $ git clone git://github.com/carpedm20/korail2.git
    $ cd korail2
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
