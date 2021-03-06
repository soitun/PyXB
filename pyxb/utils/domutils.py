# -*- coding: utf-8 -*-
# Copyright 2009-2013, Peter A. Bigot
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at:
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Functions that support activities related to the Document Object Model."""

import pyxb
import pyxb.namespace
import pyxb.namespace.resolution
import pyxb.utils.saxutils
import pyxb.utils.saxdom
import pyxb.utils.types_
import xml.dom
import logging

_log = logging.getLogger(__name__)

# The DOM implementation to be used for all processing.  Default is whatever
# your Python install uses.  If it's minidom, it should work.
__DOMImplementation = xml.dom.getDOMImplementation()

def GetDOMImplementation ():
    """Return the DOMImplementation object used for pyxb operations.

    This is primarily used as the default implementation when generating DOM
    trees from a binding instance.  It defaults to whatever
    xml.dom.getDOMImplementation() returns in your installation (often
    xml.dom.minidom).  It can be overridden with SetDOMImplementation()."""

    global __DOMImplementation
    return __DOMImplementation

def SetDOMImplementation (dom_implementation):
    """Override the default DOMImplementation object."""
    global __DOMImplementation
    __DOMImplementation = dom_implementation
    return __DOMImplementation

# Unfortunately, the DOMImplementation interface doesn't provide a parser.  So
# abstract this in case somebody wants to substitute a different one.  Haven't
# decided how to express that yet.
def StringToDOM (xml_text, **kw):
    """Convert string to a DOM instance.

    @see: L{pyxb._SetXMLStyle}."""

    xmlt = xml_text
    if pyxb.XMLStyle_minidom == pyxb._XMLStyle:
        parser = pyxb.utils.saxutils.make_parser()
        # minidom.parseString operates on text.  In Python 2, this means don't
        # feed it unicode.  In Python 3 this means don't feed it bytes.
        if isinstance(xmlt, unicode):                #!python3!
            xmlt = xmlt.encode(pyxb._InputEncoding)  #!python3!
#python3:        if isinstance(xmlt, pyxb.utils.types_.DataType):
#python3:            xmlt = xmlt.decode(pyxb._InputEncoding)
        return xml.dom.minidom.parseString(xmlt, parser)
    return pyxb.utils.saxdom.parseString(xml_text, **kw)

def NodeAttribute (node, attribute_ncname, attribute_ns=None):
    """Namespace-aware search for an optional attribute in a node.

    @param attribute_ncname: The local name of the attribute.
    @type attribute_ncname: C{str} or C{unicode}

    @keyword attribute_ns: The namespace of the attribute.  Defaults to None
    since most attributes are not in a namespace.  Can be provided as either a
    L{pyxb.namespace.Namespace} instance, or a string URI.
    @type attribute_ns: C{None} or C{str} or C{unicode} or L{pyxb.namespace.Namespace}

    @return: The value of the attribute, or C{None} if the attribute is not
    present.  (Unless C{None}, the value will always be a (unicode) string.)
    """

    ns_uri = attribute_ns
    if isinstance(attribute_ns, pyxb.namespace.Namespace):
        ns_uri = attribute_ns.uri()
    attr = node.getAttributeNodeNS(ns_uri, attribute_ncname)
    if attr is None:
        return None
    return attr.value

def NodeAttributeQName (node, attribute_ncname, attribute_ns=None):
    """Like L{NodeAttribute} but where the content is a QName that must be
    resolved in the context of the node.

    @param attribute_ncname: as in L{NodeAttribute}
    @keyword attribute_ns: as in L{NodeAttribute}

    @return: The expanded name to which the value of the attribute resolves
    given current namespaces, or C{None} if the attribute is not present
    @rtype: L{pyxb.namespace.ExpandedName}
    """
    attr = NodeAttribute(node, attribute_ncname, attribute_ns)
    if attr is None:
        return None
    nsc = pyxb.namespace.resolution.NamespaceContext.GetNodeContext(node)
    return nsc.interpretQName(attr)

def LocateUniqueChild (node, tag, absent_ok=True, namespace=pyxb.namespace.XMLSchema):
    """Locate a unique child of the DOM node.

    This function returns the sole child of node which is an ELEMENT_NODE
    instance and has a tag consistent with the given tag.  If multiple nodes
    with a matching C{tag} are found, or C{absent_ok} is C{False} and no
    matching tag is found, an exception is raised.

    @param node: An a xml.dom.Node ELEMENT_NODE instance
    @param tag: the NCName of an element in the namespace
    @keyword absent_ok: If C{True} (default), C{None} is returned if no match
    can be found.  If C{False}, an exception is raised if no match can be
    found.
    @keyword namespace: The namespace to which the child element belongs.
    Default is the XMLSchema namespace.
    @rtype: C{xml.dom.Node}

    @raise pyxb.SchemaValidationError: multiple elements are identified
    @raise pyxb.SchemaValidationError: C{absent_ok} is C{False} and no element is identified.
    """
    candidate = None
    for cn in node.childNodes:
        if (xml.dom.Node.ELEMENT_NODE == cn.nodeType) and namespace.nodeIsNamed(cn, tag):
            if candidate:
                raise pyxb.SchemaValidationError('Multiple %s elements nested in %s' % (tag, node.nodeName))
            candidate = cn
    if (candidate is None) and not absent_ok:
        raise pyxb.SchemaValidationError('Expected %s elements nested in %s' % (tag, node.nodeName))
    return candidate

def LocateMatchingChildren (node, tag, namespace=pyxb.namespace.XMLSchema):
    """Locate all children of the DOM node that have a particular tag.

    This function returns a list of children of node which are ELEMENT_NODE
    instances and have a tag consistent with the given tag.

    @param node: An a xml.dom.Node ELEMENT_NODE instance.
    @param tag: the NCName of an element in the namespace, which defaults to the
    XMLSchema namespace.
    @keyword namespace: The namespace to which the child element belongs.
    Default is the XMLSchema namespace.

    @rtype: C{list(xml.dom.Node)}
    """
    matches = []
    for cn in node.childNodes:
        if (xml.dom.Node.ELEMENT_NODE == cn.nodeType) and namespace.nodeIsNamed(cn, tag):
            matches.append(cn)
    return matches

def LocateFirstChildElement (node, absent_ok=True, require_unique=False, ignore_annotations=True):
    """Locate the first element child of the node.


    @param node: An a xml.dom.Node ELEMENT_NODE instance.
    @keyword absent_ok: If C{True} (default), C{None} is returned if no match
    can be found.  If C{False}, an exception is raised if no match can be
    found.
    @keyword require_unique: If C{False} (default), it is acceptable for there
    to be multiple child elements.  If C{True}, presence of multiple child
    elements raises an exception.
    @keyword ignore_annotations: If C{True} (default), annotations are skipped
    wheen looking for the first child element.  If C{False}, an annotation
    counts as an element.
    @rtype: C{xml.dom.Node}

    @raise SchemaValidationError: C{absent_ok} is C{False} and no child
    element was identified.
    @raise SchemaValidationError: C{require_unique} is C{True} and multiple
    child elements were identified
    """

    candidate = None
    for cn in node.childNodes:
        if xml.dom.Node.ELEMENT_NODE == cn.nodeType:
            if ignore_annotations and pyxb.namespace.XMLSchema.nodeIsNamed(cn, 'annotation'):
                continue
            if require_unique:
                if candidate:
                    raise pyxb.SchemaValidationError('Multiple elements nested in %s' % (node.nodeName,))
                candidate = cn
            else:
                return cn
    if (candidate is None) and not absent_ok:
        raise pyxb.SchemaValidationError('No elements nested in %s' % (node.nodeName,))
    return candidate

def HasNonAnnotationChild (node):
    """Return True iff C{node} has an ELEMENT_NODE child that is not an
    XMLSchema annotation node.

    @rtype: C{bool}
    """
    for cn in node.childNodes:
        if (xml.dom.Node.ELEMENT_NODE == cn.nodeType) and (not pyxb.namespace.XMLSchema.nodeIsNamed(cn, 'annotation')):
            return True
    return False

def ExtractTextContent (node):
    """Walk all the children, extracting all text content and
    catenating it into the return value.

    Returns C{None} if no text content (including whitespace) is found.

    This is mainly used to strip comments out of the content of complex
    elements with simple types.

    @rtype: C{unicode} or C{str}
    """
    text = []
    for cn in node.childNodes:
        if xml.dom.Node.TEXT_NODE == cn.nodeType:
            text.append(cn.data)
        elif xml.dom.Node.CDATA_SECTION_NODE == cn.nodeType:
            text.append(cn.data)
        elif xml.dom.Node.COMMENT_NODE == cn.nodeType:
            pass
        else:
            raise pyxb.NonElementValidationError(cn)
    if 0 == len(text):
        return None
    return ''.join(text)

class _BDSNamespaceSupport (object):
    """Class holding information relevant to generating the namespace aspects
    of a DOM instance."""
    # Namespace declarations required on the top element
    __namespaces = None

    # Integer counter to help generate unique namespace prefixes
    __namespacePrefixCounter = None

    def defaultNamespace (self):
        """The registered default namespace.

        @rtype: L{pyxb.namespace.Namespace}
        """
        return self.__defaultNamespace
    __defaultNamespace = None

    def setDefaultNamespace (self, default_namespace):
        """Set the default namespace for the generated document.

        Even if invoked post construction, the default namespace will affect
        the entire document, as all namespace declarations are placed in the
        document root.

        @param default_namespace: The namespace to be defined as the default
        namespace in the top-level element of the document.  May be provided
        as a real namespace, or just its URI.
        @type default_namespace: L{pyxb.namespace.Namespace} or C{str} or
        C{unicode}.
        """

        if isinstance(default_namespace, basestring):
            default_namespace = pyxb.namespace.NamespaceForURI(default_namespace, create_if_missing=True)
        if (default_namespace is not None) and default_namespace.isAbsentNamespace():
            raise pyxb.UsageError('Default namespace must not be an absent namespace')
        self.__defaultNamespace = default_namespace

    def namespacePrefixMap (self):
        """Return a map from Namespace instances to the prefix by which they
        are represented in the DOM document."""
        return self.__namespacePrefixMap.copy()
    __namespacePrefixMap = None

    def declareNamespace (self, namespace, prefix=None, add_to_map=False):
        """Add the given namespace as one to be used in this document.

        @param namespace: The namespace to be associated with the document.
        @type namespace: L{pyxb.namespace.Namespace}

        @keyword prefix: Optional prefix to be used with this namespace.  If
        not provided, a unique prefix is generated or a standard prefix is
        used, depending on the namespace.

        @keyword add_to_map: If C{False} (default), the prefix is not added to
        the namespace prefix map.  If C{True} it is added.  (Often, things
        added to the prefix map are preserved across resets, which is often
        not desired for specific prefix/namespace pairs).

        @todo: ensure multiple namespaces do not share the same prefix
        @todo: provide default prefix in L{pyxb.namespace.Namespace}
        @todo: support multiple prefixes for each namespace
        """
        if not isinstance(namespace, pyxb.namespace.Namespace):
            raise pyxb.UsageError('declareNamespace: must be given a namespace instance')
        if namespace.isAbsentNamespace():
            raise pyxb.UsageError('declareNamespace: namespace must not be an absent namespace')
        if prefix is None:
            prefix = self.__namespaces.get(namespace)
        if prefix is None:
            prefix = self.__namespacePrefixMap.get(namespace)
        if prefix is None:
            prefix = namespace.prefix()
        if prefix is None:
            self.__namespacePrefixCounter += 1
            prefix = 'ns%d' % (self.__namespacePrefixCounter,)
        if prefix == self.__namespaces.get(namespace):
            return prefix
        if prefix in self.__prefixes:
            raise pyxb.LogicError('Prefix %s is already in use' % (prefix,))
        self.__namespaces[namespace] = prefix
        self.__prefixes.add(prefix)
        if add_to_map:
            self.__namespacePrefixMap[namespace] = prefix
        return prefix

    def namespacePrefix (self, namespace, enable_default_namespace=True):
        """Return the prefix to be used for the given namespace.

        This will L{declare <declareNamespace>} the namespace if it has not
        yet been observed.

        @param namespace: The namespace for which a prefix is needed.  If the
        provided namespace is C{None} or an absent namespace, the C{None}
        value will be returned as the corresponding prefix.

        @keyword enable_default_namespace: Normally if the namespace is the default
        namespace C{None} is returned to indicate this.  If this keyword is
        C{False} then we need a namespace prefix even if this is the default.
        """

        if (namespace is None) or namespace.isAbsentNamespace():
            return None
        if isinstance(namespace, basestring):
            namespace = pyxb.namespace.NamespaceForURI(namespace, create_if_missing=True)
        if (self.__defaultNamespace == namespace) and enable_default_namespace:
            return None
        ns = self.__namespaces.get(namespace)
        if ns is None:
            ns = self.declareNamespace(namespace)
        return ns

    def namespaces (self):
        """Return the set of Namespace instances known to this instance."""
        return self.__namespaces

    # Restore the namespace map to its default, which is the undeclared
    # namespace for XML schema instances (C{xsi}
    def __resetNamespacePrefixMap (self):
        self.__namespacePrefixMap = { pyxb.namespace.XMLSchema_instance : 'xsi' }

    def reset (self, prefix_map=False):
        """Reset this instance to the state it was when created.

        This flushes the list of namespaces for the document.  The
        defaultNamespace is not modified."""
        self.__namespaces = { }
        self.__prefixes = set()
        self.__namespacePrefixCounter = 0
        if prefix_map:
            self.__resetNamespacePrefixMap()

    def __init__ (self, default_namespace=None, namespace_prefix_map=None, inherit_from=None):
        """Create a new namespace declaration configuration.

        @keyword default_namespace: Optional L{pyxb.namespace.Namespace}
        instance that serves as the default namespace (applies to unqualified
        names).

        @keyword namespace_prefix_map: Optional map from
        L{pyxb.namespace.Namespace} instances to C{str} values that are to be
        used as the corresponding namespace prefix when constructing
        U{qualified names<http://www.w3.org/TR/1999/REC-xml-names-19990114/#dt-qname>}.

        @keyword inherit_from: Optional instance of this class from which
        defaults are inherited.  Inheritance is overridden by values of other
        keywords in the initializer.
        """
        self.__prefixes = set()
        self.__namespacePrefixCounter = 0
        self.__namespaces = { }
        self.__defaultNamespace = None
        self.__resetNamespacePrefixMap()
        if inherit_from is not None:
            if default_namespace is None:
                default_namespace = inherit_from.defaultNamespace()
            self.__namespacePrefixMap.update(inherit_from.__namespacePrefixMap)
            self.__namespacePrefixCount = inherit_from.__namespacePrefixCounter
            self.__namespaces.update(inherit_from.__namespaces)
            self.__prefixes.update(inherit_from.__prefixes)
        if default_namespace is not None:
            self.setDefaultNamespace(default_namespace)
        prefixes = set(self.__namespacePrefixMap.itervalues())
        prefixes.update(self.__prefixes)
        if namespace_prefix_map is not None:
            prefixes = set()
            for (ns, pfx) in namespace_prefix_map.iteritems():
                ns = pyxb.namespace.NamespaceInstance(ns)
                if pfx in prefixes:
                    raise pyxb.LogicError('Cannot assign same prefix to multiple namespacess: %s' % (pfx,))
                prefixes.add(pfx)
                self.__namespacePrefixMap[ns] = pfx

class BindingDOMSupport (object):
    """This holds DOM-related information used when generating a DOM tree from
    a binding instance."""

    def implementation (self):
        """The DOMImplementation object to be used.

        Defaults to L{pyxb.utils.domutils.GetDOMImplementation()}, but can be
        overridden in the constructor call using the C{implementation}
        keyword."""
        return self.__implementation
    __implementation = None

    def document (self):
        """Return the document generated using this instance."""
        return self.__document
    __document = None

    def requireXSIType (self):
        """Indicates whether {xsi:type<http://www.w3.org/TR/xmlschema-1/#xsi_type>} should be added to all elements.

        Certain WSDL styles and encodings seem to require explicit notation of
        the type of each element, even if it was specified in the schema.

        This value can only be set in the constructor."""
        return self.__requireXSIType
    __requireXSIType = None

    def reset (self, **kw):
        """Reset this instance to the state it was when created.

        This creates a new root document with no content, and flushes the list
        of namespaces for the document.  The defaultNamespace and
        requireXSIType are not modified."""
        self.__document = self.implementation().createDocument(None, None, None)
        self.__namespaceSupport.reset(**kw)

    @classmethod
    def Reset (cls, **kw):
        """Reset the global defaults for default/prefix/namespace informmation."""
        cls.__NamespaceSupport.reset(**kw)

    def __init__ (self, implementation=None, default_namespace=None, require_xsi_type=False, namespace_prefix_map=None):
        """Create a new instance used for building a single document.

        @keyword implementation: The C{xml.dom} implementation to use.
        Defaults to the one selected by L{GetDOMImplementation}.

        @keyword default_namespace: The namespace to configure as the default
        for the document.  If not provided, there is no default namespace.
        @type default_namespace: L{pyxb.namespace.Namespace}

        @keyword require_xsi_type: If C{True}, an U{xsi:type
        <http://www.w3.org/TR/xmlschema-1/#xsi_type>} attribute should be
        placed in every element.
        @type require_xsi_type: C{bool}

        @keyword namespace_prefix_map: A map from pyxb.namespace.Namespace
        instances to the preferred prefix to use for the namespace in xmlns
        declarations.  The default one assigns 'xsi' for the XMLSchema
        instance namespace.
        @type namespace_prefix_map: C{map} from L{pyxb.namespace.Namespace} to C{str}

        @raise pyxb.LogicError: the same prefix is associated with multiple
        namespaces in the C{namespace_prefix_map}.

        """
        if implementation is None:
            implementation = GetDOMImplementation()
        self.__implementation = implementation
        self.__requireXSIType = require_xsi_type
        self.__namespaceSupport = _BDSNamespaceSupport(default_namespace, namespace_prefix_map, inherit_from=self.__NamespaceSupport)
        self.reset()

    __namespaceSupport = None
    __NamespaceSupport = _BDSNamespaceSupport()

    # Namespace declarations required on the top element
    def defaultNamespace (self):
        """The default namespace for this instance"""
        return self.__namespaceSupport.defaultNamespace()
    @classmethod
    def DefaultNamespace (cls):
        """The global default namespace (used on instance creation if not overridden)"""
        return cls.__NamespaceSupport.defaultNamespace()

    def setDefaultNamespace (self, default_namespace):
        return self.__namespaceSupport.setDefaultNamespace(default_namespace)
    @classmethod
    def SetDefaultNamespace (cls, default_namespace):
        return cls.__NamespaceSupport.setDefaultNamespace(default_namespace)

    def declareNamespace (self, namespace, prefix=None):
        """Declare a namespace within this instance only."""
        return self.__namespaceSupport.declareNamespace(namespace, prefix, add_to_map=True)
    @classmethod
    def DeclareNamespace (cls, namespace, prefix=None):
        """Declare a namespace that will be added to each created instance."""
        return cls.__NamespaceSupport.declareNamespace(namespace, prefix, add_to_map=True)

    def namespacePrefix (self, namespace, enable_default_namespace=True):
        """Obtain the prefix for the given namespace using this instance's configuration."""
        return self.__namespaceSupport.namespacePrefix(namespace, enable_default_namespace)

    def namespacePrefixMap (self):
        """Get the map from namespaces to prefixes for this instance"""
        return self.__namespaceSupport.namespacePrefixMap().copy()
    @classmethod
    def NamespacePrefixMap (cls):
        """Get the map of default namespace-to-prefix mappings"""
        return cls.__NamespaceSupport.namespacePrefixMap().copy()

    def addAttribute (self, element, expanded_name, value):
        """Add an attribute to the given element.

        @param element: The element to which the attribute should be added
        @type element: C{xml.dom.Element}
        @param expanded_name: The name of the attribute.  This may be a local
        name if the attribute is not in a namespace.
        @type expanded_name: L{pyxb.namespace.Namespace} or C{str} or C{unicode}
        @param value: The value of the attribute
        @type value: C{str} or C{unicode}
        """
        name = expanded_name
        namespace = None
        if isinstance(name, pyxb.namespace.ExpandedName):
            name = expanded_name.localName()
            namespace = expanded_name.namespace()
            # Attribute names do not use default namespace
            prefix = self.namespacePrefix(namespace, enable_default_namespace=False)
            if prefix is not None:
                name = '%s:%s' % (prefix, name)
        element.setAttributeNS(namespace, name, value)

    def finalize (self):
        """Do the final cleanup after generating the tree.  This makes sure
        that the document element includes XML Namespace declarations for all
        namespaces referenced in the tree.

        @return: The document that has been created.
        @rtype: C{xml.dom.Document}"""
        ns = self.__namespaceSupport.defaultNamespace()
        if ns is not None:
            self.document().documentElement.setAttributeNS(pyxb.namespace.XMLNamespaces.uri(), 'xmlns', ns.uri())
        for ( ns, pfx ) in self.__namespaceSupport.namespaces().iteritems():
            assert pfx is not None
            self.document().documentElement.setAttributeNS(pyxb.namespace.XMLNamespaces.uri(), 'xmlns:%s' % (pfx,), ns.uri())
        return self.document()

    def createChildElement (self, expanded_name, parent=None):
        """Create a new element node in the tree.

        @param expanded_name: The name of the element.  A plain string
        indicates a name in no namespace.
        @type expanded_name: L{pyxb.namespace.ExpandedName} or C{str} or C{unicode}

        @keyword parent: The node in the tree that will serve as the child's
        parent.  If C{None}, the document element is used.  (If there is no
        document element, then this call creates it as a side-effect.)

        @return: A newly created DOM element
        @rtype: C{xml.dom.Element}
        """

        if parent is None:
            parent = self.document().documentElement
        if parent is None:
            parent = self.__document
        if isinstance(expanded_name, (str, unicode)):
            expanded_name = pyxb.namespace.ExpandedName(None, expanded_name)
        if not isinstance(expanded_name, pyxb.namespace.ExpandedName):
            raise pyxb.LogicError('Invalid type %s for expanded name' % (type(expanded_name),))
        ns = expanded_name.namespace()
        name = expanded_name.localName()
        ns_uri = xml.dom.EMPTY_NAMESPACE
        pfx = self.namespacePrefix(ns)
        if pfx is not None:
            ns_uri = ns.uri()
            name = '%s:%s' % (pfx, name)
        element = self.__document.createElementNS(ns_uri, name)
        return parent.appendChild(element)

    def _makeURINodeNamePair (self, node):
        """Convert namespace information from a DOM node to text for new DOM node.

        The namespaceURI and nodeName are extracted and parsed.  The namespace
        (if any) is registered within the document, along with any prefix from
        the node name.  A pair is returned where the first element is the
        namespace URI or C{None}, and the second is a QName to be used for the
        expanded name within this document.

        @param node: An xml.dom.Node instance, presumably from a wildcard match.
        @rtype: C{( str, str )}"""
        ns = None
        if node.namespaceURI is not None:
            ns = pyxb.namespace.NamespaceForURI(node.namespaceURI, create_if_missing=True)
        if node.ELEMENT_NODE == node.nodeType:
            name = node.tagName
        elif node.ATTRIBUTE_NODE == node.nodeType:
            name = node.name
            # saxdom uses the uriTuple as the name field while minidom uses
            # the QName.  @todo saxdom should be fixed.
            if isinstance(name, tuple):
                name = name[1]
        else:
            raise pyxb.UsageError('Unable to determine name from DOM node %s' % (node,))
        pfx = None
        local_name = name
        if 0 < name.find(':'):
            (pfx, local_name) = name.split(':', 1)
            if ns is None:
                raise pyxb.LogicError('QName with prefix but no available namespace')
        ns_uri = None
        node_name = local_name
        if ns is not None:
            ns_uri = ns.uri()
            self.declareNamespace(ns, pfx)
            if pfx is None:
                pfx = self.namespacePrefix(ns)
            if pfx is not None:
                node_name = '%s:%s' % (pfx, local_name)
        return (ns_uri, node_name)

    def _deepClone (self, node, docnode):
        if node.ELEMENT_NODE == node.nodeType:
            (ns_uri, node_name) = self._makeURINodeNamePair(node)
            clone_node = docnode.createElementNS(ns_uri, node_name)
            attrs = node.attributes
            for ai in xrange(attrs.length):
                clone_node.setAttributeNodeNS(self._deepClone(attrs.item(ai), docnode))
            for child in node.childNodes:
                clone_node.appendChild(self._deepClone(child, docnode))
            return clone_node
        if node.TEXT_NODE == node.nodeType:
            return docnode.createTextNode(node.data)
        if node.ATTRIBUTE_NODE == node.nodeType:
            (ns_uri, node_name) = self._makeURINodeNamePair(node)
            clone_node = docnode.createAttributeNS(ns_uri, node_name)
            clone_node.value = node.value
            return clone_node
        if node.COMMENT_NODE == node.nodeType:
            return docnode.createComment(node.data)
        raise ValueError('DOM node not supported in clone', node)

    def cloneIntoImplementation (self, node):
        """Create a deep copy of the node in the target implementation.

        Used when converting a DOM instance from one implementation (e.g.,
        L{pyxb.utils.saxdom}) into another (e.g., L{xml.dom.minidom})."""
        new_doc = self.implementation().createDocument(None, None, None)
        return self._deepClone(node, new_doc)

    def appendChild (self, child, parent):
        """Add the child to the parent.

        @note: If the child and the parent use different DOM implementations,
        this operation will clone the child into a new instance, and give that
        to the parent.

        @param child: The value to be appended
        @type child: C{xml.dom.Node}
        @param parent: The new parent of the child
        @type parent: C{xml.dom.Node}
        @rtype: C{xml.dom.Node}"""

        # @todo This check is incomplete; is there a standard way to find the
        # implementation of an xml.dom.Node instance?
        if isinstance(child, pyxb.utils.saxdom.Node):
            child = self.cloneIntoImplementation(child)
        return parent.appendChild(child)

    def appendTextChild (self, text, parent):
        """Add the text to the parent as a text node."""
        return parent.appendChild(self.document().createTextNode(text))


## Local Variables:
## fill-column:78
## End:

