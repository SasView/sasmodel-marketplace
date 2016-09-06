import re
from django.core.validators import RegexValidator

validate_comma_separated_float_list = RegexValidator(
    re.compile('^([-+]?\d*\.?\d+[,\s]*)+$'),
    u"Must be a list of comma separated float values", 'invalid'
)
