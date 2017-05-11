import datetime


class CabrilloWriter:
    cabrillo_ver = '3.0'

    def __init__(self, flo, program_id=None, program_version=None):
        self._flo = flo
        self._newline = '\r\n'.encode('ascii')
        self._header_writed = False
        self._flo.write(('START-OF-LOG: %s' % self.cabrillo_ver).encode('ascii'))
        self._flo.write(self._newline)

        if program_id:
            if program_version:
                self.write_tag('CREATED-BY', '%s %s' % (program_id, program_version))
            else:
                self.write_tag('CREATED-BY', '%s' % (program_id))
        else:
            from hamutils import __version__ as hamutils_version
            self.write_tag('CREATED-BY', 'hamutils %s' % hamutils_version)


    def write_tags(self, **kw):
        for tag, data in kw.items():
            self.write_tag(tag, data)

    def write_tag(self, tag, data):
        if self._header_writed:
            return
        tmp = '%s: %s' % (tag.upper(), data)
        self._flo.write(tmp.encode('ascii'))
        self._flo.write(self._newline)

    def add_qso(self, freq, mode, datetime_on, my_call, rst_sent, exch_sent, call, rst_rcvd, exch_rcvd, transmitter='0'):
        self._header_writed = True
        d = datetime_on.strftime('%Y-%m-%d')
        t = datetime_on.strftime('%H%M')
        tmp = 'QSO: %5s %2s %s %s %-13s %3s %-6s %-13s %3s %-6s %1s' % (freq, mode, d, t, my_call, rst_sent, exch_sent,
                                                                        call, rst_rcvd, exch_rcvd, transmitter)

        self._flo.write(tmp.encode('ascii'))
        self._flo.write(self._newline)

    def close(self):
        self._flo.write('END-OF-LOG:'.encode('ascii'))
        self._flo.write(self._newline)
        self._flo.close()
