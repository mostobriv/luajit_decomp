
# From luajit wiki
# (none): unused operand
# var: variable slot number
# dst: variable slot number, used as a destination
# base: base slot number, read-write
# rbase: base slot number, read-only
# uv: upvalue number
# lit: literal
# lits: signed literal
# pri: primitive type (0 = nil, 1 = false, 2 = true)
# num: number constant, index into constant table
# str: string constant, negated index into constant table
# tab: template table, negated index into constant table
# func: function prototype, negated index into constant table
# cdata: cdata constant, negated index into constant table
# jump: branch target, relative to next instruction, biased with 0x8000

# T_NONE  = None
T_VAR   = 1
T_DST   = 2
T_BASE  = 3
T_RBASE = 4
T_UV    = 5
T_LIT   = 6
T_LITS  = 7
T_PRI   = 8
T_NUM   = 9
T_STR   = 10
T_TAB   = 11
T_FUNC  = 12
T_CDATA = 13
T_JUMP  = 14 # TODO: add processing with 0x8000



# This class represent concrete instruction in real dump with concrete args
class Instruction:
    def __init__(self, codeword):
        self.ins = OPCODES[codeword & 0xFF]
        self.codeword = codeword

        self._process()

    def _process(self):

        self.A = (self.codeword >> 8) & 0xFF

        if self.ins.args_count == 3:
            self.B = (self.codeword >> 16) & 0xFF
            self.CD = (self.codeword >> 24) & 0xFF

        else:
            self.CD = (self.codeword >> 16) & 0xFFFF

    def __str__(self):
        return '%8s %d' % (self.ins.mnem, self.A)




# Class for definition of instruction
class BCDef:
    def __init__(self, mnem, A_TYPE, B_TYPE, CD_TYPE):
        self.mnem = mnem

        # do we really need it?
        # self.op

        self.A_TYPE = A_TYPE
        self.B_TYPE = B_TYPE
        self.CD_TYPE = CD_TYPE
        self.args_count = bool(A_TYPE) + bool(B_TYPE) + bool(CD_TYPE)

    # def __call__(self, codeword):
    #     return Instruction(self, codeword)


# Comparison ops
ISLT    = BCDef("ISLT",   T_VAR,  None, T_VAR) # Jump if A < D
ISGE    = BCDef("ISGE",   T_VAR,  None, T_VAR) # Jump if A ≥ D
ISLE    = BCDef("ISLE",   T_VAR,  None, T_VAR) # Jump if A ≤ D
ISGT    = BCDef("ISGT",   T_VAR,  None, T_VAR) # Jump if A > D
ISEQV   = BCDef("ISEQV",  T_VAR,  None, T_VAR) # Jump if A = D
ISNEV   = BCDef("ISNEV",  T_VAR,  None, T_VAR) # Jump if A ≠ D
ISEQS   = BCDef("ISEQS",  T_VAR,  None, T_STR) # Jump if A = D
ISNES   = BCDef("ISNES",  T_VAR,  None, T_STR) # Jump if A ≠ D
ISEQN   = BCDef("ISEQN",  T_VAR,  None, T_NUM) # Jump if A = D
ISNEN   = BCDef("ISNEN",  T_VAR,  None, T_NUM) # Jump if A ≠ D
ISEQP   = BCDef("ISEQP",  T_VAR,  None, T_PRI) # Jump if A = D
ISNEP   = BCDef("ISNEP",  T_VAR,  None, T_PRI) # Jump if A ≠ D


# Unary Test and Copy ops
ISTC    = BCDef("ISTC", T_DST, None, T_VAR) # Copy D to A and jump, if D is true
ISFC    = BCDef("ISFC", T_DST, None, T_VAR) # Copy D to A and jump, if D is false
IST     = BCDef("IST",  None,  None, T_VAR) # Jump if D is true
ISF     = BCDef("ISF",  None,  None, T_VAR) # Jump if D is false


