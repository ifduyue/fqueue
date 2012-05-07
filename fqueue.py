import os
import fcntl

import marshal
import struct

__all__ = ['Queue']
__version__ = '0.0.6'
__author__ = 'Elyes Du <lyxint@gmail.com>'
__url__ = 'https://github.com/lyxint/fqueue'
__license__ = 'Life is short, do whatever you like'

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

    def __init__(self, filepath, mode="deprecated", seporator=".(*^__^*)@(*^__^*)@(*^__^*).\n"):
        '''init a queue

        filepath: path of file contains queue data
        mode: 'w' for write, 'r' for read
        '''
        self._filepath = filepath
        self._filepath_process = filepath + ".process"
        self._filepath_offset = filepath + ".offset"
        self._filepath_wlock = filepath + ".r.lock"
        self._filepath_rlock = filepath + ".w.lock"
        seporator = seporator[:-1].replace("\n", "|") + seporator[-1]
        if not seporator.endswith("\n"):
            seporator += "\n"
        self.seporator = seporator
        self.error = None
        self.mode = mode.lower()
        self.offset = 0
        self.wlockfp = open(self._filepath_wlock, "w")
        self.rlockfp = open(self._filepath_rlock, "w")
        self.fp = None
    
    def _save_offset(self):
        with open(self._filepath_offset, "w") as f:
            f.write(str(self.offset))
            return True
        return False
    
    def _load_offset(self):
        try:
            f = False
            f = open(self._filepath_offset, "r")
            self.offset = int(f.read())
        except:
            self.offset = 0
        finally:
            if f: f.close()
            return self.offset
    
    def get(self):
        s = []
        try:
            _lock(self.rlockfp)
            if os.access(self._filepath_process, os.F_OK|os.R_OK):
                self.fp = open(self._filepath_process, "rb")
                self._load_offset()
                self.fp.seek(self.offset)
            else:
                try:
                    _lock(self.wlockfp)
                    os.rename(self._filepath, self._filepath_process)
                    self.offset = 0
                    self._save_offset()
                    self.fp = open(self._filepath_process, "rb")
                finally:
                    _unlock(self.wlockfp)
            
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
            
            if not s:
                return None
            s = ''.join(s)
            try:
                return marshal.loads(s)
            except Exception, e:
                return None
        except Exception as e:
            return None
        finally:
            _unlock(self.rlockfp)

    def put(self, obj):
        try:
            _lock(self.wlockfp)
            self.fp = open(self._filepath, "a+b")
            self.fp.write(marshal.dumps(obj)+"\n"+self.seporator)
            self.fp.close()
            self.fp = None
            return True
        except Exception as e:
            self.error = e
            return False
        finally:
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
            
    
    
