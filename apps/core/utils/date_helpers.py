import re
from datetime import datetime, timedelta, tzinfo

import dateutil.tz
import pytz
from dateutil import parser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.timezone import utc

TZ_OFFSET = re.compile(r'^(.*?)\s?([-\+])(\d\d):?(\d\d)$')

tz_str = '''-12 Y
11 X NUT SST
10 W CKT HAST HST TAHT TKT
9 V AKST GAMT GIT HADT HNY
8 U AKDT CIST HAY HNP PST PT
7 T HAP HNR MST PDT
6 S CST EAST GALT HAR HNC MDT
5 R CDT COT EASST ECT EST ET HAC HNE PET
4 Q AST BOT CLT COST EDT FKT GYT HAE HNA PYT
3 P ADT ART BRT CLST FKST GFT HAA PMST PYST SRT UYT WGT
2 O BRST FNT PMDT UYST WGST
1 N AZOT CVT EGT
0 Z EGST GMT UTC WET WT
1 A CET DFT WAT WEDT WEST
2 B CAT CEDT CEST EET SAST WAST
3 C EAT EEDT EEST IDT MSK
4 D AMT AZT GET GST KUYT MSD MUT RET SAMT SCT
5 E AMST AQTT AZST HMT MAWT MVT PKT TFT TJT TMT UZT YEKT
6 F ALMT BIOT BTT IOT KGT NOVT OMST YEKST
7 G CXT DAVT HOVT ICT KRAT NOVST OMSST THA WIB
8 H ACT AWST BDT BNT CAST HKT IRKT KRAST MYT PHT SGT ULAT WITA WST
9 I AWDT IRKST JST KST PWT TLT WDT WIT YAKT
10 K AEST ChST PGT VLAT YAKST YAPT
11 L AEDT LHDT MAGT NCT PONT SBT VLAST VUT
12 M ANAST ANAT FJT GILT MAGST MHT NZST PETST PETT TVT WFT
13 FJST NZDT
11.5 NFT
10.5 ACDT LHST
9.5 ACST
6.5 CCT MMT
5.75 NPT
5.5 SLT
4.5 AFT IRDT
3.5 IRST
2.5 HAT NDT
3.5 HNT NST NT
4.5 HLV VET
9.5 MART MIT'''

tzd = {}
for tz_descr in map(str.split, tz_str.split('\n')):
    tz_offset = int(float(tz_descr[0]) * 3600)
    for tz_code in tz_descr[1:]:
        tzd[tz_code] = tz_offset


def date_parse(ds):
    ''' Parse datetime string (with time zone) to datetime object '''
    if not isinstance(ds, datetime):
        return parser.parse(ds, tzinfos=tzd)
    return ds


def toUTC(dt):
    ''' accept string or datetime and return datetime in UTC '''
    dt = date_parse(dt)
    if dt:
        offset = dt.utcoffset()
        if offset:
            dt = dt - offset
            return dt.replace(tzinfo=dateutil.tz.tzutc())
    return None


def toLocalZone(dt):
    ''' accept string or datetime and return datetime in local zone '''
    dt = date_parse(dt)
    if dt and dt.tzinfo:
        return dt.astimezone(dateutil.tz.tzlocal())
    else:
        None


def toSimpleDateTime(dt):
    dt = timezone.localtime(dt)
    return dt.replace(tzinfo=None)


def currentDate():
    dt = datetime.utcnow()
    return dt.replace(tzinfo=dateutil.tz.tzutc())


def currentDate2():
    return datetime.utcnow().replace(tzinfo=utc)


class TZDatetime(datetime):

    def aslocaltimezone(self):
        """Returns the datetime in the local time zone."""
        tz = pytz.timezone(settings.TIME_ZONE)
        return self.astimezone(tz)


def force_tz(obj, tz):
    """Converts a datetime to the given timezone.

    The tz argument can be an instance of tzinfo or a string such as
    'Europe/London' that will be passed to pytz.timezone. Naive datetimes are
    forced to the timezone. Wise datetimes are converted.
    """
    if not isinstance(tz, tzinfo):
        tz = pytz.timezone(tz)

    if (obj.tzinfo is None) or (obj.tzinfo.utcoffset(obj) is None):
        return tz.localize(obj)
    else:
        return obj.astimezone(tz)
