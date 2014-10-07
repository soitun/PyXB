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
  <xs:complexType name="BaseT" abstract="true"/>
  <xs:complexType name="ChildT">
     <xs:complexContent>
        <xs:extension base="BaseT">
           <xs:sequence>
             <xs:element name="kid" type="xs:string"/>
           </xs:sequence>
        </xs:extension>
     </xs:complexContent>
  </xs:complexType>

  <xs:element name="NotAType" type="xs:string"/>
  <xs:element name="Child">
     <xs:complexContent>
        <xs:extension base="BaseT">
           <xs:sequence minOccurs="0">
             <xs:element name="kid2" type="xs:string"/>
           </xs:sequence>
        </xs:extension>
     </xs:complexContent>
  </xs:element>

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

class TestTrac_0056 (unittest.TestCase):
    def testNonType (self):
        xmls = '<Child xsi:type="NotAType" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>'
        self.assertRaises(pyxb_123.BadDocumentError, CreateFromDocument, xmls)
        doc = pyxb_123.utils.domutils.StringToDOM(xmls)
        self.assertRaises(pyxb_123.BadDocumentError, CreateFromDOM, doc)

    def testAnonymousBase (self):
        xmls = '<Child xsi:type="ChildT" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>'
        #self.assertRaises(pyxb_123.BadDocumentError, CreateFromDocument, xmls)
        doc = pyxb_123.utils.domutils.StringToDOM(xmls)
        self.assertRaises(pyxb_123.ValidationError, CreateFromDOM, doc)


if __name__ == '__main__':
    unittest.main()
