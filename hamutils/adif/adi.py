import datetime
from .common import adif_field
"""
from unidecode import unidecode
unidecode(u'北京')


>>> import io
>>> buf = io.StringIO(msg)
>>> buf.readline()
'Bob Smith\n'
>>> buf.readline()
'Jane Doe\n'
>>> len(buf.read())
44

"""

class ParseError(Exception):
    def __init__(self, line, msg):
        self.line = line
        self.msg = msg

    def __str__(self):
        return 'Parse error: %s, in line: %d' % (self.msg, self.line)


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
        res = {}
        while tmp[0] != 'eor':
            try:
                if tmp[3]:
                    res[tmp[0]] = self._convert_field_date(tmp[3], tmp[1])
                elif tmp[0] in adif_field:
                    res[tmp[0]] = self._convert_field_date(adif_field[tmp[0]], tmp[1])
                else:
                    res[tmp[0]] = self._convert_field_date('S', tmp[1])
            except Exception:
                raise ParseError(self._line_num, 'invalid value for %s' % tmp[0])

            tmp = self._readfield()
        if 'qso_date' not in res:
            raise ParseError(self._line_num, 'missing qso_date field')
        if 'time_on' not in res:
            raise ParseError(self._line_num, 'missing time_on field')
        if 'call' not in res:
            raise ParseError(self._line_num, 'missing call field')
        if 'band' not in res:
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

    def _convert_field_date(self, type, data):
        if type == 'B':
            return bool(data)
        elif type == 'N':
            return float(data)
        elif type == 'D':
            return datetime.date(int(data[0:4]), int(data[4:6]), int(data[6:8]))
        elif type == 'T':
            return datetime.time(int(data[0:2]), int(data[2:4]), int(data[4:6]))
        else:
            return data

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
                        raise  ParseError(self._line_num, 'missing field name')
                elif c == '>':
                    f_name = f_name.lower()
                    if len(f_name) > 0:
                       state = 'c'
                    else:
                        raise  ParseError(self._line_num, 'missing field name')
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
                return (f_name, f_data, f_len, f_type)
            else:
                if c == '\n':
                    self._line_num += 1
                c = self._flo.read(1)


class ADIWriter:
    pass
