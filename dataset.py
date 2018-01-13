import math
import numpy as np
from torch.utils.data import Dataset


class LyricsDataset(Dataset):

    def __init__(self, dataset_path, seq_len):

        with open(dataset_path, 'rb') as dataset_txt:
            self.dataset = dataset_txt.read().lower()

        self.seq_len = seq_len
        self.unique_chars = sorted(set(self.dataset))
        self.unique_chars_map = {c: i for (i, c) in enumerate(self.unique_chars)}
        self.reverse_char_map = {i: c for (i, c) in enumerate(self.unique_chars)}

    def __len__(self):
        return int(math.floor(len(self.dataset) / float(self.seq_len)))

    def __getitem__(self, index):
        x, y = self._get_line_pair(index)

        return self.get_char_idx(x), self.get_char_idx(y)

    def _get_line_pair(self, index):
        return (
            self.dataset[index * self.seq_len: (index + 1) * self.seq_len],
            self.dataset[(index * self.seq_len) + 1: ((index + 1) * self.seq_len) + 1]
        )

    def get_char_idx(self, line):
        return [self.unique_chars_map[c] for c in line]
