# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)

import pyxb_123.binding.generate
import pyxb_123.binding.datatypes as xs
import pyxb_123.binding.basis
import pyxb_123.utils.domutils

import os.path
xsd=u'''<?xml version="1.0" encoding="utf-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:simpleType name="tEnum">
                <xs:restriction base="xs:token">
                        <xs:enumeration value="°"/> <!-- degree -->
                        <xs:enumeration value="m²"/> <!-- squared -->
                        <xs:enumeration value="m³"/> <!-- cubed -->
                </xs:restriction>
        </xs:simpleType>
</xs:schema>
'''

#open('schema.xsd', 'w').write(xsd)
code = pyxb_123.binding.generate.GeneratePython(schema_text=xsd)
#open('code.py', 'w').write(code)
#print code

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb_123.exceptions_ import *

import unittest

class TestTrac_0088 (unittest.TestCase):
    def test (self):
        enums = tEnum._CF_enumeration.items()
        self.assertEqual(3, len(enums))
        self.assertEqual(enums[0].tag(), 'emptyString')
        self.assertEqual(enums[0].value(), u'°')
        self.assertEqual(enums[1].tag(), 'm')
        self.assertEqual(enums[1].value(), u'm²')
        self.assertEqual(enums[2].tag(), 'm_')
        self.assertEqual(enums[2].value(), u'm³')

if __name__ == '__main__':
    unittest.main()
