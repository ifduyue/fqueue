import fqueue
import time

q = fqueue.Queue("data", "r")
while True:
    s = q.get()
    if s is None:
        time.sleep(5)
    else: print 'get', s
