# -*- coding: utf-8 -*-
"""
    hugh.i18n
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2009 by the Zine Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime
from time import strptime

DATE_FORMATS = ['%m/%d/%Y', '%d/%m/%Y', '%Y%m%d', '%d. %m. %Y',
                '%m/%d/%y', '%d/%m/%y', '%d%m%y', '%m%d%y', '%y%m%d']
TIME_FORMATS = ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p']


def lazy_gettext(text):
    return unicode(text)


def _(text):
    return unicode(text)


def ngettext(singular, plural, n):
    if n == 1:
        return unicode(singular)
    else:
        return unicode(plural)


def parse_datetime(string, rebase=True):
    """Parses a string into a datetime object.  Per default a conversion
    from the blog timezone to UTC is performed but returned as naive
    datetime object (that is tzinfo being None).  If rebasing is disabled
    the string is expected in UTC.

    The return value is **always** a naive datetime object in UTC.  This
    function should be considered of a lenient counterpart of
    `format_system_datetime`.
    """
    # shortcut: string as None or "now" or the current locale's
    # equivalent returns the current timestamp.
    if string is None or string.lower() in ('now', _('now')):
        return datetime.utcnow().replace(microsecond=0)

    def convert(format):
        """Helper that parses the string and convers the timezone."""
        rv = datetime(*strptime(string, format)[:7])
        return rv.replace(microsecond=0)

    # first of all try the following format because this is the format
    # Texpress will output by default for any date time string in the
    # administration panel.
    try:
        return convert(u'%Y-%m-%d %H:%M')
    except ValueError:
        pass

    # no go with time only, and current day
    for fmt in TIME_FORMATS:
        try:
            val = convert(fmt)
        except ValueError:
            continue
        return datetime.utcnow().replace(hour=val.hour, minute=val.minute,
                                         second=val.second, microsecond=0)

    # no try various types of date + time strings
    def combined():
        for t_fmt in TIME_FORMATS:
            for d_fmt in DATE_FORMATS:
                yield t_fmt + ' ' + d_fmt
                yield d_fmt + ' ' + t_fmt

    for fmt in combined():
        try:
            return convert(fmt)
        except ValueError:
            pass

    raise ValueError('invalid date format')


def format_system_datetime(datetime=None, rebase=True):
    """Formats a system datetime.  This is the format the admin
    panel uses by default.  (Format: YYYY-MM-DD hh:mm and in the
    user timezone unless rebase is disabled)
    """
    return u'%d-%02d-%02d %02d:%02d' % (
        datetime.year,
        datetime.month,
        datetime.day,
        datetime.hour,
        datetime.minute
    )


