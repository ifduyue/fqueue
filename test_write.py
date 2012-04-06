from fqueue import Queue
import multiprocessing
import sys
import time

def sigint():
    import signal, os
    def sig(n, f):
        os.kill(0, signal.SIGTERM)
    signal.signal(signal.SIGINT, sig)
    
def randstr(l=10, chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    from random import choice
    return ''.join(choice(chars) for i in xrange(l))

def run(x=0):
    q = Queue('test.queue', 'w')
    q.put({
        'x': x,
        's': randstr(10),
    })
    q.close()
    time.sleep(0.1)
    print x
    return x
    
if __name__ == '__main__':
    pnum = int(sys.argv[1])
    times = int(sys.argv[2])
    sigint()
    pool = multiprocessing.Pool(pnum)
    pool.map(run, xrange(times))