# Unary ops
MOV     = BCDef("MOV", T_DST, None, T_VAR) # Copy D to A
NOT     = BCDef("NOT", T_DST, None, T_VAR) # Set A to boolean not of D
UNM     = BCDef("UNM", T_DST, None, T_VAR) # Set A to -D (unary minus)
LEN     = BCDef("LEN", T_DST, None, T_VAR) # Set A to #D (object length)


# Binary ops
ADDVN   = BCDef("ADDVN",   T_DST, T_VAR, T_NUM)     # A = B + C
SUBVN   = BCDef("SUBVN",   T_DST, T_VAR, T_NUM)     # A = B - C
MULVN   = BCDef("MULVN",   T_DST, T_VAR, T_NUM)     # A = B * C
DIVVN   = BCDef("DIVVN",   T_DST, T_VAR, T_NUM)     # A = B / C
MODVN   = BCDef("MODVN",   T_DST, T_VAR, T_NUM)     # A = B % C
ADDNV   = BCDef("ADDNV",   T_DST, T_VAR, T_NUM)     # A = C + B
SUBNV   = BCDef("SUBNV",   T_DST, T_VAR, T_NUM)     # A = C - B
MULNV   = BCDef("MULNV",   T_DST, T_VAR, T_NUM)     # A = C * B
DIVNV   = BCDef("DIVNV",   T_DST, T_VAR, T_NUM)     # A = C / B
MODNV   = BCDef("MODNV",   T_DST, T_VAR, T_NUM)     # A = C % B
ADDVV   = BCDef("ADDVV",   T_DST, T_VAR, T_VAR)     # A = B + C
SUBVV   = BCDef("SUBVV",   T_DST, T_VAR, T_VAR)     # A = B - C
MULVV   = BCDef("MULVV",   T_DST, T_VAR, T_VAR)     # A = B * C
DIVVV   = BCDef("DIVVV",   T_DST, T_VAR, T_VAR)     # A = B / C
MODVV   = BCDef("MODVV",   T_DST, T_VAR, T_VAR)     # A = B % C
POW     = BCDef("POW",     T_DST, T_VAR, T_RBASE)   # A = B ^ C    
CAT     = BCDef("CAT",     T_DST, T_RBASE, T_RBASE) # A = B .. ~ .. C


# Constant ops
KSTR    = BCDef("KSTR",    T_DST,   None, T_STR)   # Set A to string constant D
KCDATA  = BCDef("KCDATA",  T_DST,   None, T_CDATA) # Set A to cdata constant D
KSHORT  = BCDef("KSHORT",  T_DST,   None, T_LITS)  # Set A to 16 bit signed integer D
KNUM    = BCDef("KNUM",    T_DST,   None, T_NUM)   # Set A to number constant D
KPRI    = BCDef("KPRI",    T_DST,   None, T_PRI)   # Set A to primitive D
KNIL    = BCDef("KNIL",    T_BASE,  None, T_BASE)  # Set slots A to D to nil


# Upvalue and Function ops
UGET    = BCDef("UGET",    T_DST,   None, T_UV)    # Set A to upvalue D    
USETV   = BCDef("USETV",   T_UV,    None, T_VAR)   # Set upvalue A to D
USETS   = BCDef("USETS",   T_UV,    None, T_STR)   # Set upvalue A to string constant D
USETN   = BCDef("USETN",   T_UV,    None, T_NUM)   # Set upvalue A to number constant D
USETP   = BCDef("USETP",   T_UV,    None, T_PRI)   # Set upvalue A to primitive D
UCLO    = BCDef("UCLO",    T_RBASE, None, T_JUMP)  # Close upvalues for slots ≥ rbase and jump to target D
FNEW    = BCDef("FNEW",    T_DST,   None, T_FUNC)  # Create new closure from prototype D and store it in A


