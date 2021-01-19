from ljdc.logger.logger import Logger
from ljdc.parsing.stream import RawStream
import ljdc.parsing.consts as consts
import ljdc.parsing.utils as utils


from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


class AbstractStructure:
    '''
    For future purposes
    '''

    def __init__(self):
        pass


'''
dump   = header proto+ 0U
header = ESC 'L' 'J' versionB flagsU [namelenU nameB*]
proto  = lengthU pdata
pdata  = phead bcinsW* uvdataH* kgc* knum* [debugB*]
phead  = flagsB numparamsB framesizeB numuvB numkgcU numknU numbcU
         [debuglenU [firstlineU numlineU]]
kgc    = kgctypeU { ktab | (loU hiU) | (rloU rhiU iloU ihiU) | strB* }
knum   = intU0 | (loU1 hiU)
ktab   = narrayU nhashU karray* khash*
karray = ktabk
khash  = ktabk ktabk
ktabk  = ktabtypeU { intU | (loU hiU) | strB* }
'''

class Dump(AbstractStructure):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__()
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

        self._read()

    def _read(self):
        self.header = Header(self._io, self, self._root)
        self.prototypes = list()
        while True:
            proto = Proto(self._io, self, self._root)

            # end of dump is reached
            if proto.length == 0:
                break

            self.prototypes.append(proto)


# header = ESC 'L' 'J' versionB flagsU [namelenU nameB*]
class Header(AbstractStructure):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__()
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

        self._read()


    def _read(self):
        self.magic = self._io.ensure_concrete_bytes([0x1B, 0x4C, 0x4A])
        self.version = self._io.read_byte()
        self.flags = self._io.read_uleb128()

        print('Magic: %s' % self.magic)
        print('Version: %s' % self.version)
        print('Flags: %#x' % self.flags)

        if (self.flags & consts.BCDUMP_F_STRIP) == 0:
            self.namelen = self._io.read_uleb128()
            self.name = self._io.read_string(self.namelen)

            print('Namelen: %#x' % (self.namelen))
            print('Name: "%s"' % (self.name))

# proto  = lengthU pdata
class Proto(AbstractStructure):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__()
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

        self._read()

    def _read(self):
        self.length = self._io.read_uleb128()
        if self.length == 0:
            print('==== END OF DUMP ====')
            return
        else:
            print('Proto.length: %#x' % self.length)

        self.pdata = Pdata(self._io, self, self._root)


# pdata  = phead bcinsW* uvdataH* kgc* knum* [debugB*]
class Pdata(AbstractStructure):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__()
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

        self._read()

    def _read(self):        
        self.phead = Phead(self._io, self, self._root)
        self.instructions = self._io.read_many_dwords(self.phead.num_instructions)
        print('Instructions: %s' % self.instructions)
        self.upvalues = self._io.read_many_words(self.phead.num_upvalues)
        print('Upvalues: %s' % self.upvalues)
        self.complexconstants = [ComplexConstant(self._io, self, self._root) for _ in range(self.phead.num_complexconstants)]
        self.numvericvalues = [read_numeric_value(self._io) for _ in range(self.phead.num_numericvalues)]

        if (self._root.header.flags & consts.BCDUMP_F_STRIP) == 0 and self.phead.debuglen > 0:
            self.debuginfo = self._io.read_many_bytes(self.phead.debuglen)


# phead  = flagsB numparamsB framesizeB numuvB numkgcU numknU numbcU
#          [debuglenU [firstlineU numlineU]]
class Phead(AbstractStructure):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__()
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

        self._read()

    def _read(self):
        self.flags = self._io.read_byte()
        self.num_params = self._io.read_byte()
        self.framesize = self._io.read_byte()
        self.num_upvalues = self._io.read_byte()
        self.num_complexconstants = self._io.read_uleb128()
        self.num_numericvalues = self._io.read_uleb128()
        self.num_instructions = self._io.read_uleb128()

        if (self._root.header.flags & consts.BCDUMP_F_STRIP) == 0:
            self.debuglen = self._io.read_uleb128()
            if self.debuglen > 0:
                self.firstline = self._io.read_uleb128()
                self.lines_count = self._io.read_uleb128()



        print('Phead.flags: %#x' % self.flags)
        print('Phead.num_params: %#x' % self.num_params)
        print('Phead.framesize: %#x' % self.framesize)
        print('Phead.num_upvalues: %#x' % self.num_upvalues)
        print('Phead.num_complexconstants: %#x' % self.num_complexconstants)
        print('Phead.num_numericvalues: %#x' % self.num_numericvalues)
        print('Phead.num_instructions: %#x' % self.num_instructions)

        if hasattr(self, 'debuglen'):
            print('Phead.debuglen: %#x' % self.debuglen)
            if hasattr(self, 'firstline'):
                print('Phead.firstline: %#x' % self.firstline)
                print('Phead.lines_count: %#x' % self.lines_count)


