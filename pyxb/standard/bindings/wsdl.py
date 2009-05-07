from pyxb.standard.bindings.raw.wsdl import *
import pyxb.standard.bindings.raw.wsdl as raw_wsdl

import pyxb.Namespace
import pyxb.utils.domutils as domutils

# Scan for available pre-built namespaces.  The effect of this is to
# register a bunch of namespaces including the path to the module that
# implements them.  This allows the wildcard handler in the content
# model to create proper instances rather than leave them as DOM
# nodes.
pyxb.Namespace.AvailableForLoad()

class _WSDL_binding_mixin (object):
    """Mix-in class to mark element Python bindings that are expected
    to be wildcard matches in WSDL binding elements."""
    pass

class _WSDL_port_mixin (object):
    """Mix-in class to mark element Pythong bindings that are expected
    to bed wildcard matches in WSDL port elements."""
    pass

class tPort (raw_wsdl.tPort):
    def bindingReference (self):
        return self.__bindingReference
    def _setBindingReference (self, binding_reference):
        self.__bindingReference = binding_reference
    __bindingReference = None

    def addressReference (self):
        return self.__addressReference
    def _setAddressReference (self, address_reference):
        self.__addressReference = address_reference
    __addressReference = None
raw_wsdl.tPort._SetClassRef(tPort)

class tBinding (raw_wsdl.tBinding):
    def portTypeReference (self):
        return self.__portTypeReference
    def setPortTypeReference (self, port_type_reference):
        self.__portTypeReference = port_type_reference
    __portTypeReference = None

    def protocolBinding (self):
        """Return the protocol-specific binding information."""
        return self.__protocolBinding
    def _setProtocolBinding (self, protocol_binding):
        self.__protocolBinding = protocol_binding
    __protocolBinding = None

    def operationMap (self):
        return self.__operationMap
    __operationMap = None

    def __init__ (self, *args, **kw):
        super(tBinding, self).__init__(*args, **kw)
        self.__operationMap = { }
raw_wsdl.tBinding._SetClassRef(tBinding)

class tPortType (raw_wsdl.tPortType):
    def operationMap (self):
        return self.__operationMap
    __operationMap = None

    def __init__ (self, *args, **kw):
        super(tPortType, self).__init__(*args, **kw)
        self.__operationMap = { }
raw_wsdl.tPortType._SetClassRef(tPortType)

class tParam (raw_wsdl.tParam):
    def messageReference (self):
        return self.__messageReference
    def _setMessageReference (self, message_reference):
        self.__messageReference = message_reference
    __messageReference = None
raw_wsdl.tParam._SetClassRef(tParam)

class tPart (raw_wsdl.tPart):
    pass
raw_wsdl.tPart._SetClassRef(tPart)

class definitions (raw_wsdl.definitions):
    def messageMap (self):
        return self.__messageMap
    __messageMap = None

    def namespaceData (self):
        return self.__namespaceData
    __namespaceData = None

    def bindingMap (self):
        return self.__bindingMap

    def targetNamespace (self):
        return self.namespaceData().targetNamespace()

    def _addToMap (self, map, qname, value):
        map[qname] = value
        (ns, ln) = qname
        if (ns == self.targetNamespace()):
            map[(None, ln)] = value
        elif (ns is None):
            map[(self.targetNamespace(), ln)] = value
        return map

    @classmethod
    def CreateFromDOM (cls, node, *args, **kw):
        # Get the target namespace and other relevant information, and set the
        # per-node in scope namespaces so we can do QName resolution.
        ns_data = domutils.NamespaceDataFromNode(node)
        rv = super(definitions, cls).CreateFromDOM(node, *args, **kw)
        rv.__namespaceData = ns_data
        rv.__buildMaps()
        return rv

    def __buildMaps (self):
        self.__messageMap = { }
        for m in self.message():
            name_qname = domutils.InterpretQName(m._domNode(), m.name())
            self._addToMap(self.__messageMap, name_qname, m)
        self.__portTypeMap = { }
        for pt in self.portType():
            port_type_qname = domutils.InterpretQName(pt._domNode(), pt.name())
            self._addToMap(self.__portTypeMap, port_type_qname, pt)
            for op in pt.operation():
                pt.operationMap()[op.name()] = op
                for p in (op.input() + op.output() + op.fault()):
                    msg_qname = domutils.InterpretQName(m._domNode(), p.message())
                    p._setMessageReference(self.__messageMap[msg_qname])
        self.__bindingMap = { }
        for b in self.binding():
            binding_qname = domutils.InterpretQName(b._domNode(), b.name())
            self._addToMap(self.__bindingMap, binding_qname, b)
            port_type_qname = domutils.InterpretQName(b._domNode(), b.type())
            b.setPortTypeReference(self.__portTypeMap[port_type_qname])
            for wc in b.wildcardElements():
                if isinstance(wc, _WSDL_binding_mixin):
                    b._setProtocolBinding(wc)
                    break
            for op in b.operation():
                b.operationMap()[op.name()] = op
        self.__serviceMap = { }
        for s in self.service():
            service_qname = domutils.InterpretQName(s._domNode(), s.name())
            self._addToMap(self.__serviceMap, service_qname, s)
            port_map = { }
            for p in s.port():
                port_qname = domutils.InterpretQName(p._domNode(), p.name())
                port_map[port_qname] = p
                binding_qname = domutils.InterpretQName(p._domNode(), p.binding())
                p._setBindingReference(self.__bindingMap[binding_qname])
                for wc in p.wildcardElements():
                    if isinstance(wc, _WSDL_port_mixin):
                        p._setAddressReference(wc)
                        break


raw_wsdl.definitions._SetClassRef(definitions)