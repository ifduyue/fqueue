import os
import fcntl

import marshal
import struct

__all__ = ['FQueueException', 'Queue']
__version__ = '0.0.3'
__author__ = 'Elyes Du <lyxint@gmail.com>'
__url__ = 'https://github.com/lyxint/fqueue'
__license__ = 'Life is short, do whatever you like'

class FQueueException(Exception): pass

def _lock(fp):
    try:
        _lockdata = struct.pack('hhllhh', fcntl.F_WRLCK, 0, 0, 0, 0, 0)
        fcntl.fcntl(fp, fcntl.F_SETLKW, _lockdata)
        return True
    except: return False
    
def _unlock(fp):
    try:
        _unlockdata = struct.pack('hhllhh', fcntl.F_UNLCK, 0, 0, 0, 0, 0)
        fcntl.fcntl(fp, fcntl.F_SETLKW, _unlockdata)
        return True
    except: return False

class Queue:

    def __init__(self, filepath, mode, seporator=".(*^__^*)@(*^__^*)@(*^__^*).\n"):
        '''init a queue

        filepath: path of file contains queue data
        mode: 'w' for write, 'r' for read
        '''
        self._filepath = filepath
        self._filepath_process = filepath + ".process"
        self._filepath_offset = filepath + ".offset"
        self._filepath_wlock = filepath + ".r.lock"
        self._filepath_rlock = filepath + ".w.lock"
        self.seporator = seporator
        if not seporator.endswith("\n"):
            self.seporator += "\n"
        self.error = None
        if mode.lower() not in list('wr'):
            raise FQueueException("mode can only be 'w' or 'r'")
        self.mode = mode.lower()
        self.offset = 0
        self.wlockfp = open(self._filepath_wlock, "w")
        self.rlockfp = open(self._filepath_rlock, "w")
        self.fp = None
        
        if mode == "r":
            self._r()
        elif mode == "w":
            self._w()
            
    def _r(self):
        if self.mode != "r": return False
        
        if os.access(self._filepath_process, os.F_OK):
            _lock(self.rlockfp)
            self.fp = open(self._filepath_process, "rb")
            self._load_offset()
            self.fp.seek(self.offset)
            _unlock(self.rlockfp)
            return True
        
        if not _lock(self.wlockfp): return False
        _lock(self.rlockfp)
        try:
            os.rename(self._filepath, self._filepath_process)
            self.offset = 0
            self._save_offset()
            self.fp = open(self._filepath_process, "rb")
            return True
        except Exception, e:
            self.error = e
            return False
        finally:
            _unlock(self.rlockfp)
            _unlock(self.wlockfp)
        
        
    def _w(self):
        self.fp = open(self._filepath, "a+b")
    
    def _save_offset(self):
        with open(self._filepath_offset, "w") as f:
            f.write(str(self.offset))
            return True
        return False
    
    def _load_offset(self):
        try:
            f = open(self._filepath_offset, "r")
            self.offset = int(f.read())
            f.close()
        except:
            self.offset = 0
    
    def get(self):
        if self.mode != 'r':
            raise FQueueException("cannot read in write mode")
        if self.fp is None and not self._r():
            return None
        s = []
        _lock(self.rlockfp)
        self._load_offset()
        while True:
            t = self.fp.readline()
            if not t:
                self.fp.close()
                self.fp = None
                os.unlink(self._filepath_process)
                self.offset = 0
                self._save_offset()
                break
            if t == self.seporator: break
            s.append(t)
        if self.fp is not None:
            self.offset = self.fp.tell()
            self._save_offset()
        _unlock(self.rlockfp)
        if not s:
            return None
        s = ''.join(s)
        try:
            return marshal.loads(s)
        except Exception, e:
            return None

    def put(self, obj):
        if self.mode != 'w':
            raise FQueueException("cannot write in read mode")
        _lock(self.wlockfp)
        self._w()
        self.fp.write(marshal.dumps(obj)+"\n")
        self.fp.write(self.seporator)
        _unlock(self.wlockfp)
            
    def close(self):
        if self.fp is not None:
            self.fp.close()
            self.fp = None
        if self.wlockfp is not None:
            self.wlockfp.close()
            self.wlockfp = None
        if self.rlockfp is not None:
            self.rlockfp.close()
            self.rlockfp = None
            
    
    
