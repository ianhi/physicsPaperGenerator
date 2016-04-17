#from pymarkovchain import MarkovChain
from markovChain import markovChain
import random
from getAbstracts import getAbstracts
# Create an instance of the markov chain. By default, it uses MarkovChain.py's location to
# store and load its database files to. You probably want to give it another location, like so:
mc_mid = markovChain("./middb")
mc_first = markovChain("./firstdb")
mc_last = markovChain("./lastdb")
# To generate the markov chain's language model, in case it's not present
from difflib import SequenceMatcher
import Levenshtein

def goodSentence(new,old=None):
    print('new: '+new)
    if len(new.split())<4:
        return False
    elif old is not None:
        if similar(old,new)>.6:
            return False
        if new.split()[0]==old.split()[0]:
            return False
    return True
def similar(a, b):
    return Levenshtein.ratio(a,b)
    #return SequenceMatcher(None, a, b).ratio()

def abstracts(num=1000):
    ab = getAbstracts(num)
    print("Generating text")
    count=0
    for i in ab:
        # if count%50 == 0:
            # print(count)
        count += 1
        i = " ".join(i.split("\n"))
        sentences = i.split('.')
        mc_first.generateDatabase(sentences[0])
        mc_last.generateDatabase(sentences[-1])
        for sent in sentences[1:-1]:
            mc_mid.generateDatabase(sent)
# To let the markov chain generate some text, execute
abstracts(None)

print("==============")
sentences=[""]
sentences[0]=mc_first.generateString()
while not goodSentence(sentences[0]):
    print("bad: "+sentences[0])
    sentences[0] = mc_first.generateString()
seedStr = random.choice(sentences[0].split())

for i in range(5):
    mid=""
    while not goodSentence(mid,sentences[-1]):
        #print(sentences)
        #print(sentences[len(sentences)-2])
        mid = mc_mid.generateStringWithSeed(seedStr)
        seedStr = random.choice(sentences[-1].split())
    #print("GOT HERE: "+mid)
    sentences.append(mid)

sentences.append(mc_last.generateStringWithSeed(seedStr))
while not goodSentence(sentences[-1]):
    seedStr = random.choice(sentences[-2].split())
    sentences[-1] = mc_last.generateStringWithSeed(seedStr)
print("====================================\n\n\n")
for i in sentences:
    print(i)


mc_mid.dumpdb()
mc_first.dumpdb()
mc_last.dumpdb()
