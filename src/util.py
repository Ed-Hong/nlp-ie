import sys,

def helpmsg():
    print('usage:   -n {1|2} -s {no|+1|gt}')
    print('-n   1 for unigram, 2 for bigram')
    print('-s  +1 for +1 smoothing, gt for Good-Touring, or no for no smoothing')

def processArgs(argv):
    if len(sys.argv) < 3:
        helpmsg()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv,'n:s:',['smoothing='])
    except getopt.GetoptError:
        helpmsg()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-n'):
            global n
            n = int(arg)
        elif opt in ('-s', '--smoothing'):
            global smoothing
            smoothing = arg

def test():
    print("weifjoweijfowijefiwoefoiwfe")