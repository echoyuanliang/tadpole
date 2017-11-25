# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from collections import OrderedDict
from flask import current_app
from app.lib.exceptions import ValidationError, InternalError


class Validator(object):

    def __init__(self, validator):
        self.validator = validator
        self.validate_chain = OrderedDict([
            ('required', self.process_required),
            ('nonempty', self.process_nonempty),
            ('types', self.process_types),
            ('oneof', self.process_oneof),
            ('unique', self.process_unique),  # can only do unique for list of hashable objects
            ('length', self.process_length),
            ('override', self.process_override),
            ('default', self.process_default),
            ('custom', self.process_custom)  # validate data logic
        ])

    def process_required(self, data):
        required = self.validator['required']
        not_supply = frozenset(required) - frozenset(data.keys())
        if not_supply:
            raise ValidationError(u'param %s is required' % u','.join(not_supply))

        return True

    def process_nonempty(self, data):
        no_empty = self.validator['nonempty']
        for k in no_empty:
            if not data.get(k, None):
                raise ValidationError(u'param {0} required not empty'.format(k))

        return True

    def process_types(self, data):
        types = self.validator['types']

        for key, tp in types.items():
            if key in data and not isinstance(data[key], tp):
                raise ValidationError(u'param {0} need to be type {1}, your type is {2}'
                                      .format(key, tp, type(data[key])))

        return True

    def process_unique(self, data):
        unique_params = self.validator['unique']

        for k in unique_params:
            if k in data:
                data[k] = list(frozenset(k))

        return True

    def process_length(self, data):
        length = self.validator['length']
        for key, ll in length.items():
            if key not in data:
                continue

            val_len = len(data[key])

            if val_len < ll[0] or val_len > ll[-1]:
                raise ValidationError(u'param {0} length required to between {1} and {2}, '
                                      u'your length is {3}'.format(key, ll[0], ll[-1], val_len))

        return True

    def process_oneof(self, data):
        oneof = self.validator['oneof']

        for key, option_values in oneof.items():
            if key in data and data[key] not in option_values:
                raise ValidationError(u'param {0} must in {1}, your value is {2}'.format(
                    key, u','.join(option_values), data[key]
                ))

        return True

    def process_override(self, data):
        override = self.validator['override']
        for key, override_fn in override.items():
            if key in data:
                try:
                    data[key] = override_fn(key, data[key])
                except Exception as e:
                    current_app.logger.exception(u'process override with key={0}, value={1}, error: {2}'.format(
                        key, data[key], str(e)))

                    raise InternalError(u'oops, validate param occurs internal error')

        return True

    def process_default(self, data):
        default_args = self.validator['default']

        for k, v in default_args.items():
            data.setdefault(k, v)

        return True

    def process_custom(self, data):
        custom = self.validator['custom']

        for validate_fn in custom:
            validate_fn(data)

    def __call__(self, data):
        for validate_name, validate_fn in self.validate_chain.items():
            if validate_name in self.validator:
                validate_fn(data)
