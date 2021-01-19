import ctypes


def as_sign_int32(val):
    return ctypes.c_int32(val).value

def as_sign_int64(val):
    pass