import glob


def create_dataset():
    all_lyric_pth = glob.glob('lyrics/*/*.txt')

    with open('dataset.txt', 'wb') as dataset:

        for lyric_pth in all_lyric_pth:

            with open(lyric_pth, 'rb') as ly:
                for l in ly:
                    dataset.write(l)
                dataset.write('\n')


if __name__ == '__main__':

    # create_dataset()

    print 'Dataset Stats:'

    with open('dataset.txt', 'rb') as dataset_txt:

        dataset = dataset_txt.read().lower()
        total_char = len(dataset)
        unique_char = sorted(set(dataset))

    print 'Total char : {}'.format(total_char)
    print 'Unique char : {}'.format(unique_char)
    print 'N of Unique char : {}'.format(len(unique_char))

    for i in range(total_char / 100):
        print dataset[i*100: (i+1)*100]
