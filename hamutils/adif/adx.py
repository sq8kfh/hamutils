import datetime
from unidecode import unidecode
from xml.dom import minidom, Node
from .common import ParseError, WriteError, convert_field, adif_utf_field, adif_rev_utf_field, adif_field


class ADXReader:
    def __init__(self, flo):
        self._xmldoc = minidom.parse(flo)

    def __iter__(self):
        qsos = self._xmldoc.getElementsByTagName('RECORDS')
        if qsos:
            qsos = qsos[0]
        else:
            qsos = self._xmldoc.getElementsByTagName('records')
            if qsos:
                qsos = qsos[0]
            else:
                return

        for qso in qsos.childNodes:
            if qso.nodeType != Node.ELEMENT_NODE:
                continue
            res = {}
            for node in qso.childNodes:
                if node.nodeType == Node.ELEMENT_NODE and node.hasChildNodes():
                    field = node.nodeName.lower()
                    data = None
                    if node.childNodes[0].nodeType == Node.TEXT_NODE:
                        data = node.childNodes[0].nodeValue
                        if field == 'app':
                            progid = node.getAttribute('PROGRAMID')
                            if not progid:
                                progid = node.getAttribute('programid')
                            fieldname = node.getAttribute('FIELDNAME')
                            if not fieldname:
                                fieldname = node.getAttribute('fieldname')
                            field = ('%s_%s_%s' % (field, progid, fieldname)).lower()
                        res[field] = convert_field(field, data, None)

            if 'qso_date' not in res:
                raise ParseError(0, 'missing qso_date field')
            if 'time_on' not in res:
                raise ParseError(0, 'missing time_on field')
            if 'call' not in res:
                raise ParseError(0, 'missing call field')
            if 'band' not in res:
                raise ParseError(0, 'missing band field')
            if 'mode' not in res:
                raise ParseError(0, 'missing mode field')

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

            for utf_field in adif_utf_field:
                if utf_field in res:
                    res[adif_utf_field[utf_field]] = res[utf_field]
                    del res[utf_field]

            yield res

class ADXWriter:
    adif_ver = '3.0.5'

    def __init__(self, flo, program_id=None, program_version=None, compact=False):
        self._flo = flo
        self._doc = minidom.Document()
        root = self._doc.createElement('ADX')
        self._doc.appendChild(root)
        header = self._doc.createElement('HEADER')

        header.appendChild(self._create_node('ADIF_VER', self.adif_ver))
        tmp_data = datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')
        header.appendChild(self._create_node('CREATED_TIMESTAMP', tmp_data))

        if program_id:
            header.appendChild(self._create_node('PROGRAMID', program_id))
            if program_version:
                header.appendChild(self._create_node('PROGRAMVERSION', program_version))
        else:
            from hamutils import __version__ as hamutils_version
            header.appendChild(self._create_node('PROGRAMID', 'hamutils'))
            header.appendChild(self._create_node('PROGRAMVERSION', hamutils_version))

        root.appendChild(header)
        self._records = self._doc.createElement('RECORDS')
        root.appendChild(self._records)
        self._compact = compact

    def add_qso(self, **kw):
        record = self._doc.createElement('RECORD')
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


        if 'qso_date' in kw and kw['qso_date']:
            self._create_field(record, 'qso_date', kw['qso_date'])
            del kw['qso_date']
        else:
            raise WriteError('missing field: \'qso_date\'')

        if 'time_on' in kw and kw['time_on']:
            self._create_field(record, 'time_on', kw['time_on'])
            del kw['time_on']
        else:
            raise WriteError('missing field: \'time_on\'')

        if 'call' in kw and kw['call']:
            self._create_field(record, 'call', kw['call'])
            del kw['call']
        else:
            raise WriteError('missing field: \'call\'')

        if 'band' in kw and kw['band']:
            self._create_field(record, 'band', kw['band'])
            del kw['band']
        else:
            raise WriteError('missing field: \'band\'')

        if 'mode' in kw and kw['mode']:
            self._create_field(record, 'mode', kw['mode'])
            del kw['mode']
        else:
            raise WriteError('missing field: \'mode\'')

        for field in kw:
            self._create_field(record, field, kw[field])
        self._records.appendChild(record)

    def _create_node(self, name, data, data_type=None):
        name = name.upper()
        if name.startswith('APP_'):
            app,prog,field = name.split('_')
            el = self._doc.createElement('APP')
            el.setAttribute('PROGRAMID', prog)
            el.setAttribute('FIELDNAME', field)
            if data_type:
                el.setAttribute('TYPE', data_type)
        else:
            el = self._doc.createElement(name)
        if data:
            text = self._doc.createTextNode(data)
            el.appendChild(text)
        return el

    def _create_field(self, record_node, field, data):
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

            if l_field in adif_rev_utf_field and unidecode(tmp_data) != tmp_data:
                record_node.appendChild(self._create_node(adif_rev_utf_field[l_field], tmp_data))
            record_node.appendChild(self._create_node(l_field, unidecode(tmp_data)))
        elif l_field.startswith('app_'):
            tmp_data = str(data)
            record_node.appendChild(self._create_node(l_field, tmp_data))
        else:
            raise WriteError('unknown field: \'%s\'' % l_field)

    def close(self):
        if self._compact:
            self._flo.write(self._doc.toxml(encoding='UTF-8'))
        else:
            self._flo.write(self._doc.toprettyxml(indent="  ", encoding='UTF-8'))
        self._flo.close()
