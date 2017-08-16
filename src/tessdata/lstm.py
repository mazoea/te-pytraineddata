# coding=utf-8
# See main file for licence
#
# by Mazoea s.r.o.
#

"""
    Tesseract lstm.
"""
from .base import base


class network(object):

    class type(object):
        NT_NONE = 0
        NT_INPUT = 1
        NT_CONVOLVE = 2

        NT_MAXPOOL = 3
        NT_PARALLEL = 4
        NT_REPLICATED = 5
        NT_PAR_RL_LSTM = 6
        NT_PAR_UD_LSTM = 7
        NT_PAR_2D_LSTM = 8
        NT_SERIES = 9
        NT_RECONFIG = 10
        NT_XREVERSED = 11
        NT_YREVERSED = 12
        NT_XYTRANSPOSE = 13

        names = (
            "Invalid", "Input",
            "Convolve", "Maxpool",
            "Parallel", "Replicated",
            "ParBidiLSTM", "DepParUDLSTM",
            "Par2dLSTM", "Series",
            "Reconfig", "RTLReversed",
            "TTBReversed", "XYTranspose",
            "LSTM", "SummLSTM",
            "Logistic", "LinLogistic",
            "LinTanh", "Tanh",
            "Relu", "Linear",
            "Softmax", "SoftmaxNoCTC",
            "LSTMSoftmax", "LSTMBinarySoftmax",
            "TensorFlow"
        )

    class trainingstate(object):
        TS_DISABLED = 0
        TS_ENABLED = 1
        TS_TEMP_DISABLE = 2
        TS_RE_ENABLE = 3

    tp = type.NT_NONE
    train_state = trainingstate.TS_ENABLED
    needs_to_backprop = True
    network_flags = 0
    ni = 0
    no = 0
    num_weights = 0
    name = ""
    forward_win = None
    backward_win = None
    randomizer = None

    def stub(self, fin):
        data = fin.read_byte()
        if data == network.type.NT_NONE:
            type_name = fin.read_string()
            for i in range(len(network.type.names)):
                if type_name == network.type.names[i]:
                    self.type = i
                    break
            data = fin.read_byte()
            self.train_state = network.trainingstate.TS_DISABLED
            if data == network.trainingstate.TS_ENABLED:
                self.train_state = network.trainingstate.TS_ENABLED
            data = fin.read_byte()
            self.needs_to_backprop = (data != 0)
            self.network_flags = fin.read_int4()
            self.ni = fin.read_int4()
            self.no = fin.read_int4()
            self.num_weights = fin.read_int4()
            self.name = fin.read_string()
            pass


class lstm(base):

    name = "lstm"

    def __init__(self):
        self._n = network()

    def load(self, fin, start, end, parts):
        self._n.stub(fin)

    def present(self):
        return 0 < len(self._n.name)

    def info(self, ftor, **kwargs):
        ftor("Network name: %s", self._n.name)
