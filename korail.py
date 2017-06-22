# -*- coding: utf-8 -*-

# sudo pip install --upgrade git+https://github.com/carpedm20/korail2.git@sng2c

from korail2 import *
import time
import sys

KORAIL_ID = '0443474772'
KORAIL_PW = 'illb2ack'

PUSHOVER_APP_TOKEN = 'APP_TOKEN'
PUSHOVER_USER_TOKEN = 'USER_TOKEN'

DEP = '서울'
ARV = '구포'
DEP_DATE = '20170709'
DEP_TIME = '100000'
PSGRS = [AdultPassenger(1)]
TRAIN_TYPE = TrainType.KTX


def sendnoti(msg):
    pass
    
k = Korail(KORAIL_ID, KORAIL_PW, auto_login=False)
if not k.login():
    print "login fail"
    exit(-1)
while True:
    notFound = True
    while notFound:
        try:
            sys.stdout.write( "Finding Seat %s ➜ %s              \r" %(DEP, ARV) )
            sys.stdout.flush()
            trains = k.search_train_allday(DEP, ARV, DEP_DATE, DEP_TIME, passengers=PSGRS, train_type=TRAIN_TYPE)
            print trains
            print "Found!!"
            notFound = False
        except NoResultsError:
            sys.stdout.write("No Seats                               \r")
            sys.stdout.flush()
            time.sleep(2)
        except Exception as e:
            print e
            time.sleep(2)

    k.login()
    seat = None
    ok = False
    try:
        seat = k.reserve(trains[0], passengers=PSGRS)
        ok = True
    except KorailError, e:
        print e
        sendnoti(e)
        break

    if ok:
        print seat
        sendnoti(repr(seat))
        break
