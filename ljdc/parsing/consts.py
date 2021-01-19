# global dump flags
BCDUMP_F_BE     = 0x01
BCDUMP_F_STRIP  = 0x02
BCDUMP_F_FFI    = 0x04
BCDUMP_F_FR2    = 0x08


# complex constants type
BCDUMP_KGC_CHILD    = 0x0 # Done
BCDUMP_KGC_TAB      = 0x1 # In progress
BCDUMP_KGC_I64      = 0x2 # Done
BCDUMP_KGC_U64      = 0x3 # Done
BCDUMP_KGC_COMPLEX  = 0x4 # Done
BCDUMP_KGC_STR      = 0x5 # Done


# table fields type

BCDUMP_KTAB_NIL     = 0x0 # Done
BCDUMP_KTAB_FALSE   = 0x1 # Done
BCDUMP_KTAB_TRUE    = 0x2 # Done
BCDUMP_KTAB_INT     = 0x3 #
BCDUMP_KTAB_NUM     = 0x4 #
BCDUMP_KTAB_STR     = 0x5 # Done