# Table ops
TNEW    = BCDef("TNEW",    T_DST, None, T_LIT)     # Set A to new table with size D (see below)
TDUP    = BCDef("TDUP",    T_DST, None, T_TAB)     # Set A to duplicated template table D
GGET    = BCDef("GGET",    T_DST, None, T_STR)     # A = _G[D]
GSET    = BCDef("GSET",    T_VAR, None, T_STR)     # _G[D] = A
TGETV   = BCDef("TGETV",   T_DST, T_VAR, T_VAR)    # A = B[C]
TGETS   = BCDef("TGETS",   T_DST, T_VAR, T_STR)    # A = B[C]
TGETB   = BCDef("TGETB",   T_DST, T_VAR, T_LIT)    # A = B[C]
TSETV   = BCDef("TSETV",   T_VAR, T_VAR, T_VAR)    # B[C] = A
TSETS   = BCDef("TSETS",   T_VAR, T_VAR, T_STR)    # B[C] = A
TSETB   = BCDef("TSETB",   T_VAR, T_VAR, T_LIT)    # B[C] = A

# TODO: think what we can do with (num*) type of argument
# need to process it somehow
TSETM   = BCDef("TSETM",   T_BASE, None, T_NUM)    # (A-1)[D], (A-1)[D+1], ... = A, A+1, ...


# Calls and Vararg Handling
CALLM   = BCDef("CALLM",   T_BASE,  T_LIT,  T_LIT)    # Call: A, ..., A+B-2 = A(A+1, ..., A+C+MULTRES)
CALL    = BCDef("CALL",    T_BASE,  T_LIT,  T_LIT)    # Call: A, ..., A+B-2 = A(A+1, ..., A+C-1)
CALLMT  = BCDef("CALLMT",  T_BASE,  None,   T_LIT)    # Tailcall: return A(A+1, ..., A+D+MULTRES)
CALLT   = BCDef("CALLT",   T_BASE,  None,   T_LIT)    # Tailcall: return A(A+1, ..., A+D-1)
ITERC   = BCDef("ITERC",   T_BASE,  T_LIT,  T_LIT)    # Call iterator: A, A+1, A+2 = A-3, A-2, A-1; A, ..., A+B-2 = A(A+1, A+2)
ITERN   = BCDef("ITERN",   T_BASE,  T_LIT,  T_LIT)    # Specialized ITERC, if iterator function A-3 is next()
VARG    = BCDef("VARG",    T_BASE,  T_LIT,  T_LIT)    # Vararg: A, ..., A+B-2 = ...
ISNEXT  = BCDef("ISNEXT",  T_BASE,  None,   T_JUMP)   # Verify ITERN specialization and jump


# Returns
RETM    = BCDef("RETM",    T_RBASE, None,  T_LIT)        # return A, ..., A+D+MULTRES-1
RET     = BCDef("RET",     T_RBASE, None,  T_LIT)        # return A, ..., A+D-2
RET0    = BCDef("RET0",    T_RBASE, None,  T_LIT)        # return
RET1    = BCDef("RET1",    T_RBASE, None,  T_LIT)        # return A


# Loops and branches
FORI    = BCDef("FORI",    T_BASE,  None,   T_JUMP)    # Numeric 'for' loop init
JFORI   = BCDef("JFORI",   T_BASE,  None,   T_JUMP)    # Numeric 'for' loop init, JIT-compiled
FORL    = BCDef("FORL",    T_BASE,  None,   T_JUMP)    # Numeric 'for' loop
IFORL   = BCDef("IFORL",   T_BASE,  None,   T_JUMP)    # Numeric 'for' loop, force interpreter
JFORL   = BCDef("JFORL",   T_BASE,  None,   T_LIT)     # Numeric 'for' loop, JIT-compiled
ITERL   = BCDef("ITERL",   T_BASE,  None,   T_JUMP)    # Iterator 'for' loop
IITERL  = BCDef("IITERL",  T_BASE,  None,   T_JUMP)    # Iterator 'for' loop, force interpreter
JITERL  = BCDef("JITERL",  T_BASE,  None,   T_LIT)     # Iterator 'for' loop, JIT-compiled
LOOP    = BCDef("LOOP",    T_RBASE, None,   T_JUMP)    # Generic loop
ILOOP   = BCDef("ILOOP",   T_RBASE, None,   T_JUMP)    # Generic loop, force interpreter
JLOOP   = BCDef("JLOOP",   T_RBASE, None,   T_LIT)     # Generic loop, JIT-compiled
JMP     = BCDef("JMP",     T_RBASE, None,   T_JUMP)    # Jump

