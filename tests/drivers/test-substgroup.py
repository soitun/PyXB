# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import pyxb_123
import pyxb_123.binding.generate
import pyxb_123.utils.domutils
import pyxb_123.binding.saxer
import io

from xml.dom import Node

import os.path
schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schemas/substgroup.xsd'))
code = pyxb_123.binding.generate.GeneratePython(schema_location=schema_path)

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb_123.exceptions_ import *

import unittest

class TestSubstGroup (unittest.TestCase):
    def testISO8601 (self):
        xmlt = u'<when><ISO8601>2009-06-15T17:50:00Z</ISO8601></when>'
        xmld = xmlt.encode('utf-8')
        dom = pyxb_123.utils.domutils.StringToDOM(xmlt)
        instance = CreateFromDOM(dom.documentElement)
        self.assertEqual(instance.sgTime._element(), ISO8601)
        self.assertEqual(instance.toDOM().documentElement.toxml("utf-8"), xmld)

        saxer = pyxb_123.binding.saxer.make_parser(fallback_namespace=Namespace)
        handler = saxer.getContentHandler()
        saxer.parse(io.StringIO(xmlt))
        instance = handler.rootObject()
        self.assertEqual(instance.sgTime._element(), ISO8601)
        self.assertEqual(instance.toDOM().documentElement.toxml("utf-8"), xmld)

    def testPairTime (self):
        xmlt = u'<when><pairTime><seconds>34.0</seconds><fractionalSeconds>0.21</fractionalSeconds></pairTime></when>'
        xmld = xmlt.encode('utf-8')
        dom = pyxb_123.utils.domutils.StringToDOM(xmlt)
        instance = CreateFromDOM(dom.documentElement)
        self.assertEqual(instance.sgTime._element(), pairTime)
        self.assertEqual(instance.sgTime.seconds, 34)
        self.assertEqual(instance.toDOM().documentElement.toxml("utf-8"), xmld)

        saxer = pyxb_123.binding.saxer.make_parser(fallback_namespace=Namespace)
        handler = saxer.getContentHandler()
        saxer.parse(io.StringIO(xmlt))
        instance = handler.rootObject()
        self.assertEqual(instance.sgTime._element(), pairTime)
        self.assertEqual(instance.sgTime.seconds, 34)
        self.assertEqual(instance.toDOM().documentElement.toxml("utf-8"), xmld)


    def testSGTime (self):
        xmlt = u'<when><sgTime>2009-06-15T17:50:00Z</sgTime></when>'
        xmld = xmlt.encode('utf-8')
        dom = pyxb_123.utils.domutils.StringToDOM(xmlt)
        self.assertRaises(pyxb_123.AbstractElementError, CreateFromDOM, dom.documentElement)

        saxer = pyxb_123.binding.saxer.make_parser(fallback_namespace=Namespace)
        handler = saxer.getContentHandler()
        self.assertRaises(pyxb_123.AbstractElementError, saxer.parse, io.StringIO(xmlt))

        xmlt = u'<sgTime>2009-06-15T17:50:00Z</sgTime>'
        xmld = xmlt.encode('utf-8')
        dom = pyxb_123.utils.domutils.StringToDOM(xmlt)
        self.assertRaises(pyxb_123.AbstractElementError, CreateFromDOM, dom.documentElement)
        self.assertRaises(pyxb_123.AbstractElementError, saxer.parse, io.StringIO(xmlt))

        xmlt = u'<ISO8601>2009-06-15T17:50:00Z</ISO8601>'
        xmld = xmlt.encode('utf-8')
        dom = pyxb_123.utils.domutils.StringToDOM(xmlt)
        instance = CreateFromDOM(dom.documentElement)
        self.assertEqual(instance._element(), ISO8601)
        saxer.parse(io.StringIO(xmlt))
        instance = handler.rootObject()
        self.assertEqual(instance._element(), ISO8601)

    def testGenAbstract (self):
        xmlt = u'<when><pairTime><seconds>34.0</seconds><fractionalSeconds>0.21</fractionalSeconds></pairTime></when>'
        xmld = xmlt.encode('utf-8')
        instance = when(pairTime(34.0, 0.21))
        self.assertEqual(instance.sgTime._element(), pairTime)
        self.assertEqual(instance.sgTime.seconds, 34)
        self.assertEqual(instance.toDOM().documentElement.toxml("utf-8"), xmld)
        # Loss of element association kills DOM generation
        instance.sgTime._setElement(None)
        self.assertRaises(pyxb_123.AbstractElementError, instance.toDOM)
        self.assertRaises(pyxb_123.AbstractElementError, sgTime)

if __name__ == '__main__':
    unittest.main()


