from ljdc.bytecode.instructions import Instruction 


class Crawler(object):

    def __init__(self, prots):
        self.prots = prots

        # self.crawl()


    @staticmethod
    def dis(prot, collected=set()):
        for c in prot.pdata.instructions:
            i = Instruction(c)
            collected.add(c & 0xFF)
            print(i)

        print('=' * 60)

        for c in prot.pdata.complexconstants:
            if c.type == 'prototype':
                Crawler.dis(c.value, collected)

        return collected

