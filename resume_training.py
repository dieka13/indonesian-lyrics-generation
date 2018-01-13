import torch
import random
import time
from torch.autograd import Variable


from dataset import LyricsDataset
from char_RNN import evaluate

# memory leak bug! https://github.com/pytorch/pytorch/issues/3665
torch.backends.cudnn.enabled = False

# model parameter
n_char = 100
n_feature = 69
n_hidden = 256
n_layer = 3
n_epoch = 3
dropout = 0.2

# init model
char_RNN = torch.load('model-LSTM-2.pytorch')
loss_fn = torch.nn.CrossEntropyLoss()
char_RNN.double()
char_RNN.cuda()
print char_RNN
optimizer = torch.optim.Adam(char_RNN.parameters(), lr=1e-4)

# init dataset
dataset = LyricsDataset('dataset.txt', n_char)


losses = []
history_txt = open('history_resume.txt', 'wb')
start_time = time.time()

for i_epoch in range(n_epoch):

    rand_idx = range(len(dataset))
    random.shuffle(rand_idx)

    for i_minibatch in range(len(dataset)):
        x, y = dataset[rand_idx[i_minibatch]]
        x = Variable(torch.LongTensor(x), requires_grad=False).cuda()
        y = Variable(torch.LongTensor(y), requires_grad=False).cuda()
        char_RNN.zero_grad()

        loss = 0
        for i_char in range(len(x)):
            out = char_RNN(x[i_char])
            loss = loss + loss_fn(out, y[i_char])
        losses.append(loss.data[0] / float(len(x)))

        loss.backward()
        optimizer.step()

        if i_minibatch % 500 == 0:
            summary = 'epoch {} batch {} avg. loss: {}'.format(i_epoch, i_minibatch, sum(losses) / float(500))
            generated = evaluate(char_RNN, dataset, 'cinta', 200)
            print summary
            print generated
            print

            history_txt.write('{}\n{}\n\n'.format(summary, generated))
            history_txt.flush()

            losses = []

    torch.save(char_RNN, 'model-LSTM-{}-resumed.pytorch'.format(i_epoch + 1))

history_txt.close()
end_time = time.time()

print 'total training time: {}'.format(end_time - start_time)
