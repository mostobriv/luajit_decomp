

# Types of control transfer:
# JUMP - with jmp instruction
# NATIVE - by executing next instruction
T_JUMP      = 1
T_NATIVE    = 2


def connect_two_basic_blocks(bb_from, bb_to, edge_type):
    bb_from._add_outgoing_edge(bb_to, edge_type)
    bb_to._add_incoming_edge(bb_from, edge_type)


class BasicBlock:
    def __init__(self, start, end, body, is_terminating=False):
        self.start = start
        self.end = end
        self.outgoing_edges = list()
        self.incoming_edges = list()
        self.is_terminating = is_terminating


    def _add_outgoing_edge(self, bb, edge_type):
        self.outgoing_edges.append((bb, edge_type))


    def _add_incoming_edge(self, bb, edge_type):
        self.incoming_edges.append((bb, edge_type))


def build_control_flow_graph(proto):
    pass


# if sequence of multiple bb's with one outcoming and one incoming edges met
# then merge it into one bb
def merge_sequences(cfg):
    pass