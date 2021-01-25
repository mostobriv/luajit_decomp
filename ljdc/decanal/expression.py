from ljdc.bytecode.instructions import *
# import ljdc.bytecode.instructions


# Comparison ops                 ? 
# Unary Test and Copy ops        ? 
# Unary ops                      Done
# Binary ops                     Done
# Constant ops                   Done
# Upvalue and Function ops       ?
# Table ops                      Almost (TGETM, TSETM, TGETR, TSETR)
# Calls and Vararg Handling      ?
# Returns                        Almost (RETM)
# Loops and branches             ?


class VariableSlot:
    def __init__(self, slot_number):
        self.slot_number = slot_number

    def __str__(self):
        return 'var_%d' % self.slot_number


class PrimitiveType: 
    def __init__(self, primitive_type):
        self.primitive_type = primitive_type

    def __str__(self):
        if self.primitive_type == 0:
            return 'nil'
        elif self.primitive_type == 1:
            return 'true'
        elif self.primitive_type == 2:
            return 'false'
        else:
            raise TypeError('Unknown primitive type')

# atm, this is just dummy class for treating global variable name not as regular string
class GlobalVariable:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

# strings stored as it is, just "blablabla"
class StringType:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# tables stored as list(list, dict)
class TableType:
    def __init__(self, value):
        self.array = value[0]
        self.dictionary = value[1]

    def __str__(self):
        # TODO: idk how to fix it atm, but having 0-slot filled up with stub pretty useful i think
        if len(self.array) != 0 and self.array[0] is None:
            self.array = self.array[1:]

        array_part = ', '.join([repr(item) for item in self.array])
        dictionary_part = ', '.join(['%s="%s"' % (key, value) for key, value in self.dictionary.items()])

        return '{%s}' % ''.join((array_part, dictionary_part))




# MOV dst var Copy D to A
# NOT dst var Set A to boolean not of D
# UNM dst var Set A to -D (unary minus)
# LEN dst var Set A to #D (object length)


def build_unary_expression(proto, instruction):
    operation_to_sign = {
        MOV: '',
        NOT: 'not ',
        UNM: '-',
        LEN: '#'
    }

    destination = VariableSlot(instruction.A)
    source = VariableSlot(instruction.CD)

    return UnaryExpression(destination, source, operation_to_sign[instruction.ins])

class UnaryExpression:
    def __init__(self, destination, source, sign, note=None):
        self.destination = destination
        self.source = source
        self.sign = sign
        self.note = note

    def __str__(self):
        return '%s = %s%s' % (self.destination, self.source, self.sign)


def build_binary_expression(proto, instruction):
    operation_to_sign = {
        ADDVN: '+',
        ADDNV: '+',
        ADDVV: '+',

        SUBVN: '-',
        SUBNV: '-',
        SUBVV: '-',

        MULVN: '*',
        MULNV: '*',
        MULVV: '*',

        DIVVN: '/',
        DIVNV: '/',
        DIVVV: '/',

        MODNV: '%',
        MODVN: '%',
        MODVV: '%',

        CAT: '~'
    }
    destination = VariableSlot(instruction.A)

    if instruction.ins in [ADDVN, SUBVN, MULVN, DIVVN, MODVN]:
        first_operand = VariableSlot(instruction.B)
        second_operand = retrieve_number(proto, instruction.CD)

    elif instruction.ins in [ADDNV, SUBNV, MULNV, DIVNV, MODNV]:
        first_operand = retrieve_number(proto, instruction.B)
        second_operand = VariableSlot(instruction.CD)

    elif instruction.ins in [ADDVV, SUBVV, MULVV, DIVVV, MODVV]:
        first_operand = VariableSlot(instruction.B)
        second_operand = VariableSlot(instruction.CD)

    elif instruction.ins == CAT:
        operands = [VariableSlot(slot_number) for slot_number in range(instruction.B, instruction.CD)]
        return ConcatenateExpression(destination, operands, operation_to_sign[instruction.ins])


    return BinaryExpression(destination, first_operand, second_operand, operation_to_sign[instruction.ins])


class ConcatenateExpression:
    def __init__(self, destination, operands, note=None):
        self.destination = destination
        self.operands = operands
        self.note = note

    def __str__(self):
        right_hand = ' ~ '.join([str(self.operands) for op in operands])
        return '%s = %s' % (self.destination, right_hand)


