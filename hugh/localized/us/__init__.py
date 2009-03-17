import re

from hugh import forms
from hugh import validators
from hugh.localized.us import states

_zip_code_re = re.compile(r'^\d{5}(?:-\d{4})?$')


def is_valid_us_zip_code(message=None):
    """
    Validates a US zip code.

    >>> from hugh.validators import check
    >>> check(is_valid_us_zip_code, '12345')
    True
    >>> check(is_valid_us_zip_code, '12345-6789')
    True
    >>> check(is_valid_us_zip_code, '123456789')
    False
    >>> check(is_valid_us_zip_code, 'abcde')
    False
    """
    if message is None:
        message = u'The zip code must be in the format ##### or #####-####'
    def validator(form, value):
        if _zip_code_re.match(value) is None:
            raise validators.ValidationError(message)
    return validator


class USPhoneNumberField(forms.TextField):
    """
    Validates a US-style phone number.

    >>> field = USPhoneNumberField()

    The standard format is 10 digits separated by dashes:
    >>> field('555-555-5555')
    u'555-555-5555'

    A leading "1-" is optional, but removed in normalization:
    >>> field('1-555-555-5555')
    u'555-555-5555'

    Dots can also be used to separated the fields and get converted to dashes:
    >>> field('555.555.5555')
    u'555-555-5555'

    Separators can also be omitted entirely and get inserted during conversion:
    >>> field('5555555555')
    u'555-555-5555'

    Common separators mixed in are removed and normalized:
    >>> field('1.(555)   555 - 5555')
    u'555-555-5555'

    Note that area codes cannot begin with a "1" or a "0":
    >>> field('155-555-5555')
    Traceback (most recent call last):
      ...
    ValidationError: Phone area codes cannot begin with a "1" or "0"
    >>> field('055-555-5555')
    Traceback (most recent call last):
      ...
    ValidationError: Phone area codes cannot begin with a "1" or "0"

    And of course values with a completely wrong format do not validate:
    >>> field('12345')                          #doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValidationError: Please enter a phone number with area code in the format
    555-867-5309

    The value may be empty if it is not marked as required:
    >>> USPhoneNumberField(required=True)('')
    Traceback (most recent call last):
      ...
    ValidationError: This field is required.
    >>> USPhoneNumberField(required=False)('')
    u''
    """
    _phone_digits_re = re.compile(r'^1?(\d{3})(\d{3})(\d{4})$')
    _phone_digits_strip_re = re.compile(r'[-\.()\s]')

    messages = dict(
        invalid_phone = (u'Please enter a phone number with area code in the'
                         ' format 555-867-5309'),
        bad_area_code = u'Phone area codes cannot begin with a "1" or "0"',
    )

    def convert(self, value):
        value = forms.TextField.convert(self, value)
        if not value and not self.required:
            return value
        value = self._phone_digits_strip_re.sub('', value)
        match = self._phone_digits_re.match(value)
        if not match:
            raise validators.ValidationError(self.messages['invalid_phone'])
        if match.group(1)[0] in '01':
            raise validators.ValidationError(self.messages['bad_area_code'])
        return u'-'.join(match.groups())


class USStateField(forms.TextField):
    """
    Validates that the input is a 2-character U.S. state or territory code.

    Input values are normalized to upper-case characters.
    """
    messages = dict(
        invalid_state = u'Enter a valid 2-letter U.S. state or territory code.'
    )

    def convert(self, value):
        value = forms.TextField.convert(self, value)
        value = value.upper()
        if value not in states.VALID_STATE_CODES:
            raise validators.ValidationError(self.messages['invalid_state'])
        return value