# overwrite this to function too
# kgc    = kgctypeU { ktab | (loU hiU) | (rloU rhiU iloU ihiU) | strB* }
class ComplexConstant(AbstractStructure):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__()
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

        self._read()

    def _read(self):
        tp = self._io.read_uleb128()

        # string
        if tp >= consts.BCDUMP_KGC_STR:
            self.len = tp - consts.BCDUMP_KGC_STR
            self.value = self._io.read_string(self.len)
            self.type = 'string'

            print('ComplexConstant: type(%s) value(%s)' % (self.type, repr(self.value)))

        elif tp == consts.BCDUMP_KGC_CHILD:
            self.value = self._root.prototypes.pop()
            self.type = 'prototype'

            print('ComplexConstant: type(%s) value(%s)' % (self.type, repr(self.value)))
            
        elif tp == consts.BCDUMP_KGC_I64 or tp == consts.BCDUMP_KGC_U64:
            self.value = self._io.read_number()
            self.type = 'number'

            print('Number: type(%s) value(%#x)' % (self.type, repr(self.value)))

        elif tp == consts.BCDUMP_KGC_COMPLEX:
            # (real_part, imaginary_part)
            self.value = (self._io.read_number(), self._io.read_number())
            self.type = 'complex number'

            print('ComplexNumber: type(%s) value(%s)' % (self.type, repr(self.value)))

        elif tp == consts.BCDUMP_KGC_TAB:
            self.value = read_ktab(self._io)
            self.type = 'table'

            print('Table: type(%s) value(%s)' % (self.type, repr(self.value)))

        else:
            assert ValueError('Unknown ComplexConstant type - %#x' % tp)


# ktab   = narrayU nhashU karray* khash*
# karray = ktabk
# khash  = ktabk ktabk
# ktabk  = ktabtypeU { intU | (loU hiU) | strB* }

# knum   = intU0 | (loU1 hiU)
# I think, there is no need in OOP, cuz we just simply can replace values with python's default types
def read_numeric_value(io):
    isnum, lo = io.read_uleb128_33bit()

    if isnum:
        hi = io.read_uleb128()
        value = hi << 32 | lo
    else:
        value = utils.as_sign_int32(lo)

    return value

def read_ktab(io):
    narray = io.read_uleb128()
    nhash = io.read_uleb128()

    _array = list()
    _hash = dict()

    for _ in range(narray):
        _array.append(_read_ktabk(io))

    for _ in range(nhash):
        k = _read_ktabk(io)
        v = _read_ktabk(io)
        _hash[k] = v

    return (_array, _hash)



def _read_ktabk(io):
    tp = io.read_uleb128()
    if tp >= consts.BCDUMP_KTAB_STR:
        length = tp - consts.BCDUMP_KTAB_STR
        return io.read_string(length)

    elif tp == consts.BCDUMP_KTAB_NIL:
        return None

    elif tp == consts.BCDUMP_KTAB_TRUE:
        return True

    elif tp == consts.BCDUMP_KTAB_FALSE:
        return False

    elif tp == consts.BCDUMP_KTAB_INT:
        return utils.as_sign_int32(io.read_uleb128())

    elif tp == consts.BCDUMP_KTAB_NUM:
        lo = io.read_uleb128()
        hi = io.read_uleb128()

        return (hi << 32) | lo

    else:
        assert ValueError('Unknown ktab element type - %#x' % tp)
