from __future__ import print_function
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import string

import luigi


class TG_LSTM():
    # cut the text in semi-redundant sequences of maxlen characters
    maxlen = 40

    def __init__(self):
        # List of allowed charachters
        self.chars = sorted(list(set(string.ascii_lowercase + " '.,!\"")))
        self.char_indices = dict((c, i) for i, c in enumerate(self.chars))
        self.indices_char = dict((i, c) for i, c in enumerate(self.chars))

    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def train(self, txt_file_target):  # path='../data/pg/pg32040.txt'
        text = txt_file_target.open().read().lower()
        text = "".join([x if x in self.chars else " " for x in text])
        print('corpus length:', len(text))

        step = 3
        sentences = []
        next_chars = []
        for i in range(0, len(text) - self.maxlen, step):
            sentences.append(text[i: i + self.maxlen])
            next_chars.append(text[i + self.maxlen])
        print('nb sequences:', len(sentences))

        print('Vectorization...')
        X = np.zeros((len(sentences),
                      self.maxlen,
                      len(self.chars)),
                     dtype=np.bool)
        y = np.zeros((len(sentences), len(self.chars)), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                X[i, t, self.char_indices[char]] = 1
            y[i, self.char_indices[next_chars[i]]] = 1

        # build the model: a single LSTM
        print('Build model...')
        self.model = Sequential()
        self.model.add(LSTM(128, input_shape=(self.maxlen, len(self.chars))))
        self.model.add(Dense(len(self.chars)))
        self.model.add(Activation('softmax'))

        optimizer = RMSprop(lr=0.01)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer=optimizer)

        self.model.fit(X, y,
                       batch_size=128,
                       epochs=30)

    def generate(self, sentence, diversity=1.0):
        generated = ''
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')

        for i in range(400):
            x = np.zeros((1, self.maxlen, len(self.chars)))
            for t, char in enumerate(sentence):
                x[0, t, self.char_indices[char]] = 1.

            preds = self.model.predict(x, verbose=0)[0]
            next_index = self.sample(preds, diversity)
            next_char = self.indices_char[next_index]

            generated += next_char
            sentence = sentence + next_char
            if len(sentence) >= self.maxlen:
                sentence = sentence[-self.maxlen:]

        return generated

    def save(self, path='../data/models/lstm.model'):
        self.model.save(path)

    def load(self, path='../data/models/lstm.model'):
        self.model = load_model(path)


class InputFileOnLocal(luigi.ExternalTask):
    """
    This class represents file stored on Google Storage in advance.
    """
    path = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present on Local disk.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(self.path)


class TrainLSTM(luigi.Task):

    # task_namespace = 'detect'
    path_txt = luigi.Parameter()
    epochs = luigi.IntParameter()
    epochs_step = luigi.IntParameter(10)

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.InputFileOnStorage`
        We don't read this file, just make sure it exists.
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        if self.epochs > self.epochs_step:
            return [TrainLSTM(path_txt=self.path_txt,
                              epochs=self.epochs - self.epochs_step,
                              epochs_step=self.epochs_step)]

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on
        the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(self.path_txt +
                                 "_" + str(self.epochs) +
                                 ".model")

    def run(self):
        """
        1. generate LSTM for given epoch_steps
        2. write the result into the :py:meth:`*(epoch).model` local target 
        """
        lstm = TG_LSTM()


#lstm = TG_LSTM()
# lstm.train()
# print(lstm.generate('immunity'))

# lstm.save()

#lstm2 = TG_LSTM()
# lstm2.load()
# print(lstm2.generate('immunity'))

#print(lstm2.generate('immunity ' * 2))

#print(lstm2.generate('immunity ' * 4))
