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
xsd='''
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="iopt" nillable="true" type="xs:integer"/>
</xs:schema>
'''

#open('schema.xsd', 'w').write(xsd)
code = pyxb.binding.generate.GeneratePython(schema_text=xsd)
#open('code.py', 'w').write(code)
#print code

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb_123.exceptions_ import *

import unittest

class TestTrac_0058 (unittest.TestCase):
    def testRoundTrip (self):
        xmlt = u'<iopt xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"></iopt>'
        xmld = xmlt.encode('utf-8')
        instance = CreateFromDocument(xmlt)
        self.assertTrue(instance._isNil())
        self.assertEqual(0, instance)
        self.assertEqual('', instance.xsdLiteral())
        self.assertEqual(instance.toxml("utf-8", root_only=True), xmld)

if __name__ == '__main__':
    unittest.main()
