from ljdc.logger.logger import Logger


class RawStream:
    def __init__(self, filepath):
        self.offset = 0
        self._logger = Logger(self)
        print('Trying to open file: %s' % filepath)
        try:
            with open(filepath, 'rb') as f:
                self.buffer = f.read()
        except Exception as e:
            self._logger.error('An error due opening and reading the %s: %s' % (filepath, e), e)

    def read_byte(self):
        res = self.buffer[self.offset]
        self.offset+= 1

        return res

    def ensure_concrete_bytes(self, excepted):
        for excepted_byte in excepted:
            real_byte = self.read_byte()
            if excepted_byte != real_byte:
                raise Exception('Wrong byte at %#x offset, excepted: %#x, got: %#x' % (self.offset-1, excepted_byte, real_byte))

        return excepted

    def read_many_bytes(self, n):
        return [self.read_byte() for i in range(n)]

    def read_many_dwords(self, n):
        return [self.read_dword() for i in range(n)]

    def read_many_words(self, n):
        return [self.read_word() for i in range(n)]

    def read_word(self):
        res = 0
        for i in range(2):
            res|= self.read_byte() << (i << 3)

        return res

    def read_dword(self):
        res = 0
        for i in range(4):
            res|= self.read_byte() << (i << 3)

        return res

    def read_uleb128(self):
        '''
        Don't forget that we need to read as little-endian
        '''

        value = 0
        has_next = True
        length = 0
        while has_next and length < 8:
            b = self.read_byte()
            has_next = (b & 0x80) != 0
            b = b & 0x7F
            value = value + (b << length * 7)
            length = length + 1

        return value


    def read_uleb128_33bit(self):
        byte = self.read_byte()
        isnum = byte & 1
        value = byte >> 1

        if value >= 0x40:
            value &= 0x3F
            shift = -1

            while True:
                byte = self.read_byte()

                shift += 7
                value |= (byte & 0x7F) << shift

                if (byte < 0x80):
                    break

        return isnum, value

    def read_number(self):
        return (self.read_uleb128() << 32) | self.read_uleb128()


    def read_string(self, size):
        return ''.join([chr(self.read_byte()) for i in range(size)])