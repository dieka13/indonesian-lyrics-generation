import torch
from torch.autograd import Variable


class CharRNN(torch.nn.Module):

    def __init__(self, n_feature, n_hidden, n_layers, n_target, dropout=0):

        super(CharRNN, self).__init__()
        self.n_layers = n_layers
        self.n_hidden = n_hidden

        self.lookup = torch.nn.Embedding(n_feature, n_hidden)
        self.gru = torch.nn.GRU(n_hidden, n_hidden, n_layers, batch_first=True, dropout=dropout)
        self.dense = torch.nn.Linear(n_hidden, n_target)
        self.hidden_state = None

    def init_hidden(self):
        return Variable(torch.zeros(self.n_layers, 1, self.n_hidden)).double().cuda()

    def forward(self, x):

        x = self.lookup(x.view(1, -1))
        # print x.shape
        rnn_out, hidden = self.gru(x.view(1, 1, -1), self.hidden_state)
        # print rnn_out.shape
        logits = self.dense(rnn_out.view(1, -1))
        self.hidden_state = repackage_hidden(hidden)
        # print logits.shape

        return logits


def evaluate(model, dataset, start_str='A', generate_len=100, temp=0.8):

    predicted = start_str
    start_str = Variable(torch.LongTensor(dataset.get_char_idx(start_str))).cuda()

    #
    for p in range(len(start_str) - 1):
        _ = model(start_str[p])
    inp = start_str[-1]

    for i in range(generate_len):
        out = model(inp)

        out_dist = out.data.view(-1).div(temp).exp()
        top_i = torch.multinomial(out_dist, 1)[0]
        predicted = predicted + dataset.unique_chars[top_i]
        inp = Variable(torch.LongTensor([top_i])).cuda()

    return predicted


def repackage_hidden(h):
    """Wraps hidden states in new Variables, to detach them from their history."""
    if type(h) == Variable:
        return Variable(h.data)
    else:
        return tuple(repackage_hidden(v) for v in h)
