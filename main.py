import sys
import argparse

from ljdc.parsing.dump import Dump
from ljdc.parsing.stream import RawStream
from ljdc.decanal.crawler import Crawler

from ljdc.bytecode.instructions import OPCODES

def main(argc, argv):
    io = RawStream(argv[1])
    parsed = Dump(io)

    canal = Crawler(parsed)

    assert len(parsed.prototypes) == 1

    used_ops = Crawler.dis(parsed.prototypes[0])
    for i in used_ops:
        print(OPCODES[i].mnem)

    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))