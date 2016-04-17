import os
def eliminateBraces(f, l):
    abstract = ""
    numOpenedBrackets = 1
    index = l.index("{")
    abstract += l[:index]
    l = l[index:]
    if len(l) > 1:
        l = l[1:]
    else:
        l = ""
    while numOpenedBrackets and "\\end{abstract}" not in l: # this might return junk now.
        openPos = float("inf")
        closedPos = float("inf")
        if "{" in l:
            openPos = l.index("{")
        if "}" in l:
            closedPos = l.index("}")
        next = min(openPos, closedPos)
        if next < float("inf"):
            l = l[next:]
            if l[0] == "{":
                numOpenedBrackets += 1
            else:
                numOpenedBrackets -= 1
            l = l[1:]
        else:
            l = f.readline()
    abstract += l
    return abstract

def getAbstracts(amt = None):
    abstracts = []
    counter = 0
    for year in list(range(1992,2004)):
        print(year)
        files = os.listdir('KDD-Downloads/'+str(year)+'/')
        if amt:
            files = files[:amt]
        for filename in files:
            f = open(os.path.join('KDD-Downloads/'+str(year)+'/',filename), "r")
            # if counter%50==0:
                # print(counter)
            print(counter)
            # print(filename)
            abstract = ""
            try:
                for line in f:
                    if line[0]=='%':
                        continue
                    if line.strip() == "\\begin{abstract}":
                        l = f.readline()
                        counts = 0
                        while "\\end{abstract}" not in l :
                            counts+=1
                            if counts>100:
                                break
                            if "{" in l:
                                l += eliminateBraces(f,l)
                            else:
                                abstract += l

                            l = f.readline()
                        break
            except UnicodeDecodeError:
                pass
            abstracts.append(abstract)
            counter += 1

    f = open("abstracts.txt", "w")
    for abstract in abstracts:
        f.write(abstract)
    return abstracts
