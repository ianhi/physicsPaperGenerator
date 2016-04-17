#from pymarkovchain import MarkovChain
from markovChain import markovChain
import random
from getAbstracts import getAbstracts
import os.path
# Create an instance of the markov chain. By default, it uses MarkovChain.py's location to
# store and load its database files to. You probably want to give it another location, like so:
mc_mid = markovChain("./middb")
mc_first = markovChain("./firstdb")
mc_last = markovChain("./lastdb")
# To generate the markov chain's language model, in case it's not present
from difflib import SequenceMatcher
import Levenshtein
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'] #taken from nltk
def goodSentence(new,old=None):
    """
    Here is where most readability stuff should go. NLTK may have some real
    good stuff for this part
    """
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

def abstracts(num=None):
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
if(not os.path.exists("./middb")):
    print("makin abstracts")
    abstracts()
    mc_mid.dumpdb()
    mc_first.dumpdb()
    mc_last.dumpdb()

print("==============")
sentences=[""]
sentences[0]=mc_first.generateString()
while not goodSentence(sentences[0]):
    sentences[0] = mc_first.generateString()
seedStr = random.choice(sentences[0].split())

for i in range(3):
    mid=""
    while not goodSentence(mid,sentences[-1]):
        mid = mc_mid.generateStringWithSeed(seedStr)
        seedStr = random.choice([z for z in sentences[-1].split() if z not in stopwords])
    sentences.append(mid)

sentences.append(mc_last.generateStringWithSeed(seedStr))
while not goodSentence(sentences[-1]):
    seedStr = random.choice([z for z in sentences[-2].split() if z not in stopwords])
    sentences[-1] = mc_last.generateStringWithSeed(seedStr)
print("====================================\n\n\n")

for i in sentences:
    print(i)
