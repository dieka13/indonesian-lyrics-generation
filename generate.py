import torch
import time

from char_RNN import evaluate
from dataset import LyricsDataset

dataset = LyricsDataset('dataset.txt', 100)
char_RNN = torch.load('model-LSTM-3-resumed.pytorch')

start_str = 'dirimu'
generated_text = evaluate(char_RNN, dataset, start_str, generate_len=1000, temp=0.75)
print generated_text

with open('generated-{}-{}.txt'.format(start_str, time.strftime('%Y%m%d_%H%M%S')), 'w') as f:
    f.write(generated_text)