class BinaryExpression:
    def __init__(self, destination, first_operand, second_operand, sign, note=None):
        self.note = None
        self.destination = destination
        self.first_operand = first_operand
        self.second_operand = second_operand
        self.sign = sign

    def __str__(self):
        return '%s = %s %s %s' % (self.first_operand, self.sign, self.second_operands)



# KSTR    dst str       Set A to string constant D
# KCDATA  dst cdata     Set A to cdata constant D
# KSHORT  dst lits      Set A to 16 bit signed integer D
# KNUM    dst num       Set A to number constant D
# KPRI    dst pri       Set A to primitive D
# KNIL    base    base  Set slots A to D to nil


def build_const_expression(proto, instruction):
    if instruction.ins == KNIL:
        # TODO: make sure that it's [B:D] or [B:D)
        destination = [VariableSlot() for slot_number in range(instruction.B, instruction.CD)]
        source = PrimitiveType(0) # 0 - nil


    elif instruction.ins == KSTR:
        destination = VariableSlot(instruction.A)
        source = StringType(retrieve_string_from_proto(proto, instruction.CD))

    # TODO: добавить обработку CDATA
    elif instruction.ins == KCDATA:
        pass

    elif instruction.ins == KSHORT:
        destination = VariableSlot(instruction.A)
        source = util.as_sign_int16(instruction.B)

    elif instruction.ins == KNUM:
        destination = VariableSlot(instruction.A)
        source = retrieve_number(proto, instruction.CD)

    elif instruction.ins == KPRI:
        destination = VariableSlot(instruction.A)
        try:
            source = PrimitiveType(instruction.CD)
        except TypeError:
             # TODO: как-то пофиксить надо это что ли, а то чот тупо возвращать None не кошерно
            return None

    return ConstExpression(destination, source)


# 1 - если всратый KNIL первой инструкцией в функе, то можно его тупо игнорить
class ConstExpression(object):
    def __init__(self, destination, source, note=None):
        self.destination = destination
        self.source = source
        self.note = note

    def __str__(self):
        if self.destination == list:
            left_hand = ', '.join([str(var) for var in self.destination])
            right_hand = ', '.join([source for _ in range(len(self.destination))])

        else:
            left_hand = self.destination
            right_hand = self.source

        return '%s = %s' % (left_hand, right_hand)


# RETM      base    lit return A, ..., A+D+MULTRES-1
# RET       rbase   lit return A, ..., A+D-2
# RET0      rbase   lit return
# RET1      rbase   lit return A

def build_return_expression(proto, instruction):
    if instruction.ins == RET:
        sources = [VariableSlot(slot_number) for slot_number in range(instruction.A, instruction.A+instruction.D-2)]

    elif instruction.ins == RET0:
        source = []

    elif instruction.ins == RET1:
        source = [VariableSlot(instruction.A)]

    elif instruction.ins == RETM:
        return None

    return ReturnExpression(source)



class ReturnExpression:
    def __init__(self, source, note=None):
        self.source = source
        self.note = note

    def __str__(self):
        return 'return %s' % (', '.join([str(result) for result in self.source]))



# UGET    dst uv  Set A to upvalue D
# USETV   uv  var Set upvalue A to D
# USETS   uv  str Set upvalue A to string constant D
# USETN   uv  num Set upvalue A to number constant D
# USETP   uv  pri Set upvalue A to primitive D
# UCLO    rbase   jump    Close upvalues for slots ≥ rbase and jump to target D
# FNEW    dst func    Create new closure from prototype D and store it in A

def build_upvalue_expression(proto, instruction):
    pass


class UpvalueExpression:
    def __init__(self, ins):
        pass


def _retrieve_constant_from_proto(proto, index):
    return proto.pdata.constant_table[len(proto.pdata.constant_table) - index - 1]


def retrieve_table_from_proto(proto, index):
    constant = _retrieve_constant_from_proto(proto, index)
    return TableType(constant.value)

def retrieve_string_from_proto(proto, index):
    constant = _retrieve_constant_from_proto(proto, index)
    return constant.value


