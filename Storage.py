import numpy as np
import h5py
import threading

def test(n):
    groups = ["test"]
    shapes = [(2, 2)]
    dtypes = [np.int]
    s = Storage("test.hdf5", groups, shapes, dtypes, buffer_size=50)

    for i in range(n):
        s.set("test", i, np.array([[i, i],[i, i]]))

    return s

class Storage():
    def __init__(self, file_name, groups = [], shapes = [], dtypes = [], buffer_size = 100, compression = "lzf"):
        self.file = h5py.File(file_name, "a")
        self.groups = groups
        self.shapes = shapes
        self.dtypes = dtypes

        self.buffer_size = buffer_size

        self.current_id = -1
        self.buffer = {}
        self.buffer_next = {}
        self.buffer_prev = {}

        self.length = 0

        if "buffer" in self.file and "keyval" in self.file:
            print("Storage: recalling " + file_name)

            self.length = self.file["buffer"].attrs["length"]

            self.groups = self.file["buffer"].attrs["groups"]
            self.shapes = [None] * len(self.groups)
            self.dtypes = [None] * len(self.groups)
        else:
            print("Storage: creating " + file_name)
            self.file.create_group("buffer")
            self.file.create_group("keyval")

            for i in range(len(self.groups)):
                maxshape = (None,) * (len(self.shapes[i]) + 1)
                self.file["buffer"].create_dataset(self.groups[i], (0,) + self.shapes[i], self.dtypes[i], chunks=True, maxshape=maxshape, compression = compression)

        self.recall(0)
        return

    def __del__(self):
        self.file.close()

    def keyval_set(self, key, val):
        self.file["keyval"].attrs[key] = val
        return

    def keyval_get(self, key):
        return self.file["keyval"].attrs[key]

    def set(self, group, index, val):
        if index < 0 or index > self.length:
            return False

        id = (index // self.buffer_size) * self.buffer_size
        self.recall(id)

        done = self.buffer[group].set(index - id, val)

        if done and index == self.length:
            self.length += 1

        return done
        

    def get(self, group, index):
        if index < 0 or index >= self.length:
            return None

        id = (index // self.buffer_size) * self.buffer_size
        self.recall(id)

        return self.buffer[group].get(index - id)


    def recall(self, id):
        if id == self.current_id:
            return True

        if id == self.current_id + self.buffer_size:
            if self.buffer_prev:
                for name in self.groups:
                    self.buffer_prev[name].store()
            self.buffer_prev = self.buffer
            self.buffer = self.buffer_next
            self.buffer_next = {}
        elif id == self.current_id - self.buffer_size:
            if self.buffer_next:
                for name in self.groups:
                    self.buffer_next[name].store()
            self.buffer_next = self.buffer
            self.buffer = self.buffer_prev
            self.buffer_prev = {}
        else:
            if self.buffer_prev:
                for name in self.groups:
                    self.buffer_prev[name].store()
            self.buffer_prev = {}
            if self.buffer:
                for name in self.groups:
                    self.buffer[name].store()
            self.buffer = {}
            if self.buffer_next:
                for name in self.groups:
                    self.buffer_next[name].store()
            self.buffer_next = {}

        self.current_id = id

        if not self.buffer_prev and id - self.buffer_size >= 0:
            for i in range(len(self.groups)):
                self.buffer_prev[self.groups[i]] = Buffer(self.file, self.groups[i], id - self.buffer_size, self.buffer_size, self.shapes[i], self.dtypes[i])
        if not self.buffer and id >= 0:
            for j in range(len(self.groups)):
                self.buffer[self.groups[j]] = Buffer(self.file, self.groups[j], id, self.buffer_size, self.shapes[j], self.dtypes[j])
        if not self.buffer_next and id + self.buffer_size >= 0:
            for k in range(len(self.groups)):
                self.buffer_next[self.groups[k]] = Buffer(self.file, self.groups[k], id + self.buffer_size, self.buffer_size, self.shapes[k], self.dtypes[k])

        return True

    def store(self):
        # save relevant fields for recall
        self.file["buffer"].attrs["length"] = self.length
        self.file["buffer"].attrs["groups"] = self.groups

        # write remainig data to disk
        if self.buffer_prev:
            for name in self.groups:
                self.buffer_prev[name].store()
        if self.buffer:
            for name in self.groups:
                self.buffer[name].store()
        if self.buffer_next:
            for name in self.groups:
                self.buffer_next[name].store()

        return


class Buffer():
    def __init__(self, file, name, id, size, shape, dtype):
        self.thread = None

        self.id = id
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.size = size

        if not self.name in file["buffer"]:
            print("Storage: critical error")

        self.buffer = None
        self.changed = False

        self.dset = file["buffer"][self.name]

        super_length = self.dset.shape[0]
        self.length = min(max(0, super_length - self.id), self.size)

        self.recall()

        return

    def recall(self):
        if self.buffer:
            return True

        if self.length != 0:
            print("Storage: recalling " + self.name + "[" + str(self.id) + ":" + str(self.id + self.length) + "]")

        if self.thread:
            self.thread.join()
        self.thread = BufferReader(self)
        self.thread.start()

        return True

    def store(self):
        if not self.buffer:
            return True

        print("Storage: storing " + self.name + "[" + str(self.id) + ":" + str(self.id + self.length) + "]")

        if self.changed:
            if self.thread:
                self.thread.join()
            self.thread = BufferWriter(self)
            self.thread.start()

        return True


    def set(self, index, val):
        if index < 0 or index >= self.size or index > self.length:
            return False

        if self.shape != val.shape:
            return False

        if not self.buffer:
            return False

        if self.thread:
            self.thread.join()
            self.thread = None

        self.buffer[index] = val
        self.changed = True

        if index == self.length:
            self.length += 1

        return True

    def get(self, index):
        if index < 0 or index > self.length:
            return None

        if not self.buffer:
            return None

        if self.thread:
            self.thread.join()
            self.thread = None

        return self.buffer[index]


class BufferWriter(threading.Thread):
    lock = threading.Lock()

    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer
        return

    def run(self):
        BufferWriter.lock.acquire()

        super_length = self.buffer.dset.shape[0]
        if super_length < self.buffer.id + self.buffer.length:
            self.buffer.dset.resize(self.buffer.id + self.buffer.length, axis=0)
            
        self.buffer.dset[self.buffer.id:self.buffer.id + self.buffer.length] = self.buffer.buffer[0:self.buffer.length]

        self.buffer.buffer = None
        self.buffer.changed = False

        BufferWriter.lock.release()
        return

class BufferReader(threading.Thread):
    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer
        return

    def run(self):
        if not self.buffer.buffer:
            self.buffer.buffer = [ np.array([-1]) ] * self.buffer.size

        self.buffer.length = min(self.buffer.size, max(0, self.buffer.dset.shape[0] - self.buffer.id))
        self.buffer.buffer[0:self.buffer.length] = self.buffer.dset[self.buffer.id:self.buffer.id + self.buffer.length]
        self.buffer.changed = False

        return
