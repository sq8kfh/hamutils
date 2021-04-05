import datetime
from .common import ParseError, WriteError, adif_field, convert_field, convert_freq_to_band
from unidecode import unidecode


class ParseErrorIncData(ParseError):
    def __init__(self, line):
        ParseError.__init__(self, line, 'incomplete data')


class ADIReader:
    def __init__(self, flo):
        self._flo = flo
        self._line_num = 1
        tmp = self._readfield()
        while tmp[0] != 'eoh':
            tmp = self._readfield()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            tmp = self._readfield()
        except ParseErrorIncData:
            raise StopIteration
        if tmp[0] == 'app_lotw_eof':
            raise StopIteration
        res = {}
        while tmp[0] != 'eor':
            try:
                res[tmp[0]] = convert_field(tmp[0], tmp[1], tmp[3])
            except Exception:
                raise ParseError(self._line_num, 'invalid value for \'%s\'' % tmp[0])

            tmp = self._readfield()
        if 'qso_date' not in res:
            raise ParseError(self._line_num, 'missing qso_date field')
        if 'time_on' not in res:
            raise ParseError(self._line_num, 'missing time_on field')
        if 'call' not in res:
            raise ParseError(self._line_num, 'missing call field')
        if 'band' not in res:
            if 'freq' in res:
                tmpband = convert_freq_to_band(res['freq'])
                if tmpband:
                    res['band'] = convert_freq_to_band(res['freq'])
                else:
                    raise ParseError(self._line_num, 'error in freq to band conversion')
            else:
                raise ParseError(self._line_num, 'missing band field')
        if 'mode' not in res:
            raise ParseError(self._line_num, 'missing mode field')

        res['datetime_on'] = datetime.datetime.combine(res['qso_date'], res['time_on'])
        if 'time_off' in res:
            if 'qso_date_off' in res:
                res['datetime_off'] = datetime.datetime.combine(res['qso_date_off'], res['time_off'])
                del res['qso_date_off']
            else:
                res['datetime_off'] = datetime.datetime.combine(res['qso_date'], res['time_off'])
            del res['time_off']
        del res['time_on']
        del res['qso_date']
        return res

    def _readfield(self):
        c = self._flo.read(1)
        state = 'n'
        f_name = ''
        f_len = ''
        tmp_f_len = 0
        f_type = ''
        f_data = ''
        while True:
            if c == '':
                raise ParseErrorIncData(self._line_num)

            if state == 'n':
                if c == '<':
                    state = 'f'
            elif state == 'f':
                if c == ':':
                    f_name = f_name.lower()
                    if len(f_name) > 0:
                        state = 'l'
                    else:
                        raise ParseError(self._line_num, 'missing field name')
                elif c == '>':
                    f_name = f_name.lower()
                    if len(f_name) > 0:
                        state = 'c'
                    else:
                        raise ParseError(self._line_num, 'missing field name')
                else:
                    f_name += c
            elif state == 'l':
                if c == ':':
                    try:
                        f_len = int(f_len)
                    except:
                        raise ParseError(self._line_num, 'invalid value for data length')
                    tmp_f_len = f_len
                    state = 't'
                elif c == '>':
                    try:
                        f_len = int(f_len)
                    except:
                        raise ParseError(self._line_num, 'invalid value for data length')
                    tmp_f_len = f_len
                    if f_len > 0:
                        state = 'd'
                    else:
                        state = 'c'
                else:
                    f_len += c
            elif state == 't':
                if c == '>':
                    if f_len > 0:
                        state = 'd'
                    else:
                        state = 'c'
                else:
                    f_type += c
            elif state == 'd':
                f_data += c
                tmp_f_len -= 1
                if tmp_f_len == 0:
                    state = 'c'

            if state == 'c':
                return f_name, f_data, f_len, f_type
            else:
                if c == '\n':
                    self._line_num += 1
                c = self._flo.read(1)


