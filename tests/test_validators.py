# -*- coding:utf-8 -*-
import unittest2

from libcloud_rest.api import validators
from libcloud_rest.errors import ValidationError, MissingArguments,\
    UnknownArgument


class TestParser(unittest2.TestCase):
    def test_string(self):
        string_validator = validators.StringValidator()
        valid_string = 'abc'
        invalid_type = 123
        self.assertTrue(string_validator(valid_string))
        self.assertRaises(ValidationError, string_validator, invalid_type)

    def test_integer(self):
        integer_validator = validators.IntegerValidator()
        valid_integer = 123
        valid_integer2 = 12.3
        invalid_integer = '12.3'
        self.assertTrue(integer_validator(valid_integer))
        self.assertTrue(integer_validator(valid_integer2))
        self.assertRaises(ValidationError, integer_validator, invalid_integer)
        #test max and min
        max_int_validator = validators.IntegerValidator(max=100, min=0)
        valid_integer = 50
        invalid_integer = -1
        invalid_integer2 = 101
        self.assertTrue(max_int_validator(valid_integer))
        self.assertRaises(ValidationError, max_int_validator, invalid_integer)
        self.assertRaises(ValidationError, max_int_validator, invalid_integer2)

    def test_dict(self):
        dict_validator = validators.DictValidator(
            {'arg1': validators.StringValidator()})
        valid_dict = {'arg1': 'str'}
        invalid_dict = {'arg1': 123}
        invalid_dict2 = {'abc': 'str'}
        self.assertTrue(dict_validator(valid_dict))
        self.assertRaises(ValidationError, dict_validator, invalid_dict)
        self.assertRaises(ValidationError, dict_validator, invalid_dict2)

    def test_required(self):
        req_string_validator = validators.StringValidator()
        not_req_string_validator = validators.StringValidator(required=False)
        dict_validator = validators.DictValidator({
            'req': req_string_validator,
            'opt': not_req_string_validator,
        })
        valid_dict = {'req': 'abc'}
        valid_dict2 = {'req': 'abc', 'opt': 'def'}
        invalid_dict = {'opt': 'def'}
        self.assertTrue(dict_validator(valid_dict))
        self.assertTrue(dict_validator(valid_dict2))
        self.assertRaises(ValidationError, dict_validator, invalid_dict)

    def test_const(self):
        const_validator = validators.ConstValidator({'a': 1})
        valid_data = {'a': 1}
        invalid_data = {'a': '1'}
        self.assertTrue(const_validator(valid_data))
        self.assertRaises(ValidationError, const_validator, invalid_data)

    def test_name(self):
        int_validator = validators.IntegerValidator(name='test')
        invalid_data = 'abc'
        self.assertRaisesRegexp(ValidationError, 'test.*',
                                int_validator, invalid_data)
        dict_validator = validators.DictValidator({
            'test_name': validators.ConstValidator('333')
        })
        self.assertRaisesRegexp(ValidationError, 'test_name .*',
                                dict_validator, {})
        str_validator = validators.StringValidator()
        self.assertRaisesRegexp(ValidationError,
                                '%s .*' % (str_validator.default_name),
                                str_validator, {})

    def test_choices(self):
        choices_valid = validators.ChoicesValidator(['abc', 'cd', 123])
        self.assertTrue(choices_valid('abc'))
        self.assertRaises(ValidationError, choices_valid, 'ab')
        self.assertRaises(TypeError, validators.ChoicesValidator, 123)

    def test_type(self):
        type_validator = validators.TypeValidator(int)
        self.assertTrue(type_validator(123))
        self.assertRaises(ValidationError, type_validator, 'str')

        class A(object):
            pass

        class B(A):
            pass

        class D(object):
            pass

        a_validator = validators.TypeValidator(A)
        self.assertTrue(a_validator(A()))
        self.assertTrue(a_validator(B()))
        self.assertRaises(ValidationError, a_validator, D())
