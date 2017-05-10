import datetime
from xml.dom import minidom, Node
from .common import ParseError, convert_field, adif_utf_field


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

                    print("'%s' = %s" % (field, data))

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
    pass