def build_table_expression(proto, instruction):
    if instruction.ins == TNEW:
        destination = VariableSlot(instruction.A)
        source = TableType(([], {}))
        return TableAssignmentExpression() # add `table.setn(tab, instruction.CD)` or smthing like that, but idk mb there is no need in it

    elif instruction.ins == TDUP:
        destination = VariableSlot(instruction.A)
        source = retrieve_table_from_proto(proto, instruction.CD)
        return TableAssignmentExpression(destination, source)

    elif instruction.ins in [TGETV, TGETS, TGETB]:
        destination = VariableSlot(instruction.A)
        source = VariableSlot(instruction.B)

        if instruction.ins == TGETV:
            index = VariableSlot(instruction.CD)
        
        elif instruction.ins == TGETS:
            index = StringType(retrieve_string_from_proto(proto, instruction.CD))
        
        elif instruction.ins == TGETB:
            index = instruction.CD

        return TableIndexExpression(destination, source, index)

    elif instruction.ins in [TSETV, TSETS, TSETB, TSETM]:
        destination = VariableSlot(instruction.B)
        source = VariableSlot(instruction.A)

        if instruction.ins == TSETV:
            index = VariableSlot(instruction.CD)
        
        elif instruction.ins == TSETS:
            index = StringType(retrieve_string_from_proto(proto, instruction.CD))
        
        elif instruction.ins == TSETB:
            index = instruction.CD

        elif instruction.ins == TSETM:
            # TODO: add TSETM support
            return None

        return TableIndexExpression(destination, source, index)

    elif instruction.ins in [GGET, GSET]:
        global_variable = GlobalVariable(retrieve_string_from_proto(proto, instruction.CD))
        variable_slot = VariableSlot(instruction.A)

        if instruction.ins == GGET:
            destination = variable_slot
            source = global_variable
        else: # instruction.ins == GSET:
            destination = global_variable
            source = variable_slot

        return GlobalExpression(destination, source)

    return None





# TNEW    dst     lit Set A to new table with size D (see below)
# TDUP    dst     tab Set A to duplicated template table D
class TableAssignmentExpression:
    def __init__(self, destination, source, note=None):
        self.source = source
        self.destination = destination
        self.note = note

    def __str__(self):
        return '%s = %s' % (self.destination, self.source)

# GGET    dst     str A = _G[D]
# GSET    var     str _G[D] = A
class GlobalExpression:
    def __init__(self, destination, source, note=None):
        self.source = source
        self.destination = destination
        self.note = note

    def __str__(self):
        return '%s = %s' % (self.destination, self.source)



# TGETV   dst var var A = B[C]
# TGETS   dst var str A = B[C]
# TGETB   dst var lit A = B[C]

# TSETV   var var var B[C] = A
# TSETS   var var str B[C] = A
# TSETB   var var lit B[C] = A
# TSETM   base        num*    (A-1)[D], (A-1)[D+1], ... = A, A+1, ...
class TableIndexExpression:
    def __init__(self, destination, source, index, note=None):
        self.destination = destination
        self.source = source
        self.index = index
        self.note = note

    def __str__(self):
        return '%s = %s[%s]' % (self.destination, self.source, self.index)

# CALL    base    lit lit Call: A, ..., A+B-2 = A(A+1, ..., A+C-1)
# CALLT   base        lit Tailcall: return A(A+1, ..., A+D-1)

def build_call_expression(proto, instruction):
    if instruction.ins in [CALL, CALLT]:
        destination = [VariableSlot(slot_number) for slot_number in range(instruction.A, instruction.A+instruction.B-2+1)]
        function = VariableSlot(instruction.A)
        arguments = [VariableSlot(slot_number) for slot_number in range(instruction.A+1, instruction.A+instruction.CD-1+1)]
        if instruction.ins == CALL:
            return CallExpression(destination, function, arguments)
        else:
            return ReturnExpression(CallExpression(destination, function, arguments))


class CallExpression:
    def __init__(self, destination, function, source, note=None):
        self.destination = destination
        self.function = function
        self.source = source
        self.note = note

    def __str__(self):
        result = str()
        if len(self.destination) > 0:
            result = '%s = ' % (', '.join([str(d) for d in self.destination]))

        return '%s%s(%s)' % (result, self.function, ', '.join([str(s) for s in self.source]))


class FunctionHeader:
    def __init__(self):
        pass


class FunctionTail:
    def __init__(self):
        pass


# def test_stuff():
#     test_table = ([100, "asdf", 12, 10, 0x2100], {"test_key_0": "test_value_0", "test_key_1": "test_value_1"})
#     print(TableType(test_table))