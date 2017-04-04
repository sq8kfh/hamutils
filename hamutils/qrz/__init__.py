"""
Provides access to the QRZ's XML subscription data service (https://www.qrz.com/XML/current_spec.html).
"""
import urllib.parse
import urllib.request
import xml.dom.minidom


class QrzException(Exception):
    """Qrz base exceptions"""
    pass


class Qrz(object):
    """Interface to qrz.com XML subscription data service.

    Attributes:
        message (str): Message returned by last query.
    """
    _qrz_api_url = 'http://xmldata.qrz.com/xml/1.33/'
    _qrz_tls_api_url = 'https://xmldata.qrz.com/xml/1.33/'

    def __init__(self, username=None, password=None, *, usetls=True):
        """Initialize object and if username and password are set establish session

        Args:
            username (str, optional): qrz.com's username
            password (str, optional): qrz.com's password
            usetls (bool, optional): if true https will be used to login
        """
        self.message = ''
        self._key = None
        self._usetls = usetls
        if username and password:
            response = None
            try:
                data = None
                data = urllib.parse.urlencode({'username': username, 'password': password, 'agent': 'hamutils'})
                data = data.encode('ascii')
                if usetls:
                    response = urllib.request.urlopen(self._qrz_tls_api_url, data)
                else:
                    response = urllib.request.urlopen(self._qrz_api_url, data)
            finally:
                del data
                del password

            with xml.dom.minidom.parse(response) as dom:
                self._setmessage(dom)
                self._setkey(dom)

    def lookup(self, call, *, username=None, password=None):
        """Make a callsign query and if username and password are set establish session

        Args:
            call (str): callsign
            username (str, optional if session is established): qrz.com's username
            password (str, optional if session is established): qrz.com's password

        Returns:
            Dictionary if successful, None otherwise.
        """
        response = None
        if self._key:
            data = urllib.parse.urlencode({'s': self._key, 'callsign': call})
            data = data.encode('ascii')
            response = urllib.request.urlopen(self._qrz_api_url, data)
        elif username and password:
            try:
                data = urllib.parse.urlencode({'username': username, 'password': password, 'callsign': call, 'agent': 'hamutils'})
                data = data.encode('ascii')
                if self._usetls:
                    response = urllib.request.urlopen(self._qrz_tls_api_url, data)
                else:
                    response = urllib.request.urlopen(self._qrz_api_url, data)
            finally:
                del data
                del password
        else:
            raise QrzException('Missing authentication data')
        with xml.dom.minidom.parse(response) as dom:
            self._setmessage(dom)
            self._setkey(dom)
            return self._getcalldata(dom)

    def _setmessage(self, dom):
        tmp = self._getdata(dom, 'Message')
        if tmp:
            self.message = tmp
        else:
            self.message = ''

    def _setkey(self, dom):
        key = dom.getElementsByTagName('Key')
        if key:
            key = key[0]
            self._key = self._gettext(key.childNodes)
        else:
            error = dom.getElementsByTagName('Error')
            if error:
                error = error[0]
                raise QrzException(self._gettext(error.childNodes))
            else:
                raise QrzException('Unknown response')

    def _getdata(self, dom, nodename):
        node = dom.getElementsByTagName(nodename)
        if node:
            node = node[0]
            return self._gettext(node.childNodes)
        else:
            return None

    def _gettext(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def _getcalldata(self, dom):
        node_array = ['call', 'aliases', 'dxcc', 'fname', 'name', 'addr1', 'addr2', 'state', 'zip',
                      'country', 'ccode', 'lat', 'lon', 'grid', 'county', 'fips', 'land', 'efdate',
                      'expdate', 'p_call', 'class', 'codes', 'qslmgr', 'email', 'url', 'u_views',
                      'bio', 'image', 'serial', 'moddate', 'MSA', 'AreaCode', 'TimeZone', 'GMTOffset',
                      'DST', 'eqsl', 'mqsl', 'cqzone', 'ituzone', 'geoloc', 'born']
        res = {}
        for node in node_array:
            tmp = self._getdata(dom, node)
            if tmp:
                res[node] = tmp
        return res