class ADIWriter:
    adif_ver = '3.0.5'

    def __init__(self, flo, program_id=None, program_version=None, compact=False):
        self._flo = flo
        if program_id:
            self.program_id = program_id
            if program_version:
                self.program_version = program_version
            else:
                self.program_version = None
        else:
            from hamutils import __version__ as hamutils_version
            self.program_version = hamutils_version
            self.program_id = 'hamutils'
        self._compact = compact
        self._head_writed = False
        self._newline = '\r\n'.encode('ascii')

    def write_header(self):
        self._flo.write(self._write_field('adif_ver', self.adif_ver))
        self._flo.write(self._newline)
        tmp_data = datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')
        self._flo.write(self._write_field('created_timestamp', tmp_data))
        self._flo.write(self._newline)
        self._flo.write(self._write_field('programid', self.program_id))
        self._flo.write(self._newline)
        if self.program_version:
            self._flo.write(self._write_field('programversion', self.program_version))
            self._flo.write(self._newline)
        self._flo.write(self._write_field('eoh', None))
        self._flo.write(self._newline)
        self._head_writed = True

    def add_qso(self, **kw):
        if not self._head_writed:
            self.write_header()

        if not self._compact:
            self._flo.write(self._newline)

        if 'datetime_on' in kw:
            tmp = kw['datetime_on']
            kw['qso_date'] = tmp.date()
            kw['time_on'] = tmp.time()
            del kw['datetime_on']
        if 'datetime_off' in kw:
            tmp = kw['datetime_off']
            t_date = tmp.date()
            if t_date != kw['qso_date']:
                kw['qso_date_off'] = t_date
            elif 'qso_date_off' in kw:
                del kw['qso_date_off']
            kw['time_off'] = tmp.time()
            del kw['datetime_off']

        def writefield(field, data):
            if data == None:
                return
            l_field = field.lower()
            if l_field in adif_field:
                if adif_field[l_field] == 'D':
                    tmp_data = data.strftime('%Y%m%d')
                elif adif_field[l_field] == 'T':
                    tmp_data = data.strftime('%H%M%S')
                elif adif_field[l_field] == 'B':
                    tmp_data = 'Y' if data else 'N'
                else:
                    tmp_data = str(data)
                self._flo.write(self._write_field(l_field, tmp_data))
                if not self._compact:
                    self._flo.write(self._newline)
            elif l_field.startswith('app_'):
                tmp_data = str(data)
                self._flo.write(self._write_field(l_field, tmp_data))
                if not self._compact:
                    self._flo.write(self._newline)
            else:
                raise WriteError('unknown field: \'%s\'' % l_field)

        if 'qso_date' in kw and kw['qso_date']:
            writefield('qso_date', kw['qso_date'])
            del kw['qso_date']
        else:
            raise WriteError('missing field: \'qso_date\'')

        if 'time_on' in kw and kw['time_on']:
            writefield('time_on', kw['time_on'])
            del kw['time_on']
        else:
            raise WriteError('missing field: \'time_on\'')

        if 'call' in kw and kw['call']:
            writefield('call', kw['call'])
            del kw['call']
        else:
            raise WriteError('missing field: \'call\'')

        if 'band' in kw and kw['band']:
            writefield('band', kw['band'])
            del kw['band']
        else:
            raise WriteError('missing field: \'band\'')

        if 'mode' in kw and kw['mode']:
            writefield('mode', kw['mode'])
            del kw['mode']
        else:
            raise WriteError('missing field: \'mode\'')

        for field in kw:
            writefield(field, kw[field])
        self._flo.write(self._write_field('eor', None))
        self._flo.write(self._newline)

    def close(self):
        if not self._head_writed:
            self.write_header()
        self._flo.close()

    @staticmethod
    def _write_field(name, data, data_type=None):
        name = name.lower()
        if data:
            data = str(data).replace('\r\n', '\n').replace('\n', '\r\n')
            data = unidecode(data)
            dlen = len(data)
            if data_type:
                raw = '<%s:%d:%s>%s' % (name, dlen, data_type, data)
            else:
                raw = '<%s:%d>%s' % (name, dlen, data)
        else:
            raw = '<%s:0>' % name

        return unidecode(raw).encode('ascii')
