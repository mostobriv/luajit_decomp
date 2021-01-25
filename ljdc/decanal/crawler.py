from ljdc.bytecode.instructions import *
from ljdc.decanal.expression import *



class Crawler(object):

    def __init__(self, dump):
        self.dump = dump
        self.proto = dump.prototypes[0]

        # self.crawl()

    def translate(self):
        currrent_pc = 0
        # print([i.value for i in self.proto.pdata.constant_table])
        for code in self.proto.pdata.instructions:
            instruction = Instruction(code)
            # print(' --  %s' % instruction.ins.mnem)
            if instruction.ins in table_opcodes:
                expr = build_table_expression(self.proto, instruction)
                print(expr)

            elif instruction.ins in calls_and_vararg_opcodes:
                expr = build_call_expression(self.proto, instruction)
                print(expr)

            elif instruction.ins in constants_opcodes:
                expr = build_const_expression(self.proto, instruction)
                print(expr)

            elif instruction.ins in return_opcodes:
                expr = build_return_expression(self.proto, instruction)
                print(expr)

            else:
                pass



            currrent_pc+= 1

    @staticmethod
    def dis(prot, collected=set()):
        cur_pc = 0
        for c in prot.pdata.instructions:
            
            i = Instruction(c)
            collected.add(c & 0xFF)
            print('%4.4d %s' % (cur_pc, i))

            cur_pc+= 1
        print('=' * 60)

        for c in prot.pdata.complexconstants:
            if c.type == 'prototype':
                Crawler.dis(c.value, collected)

        return collected

