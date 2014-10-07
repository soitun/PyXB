# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import pyxb_123.binding.generate
import pyxb_123.utils.domutils
from xml.dom import Node

import os.path
xst = u'''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
 <xs:complexType name="XsdWithHyphens">
    <xs:sequence>
        <xs:element name="username" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>
  <xs:element name="xsd-with-hyphens" type="XsdWithHyphens"/>
</xs:schema>
'''

code = pyxb_123.binding.generate.GeneratePython(schema_text=xst)
#print code

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb_123.exceptions_ import *

import unittest

class TestTrac0203 (unittest.TestCase):
    def testBasic (self):
        unbound = XsdWithHyphens('name')
        with self.assertRaises(pyxb_123.UnboundElementError) as cm:
            unbound.toxml('utf-8', root_only=True)
        e = cm.exception
        self.assertEqual(e.instance, unbound)
        self.assertEqual('Instance of type XsdWithHyphens has no bound element for start tag', str(e))

if __name__ == '__main__':
    unittest.main()
