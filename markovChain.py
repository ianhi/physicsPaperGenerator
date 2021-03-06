"""
Modified pymarkovchain to make it faster when dealing with many text inputs
"""
from __future__ import division
# use cPickle when using python2 for better performance
try:
    import cPickle as pickle
except ImportError:
    import pickle
import logging
import os
import random
import re
from collections import defaultdict
from copy import deepcopy


class StringContinuationImpossibleError(Exception):
    pass

# {words: {word: prob}}
# We have to define these as separate functions so they can be pickled.


def _db_factory():
    return defaultdict(_one_dict)


def _one():
    return 1.0


def _one_dict():
    return defaultdict(_one)


def _wordIter(text, separator='.'):
    """
    An iterator over the 'words' in the given text, as defined by
    the regular expression given as separator.
    """
    exp = re.compile(separator)
    pos = 0
    for occ in exp.finditer(text):
        sub = text[pos:occ.start()].strip()
        if sub:
            yield sub
        pos = occ.start() + 1
    if pos < len(text):
        # take case of the last part
        sub = text[pos:].strip()
        if sub:
            yield sub


class markovChain(object):

    def __init__(self, dbFilePath=None):
        self.dbFilePath = dbFilePath
        self.normed_db = {}
        self.normalized = False
        if not dbFilePath:
            self.dbFilePath = os.path.join(
                os.path.dirname(__file__), "markovdb")
        try:
            with open(self.dbFilePath, 'rb') as dbfile:
                self.db = pickle.load(dbfile)
        except (IOError, ValueError):
            logging.warn(
                'Database file corrupt or not found, using empty database')
            self.db = _db_factory()

    def generateDatabase(self, textSample, sentenceSep='[.!?\n]', n=2):
        """ Generate word probability database from raw content string """
        # I'm using the database to temporarily store word counts
        # get an iterator for the 'sentences'
        textSample = _wordIter(textSample, sentenceSep)
        # We're using '' as special symbol for the beginning
        # of a sentence
        self.normalized = False
        self.db[('',)][''] = 0.0
        for line in textSample:
            words = line.strip().split()  # split words in line
            if len(words) == 0:
                continue
            # first word follows a sentence end
            self.db[("",)][words[0]] += 1

            for order in range(1, n + 1):
                for i in range(len(words) - 1):
                    if i + order >= len(words):
                        continue
                    word = tuple(words[i:i + order])
                    self.db[word][words[i + order]] += 1

                # last word precedes a sentence end
                self.db[tuple(words[len(words) - order:len(words)])][""] += 1

        # We've now got the db filled with parametrized word counts
        # We still need to normalize this to represent probabilities

    def normalize(self):
        print("NORMALIZING")
        import time
        millis = int(round(time.time() * 1000))

        # self.normed_db = deepcopy(self.db) #good bit slower than _db_factory
        self.normed_db = _db_factory()
        for word in self.db:
            wordsum = 0
            for nextword in self.db[word]:
                wordsum += self.db[word][nextword]
            if wordsum != 0:
                for nextword in self.db[word]:
                    self.normed_db[word][nextword] = self.db[
                        word][nextword] / wordsum
        self.normalized = True
        print(int(round(time.time() * 1000)) - millis)

    def dumpdb(self):
        try:
            with open(self.dbFilePath, 'wb') as dbfile:
                pickle.dump(self.db, dbfile)
            # It looks like db was written successfully
            return True
        except IOError:
            logging.warn('Database file could not be written')
            return False

    def generateString(self):
        """ Generate a "sentence" with the database of known text """
        return self._accumulateWithSeed(('',))

    def generateStringWithSeed(self, seed):
        """ Generate a "sentence" with the database and a given word """
        # using str.split here means we're contructing the list in memory
        # but as the generated sentence only depends on the last word of the seed
        # I'm assuming seeds tend to be rather short.

        words = seed.split()
        if (words[-1],) not in self.db:
            # The only possible way it won't work is if the last word is not
            # known
            raise StringContinuationImpossibleError('Could not continue string: '
                                                    + seed)
        return self._accumulateWithSeed(words)

    def _accumulateWithSeed(self, seed):
        """ Accumulate the generated sentence with a given single word as a
        seed """
        if not self.normalized:
            self.normalize()
            self.normalized = True
        nextWord = self._nextWord(seed)
        sentence = list(seed) if seed else []
        while nextWord:
            sentence.append(nextWord)
            nextWord = self._nextWord(sentence)
        return ' '.join(sentence).strip()

    def _nextWord(self, lastwords):
        lastwords = tuple(lastwords)
        if lastwords != ('',):
            while lastwords not in self.normed_db:
                lastwords = lastwords[1:]
                if not lastwords:
                    return ''
        probmap = self.normed_db[lastwords]
        sample = random.random()
        # since rounding errors might make us miss out on some words
        maxprob = 0.0
        maxprobword = ""
        for candidate in probmap:
            # remember which word had the highest probability
            # this is the word we'll default to if we can't find anythin else
            if probmap[candidate] > maxprob:
                maxprob = probmap[candidate]
                maxprobword = candidate
            if sample > probmap[candidate]:
                sample -= probmap[candidate]
            else:
                return candidate
        # getting here means we haven't found a matching word. :(
        return maxprobword
