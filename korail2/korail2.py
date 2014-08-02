
"""
    korail2.korail2
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""
import re
try:
    import simplejson as json
except ImportError:
    import json

EMAIL_REGEX        = re.compile(r"[^@]+@[^@]+\.[^@]+")
PHONE_NUMBER_REGEX = re.compile(r"(\d{3})-(\d{3,4})-(\d{4})")

SCHEME      = "https"
KORAIL_HOST = "smart.letskorail.com"
KORAIL_PORT = "443"

KORAIL_DOMAIN = "%s://%s:%s" % (SCHEME, KORAIL_HOST, KORAIL_PORT)
KORAIL_COMMON = "%s/classes/com.korail.mobile.common" % KORAIL_DOMAIN
KORAIL_LOGIN  = "%s/classes/com.korail.mobile.login.Login" % KORAIL_DOMAIN

KORAIL_LOGOUT           = "%s.logout" % KORAIL_COMMON
KORAIL_STATION_DB       = "%s.stationinfo?device=ip" % KORAIL_COMMON
KORAIL_STATION_DB_DATA  = "%s.stationdata" % KORAIL_COMMON
KORAIL_EVENT            = "%s.event" % KORAIL_COMMON
KORAIL_PAYMENT          = "%s/ebizmw/PrdPkgMainList.do" % KORAIL_DOMAIN
KORAIL_PAYMENT_VOUNCHER = "%s/ebizmw/PrdPkgBoucherView.do" % KORAIL_DOMAIN


class Korail(object):
    """Korail object"""
    _session = requests.session()

    def __init__(self, id, password):
        self.id = id
        self.password = password

    def _login(self, id, password):
        """Login to Korail server.

        :param id: `Korail membership number` or `phone number` or `email`
                   membership   : xxxxxxxx (8 digits) 
                   phone number : xxx-xxxx-xxxx
                   email        : xxx@xxx.xxx
        :param password: Korail account password
        """
        if EMAIL_REGEX.match(id):
            txtInputFlg = '5'
        elif PHONE_NUMBER_REGEX.match(id):
            txtInputFlg = '4'
        else:
            txtInputFlg = '2'

        url  = KORAIL_LOGIN
        data = {
            'Device'      : 'AD',
            'Version'     : '130607001',
            # 2 : for membership number,
            # 4 : for phone number,
            # 5 : for email,
            'txtInputFlg' : txtInputFlg,
            'txtMemberNo' : id,
            'txtPwd'      : password
        }

        r = self._session.post(url, data=data)
        j = json.loads(r.text)

        if r['strResult'] == 'SUCC':
            return True

        return False
