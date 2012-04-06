from fqueue import Queue
import multiprocessing
import sys
import time

def sigint():
    import signal, os
    def sig(n, f):
        os.kill(0, signal.SIGTERM)
    signal.signal(signal.SIGINT, sig)

def run(x=0):
    q = Queue('test.queue', 'r')
    obj = q.get()
    if obj is not None:
        print obj
    q.close()
    
if __name__ == '__main__':
    pnum = int(sys.argv[1])
    times = 1000
    sigint()
    pool = multiprocessing.Pool(pnum)
    while True:
        pool.map(run, xrange(times))