# Function headers

FUNCF   = BCDef("FUNCF",   T_RBASE, None, None)       # Fixed-arg Lua function
IFUNCF  = BCDef("IFUNCF",  T_RBASE, None, None)       # Fixed-arg Lua function, force interpreter
JFUNCF  = BCDef("JFUNCF",  T_RBASE, None, T_LIT) # Fixed-arg Lua function, JIT-compiled
FUNCV   = BCDef("FUNCV",   T_RBASE, None, None)       # Vararg Lua function
IFUNCV  = BCDef("IFUNCV",  T_RBASE, None, None)       # Vararg Lua function, force interpreter
JFUNCV  = BCDef("JFUNCV",  T_RBASE, None, T_LIT) # Vararg Lua function, JIT-compiled
FUNCC   = BCDef("FUNCC",   T_RBASE, None, None)       # Pseudo-header for C functions
FUNCCW  = BCDef("FUNCCW",  T_RBASE, None, None)       # Pseudo-header for wrapped C functions
FUNC    = BCDef("FUNC",   T_RBASE, None, None)       # Pseudo-header for fast functions



_comparison_opcodes = [
    ISLT,
    ISGE,
    ISLE,
    ISGT,
    ISEQV,
    ISNEV,
    ISEQS,
    ISNES,
    ISEQN,
    ISNEN,
    ISEQP,
    ISNEP
]

_unary_test_and_copy_opcodes = [
    ISTC,
    ISFC,
    IST,
    ISF,
    # ISTYPE,
    # ISNUM
]

_unary_opcodes = [
    MOV,
    NOT,
    UNM,
    LEN
]

_binary_opcodes = [
    ADDVN,
    SUBVN,
    MULVN,
    DIVVN,
    MODVN,
    ADDNV,
    SUBNV,
    MULNV,
    DIVNV,
    MODNV,
    ADDVV,
    SUBVV,
    MULVV,
    DIVVV,
    MODVV,
    POW,
    CAT
]

_constants_opcodes = [
    KSTR,
    KCDATA,
    KSHORT,
    KNUM,
    KPRI,
    KNIL
]

_upvalue_and_function_opcodes = [
    UGET,
    USETV,
    USETS,
    USETN,
    USETP,
    UCLO,
    FNEW
]

_table_opcodes = [
    TNEW,
    TDUP,
    GGET,
    GSET,
    TGETV,
    TGETS,
    TGETB,
    # TGETR,
    TSETV,
    TSETS,
    TSETB,
    TSETM,
    # TSETR
]

_calls_and_vararg_opcodes = [
    CALLM,
    CALL,
    CALLMT,
    CALLT,
    ITERC,
    ITERN,
    VARG,
    ISNEXT
]

_return_opcodes = [
    RETM,
    RET,
    RET0,
    RET1
]

_loops_and_branches_opcodes = [
    FORI,
    JFORI,
    FORL,
    IFORL,
    JFORL,
    ITERL,
    IITERL,
    JITERL,
    LOOP,
    ILOOP,
    JLOOP,
    JMP
]

_function_headers_opcodes = [
    FUNCF,
    IFUNCF,
    JFUNCF,
    FUNCV,
    IFUNCV,
    JFUNCV,
    FUNCC,
    FUNCCW
]


OPCODES = list()
OPCODES.extend(_comparison_opcodes)
OPCODES.extend(_unary_test_and_copy_opcodes)
OPCODES.extend(_unary_opcodes)
OPCODES.extend(_binary_opcodes)
OPCODES.extend(_constants_opcodes)
OPCODES.extend(_upvalue_and_function_opcodes)
OPCODES.extend(_table_opcodes)
OPCODES.extend(_calls_and_vararg_opcodes)
OPCODES.extend(_return_opcodes)
OPCODES.extend(_loops_and_branches_opcodes)
OPCODES.extend(_function_headers_opcodes)