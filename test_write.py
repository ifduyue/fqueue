import fqueue
import multiprocessing
import time

def w(x=0):
    q = fqueue.Queue("data", "w")
    q.put({'this-is\n': x})
    print 'put', {'this-is': x}
    q.close()
    time.sleep(0.1)
    
pool = multiprocessing.Pool(5)
pool.map(w, xrange(2000))

for i in xrange(2000):
    w("\n" * i)
    w(i)
