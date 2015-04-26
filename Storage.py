import numpy as np
import h5py

def test(n):
    groups = ["test"]
    shapes = [(2, 2)]
    dtypes = [np.int]
    s = Storage(groups, shapes, dtypes, file_name="test.hdf5")

    for i in range(n):
        s.set("test", i, np.array([[i, i],[i, i]]))

    return s

class Storage():
    def __init__(self, groups = [], shapes = [], dtypes = [], file_name = "record.hdf5", buffer_size = 100):
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
            self.buffer_size = self.file["buffer"].attrs["buffer_size"]

            self.groups = self.file["buffer"].attrs["groups"]

            self.shapes = [None] * len(self.groups)
            self.dtypes = [None] * len(self.groups)
        else:
            print("Storage: creating " + file_name)
            self.file.create_group("buffer")
            self.file.create_group("keyval")

            for name in self.groups:
                self.file["buffer"].create_group(name)

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

        id = index // self.buffer_size
        self.recall(id)

        done = self.buffer[group].set(index - (id * self.buffer_size), val)

        if done and index == self.length:
            self.length += 1

        return done
        

    def get(self, group, index):
        if index < 0 or index >= self.length:
            return None

        id = index // self.buffer_size
        self.recall(id)

        return self.buffer[group].get(index - (id * self.buffer_size))


    def recall(self, id):
        if id == self.current_id:
            return True

        if id == self.current_id + 1:
            if self.buffer_prev:
                for name in self.groups:
                    self.buffer_prev[name].store()
            self.buffer_prev = self.buffer
            self.buffer = self.buffer_next
            self.buffer_next = {}
        elif id == self.current_id - 1:
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

        if not self.buffer_prev and id - 1 >= 0:
            for i in range(len(self.groups)):
                self.buffer_prev[self.groups[i]] = Buffer(self.file, self.groups[i], id - 1, self.shapes[i], self.dtypes[i], self.buffer_size)
        if not self.buffer and id >= 0:
            for j in range(len(self.groups)):
                self.buffer[self.groups[j]] = Buffer(self.file, self.groups[j], id , self.shapes[j], self.dtypes[j], self.buffer_size)
        if not self.buffer_next and id + 1 >= 0:
            for k in range(len(self.groups)):
                self.buffer_next[self.groups[k]] = Buffer(self.file, self.groups[k], id + 1, self.shapes[k], self.dtypes[k], self.buffer_size)

        return True

    def store(self):
        # save relevant fields for recall
        self.file["buffer"].attrs["length"] = self.length
        self.file["buffer"].attrs["buffer_size"] = self.buffer_size

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
    def __init__(self, file, name, id, shape, dtype, size):
        self.id = str(id)
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.size = size

        self.buffer = None
        self.buffered = False
        self.changed = False

        if self.id in file["buffer"][self.name]:
            self.dset = file["buffer"][self.name][self.id]

            self.recall()
            self.shape = self.buffer[0].shape
            self.dtype = self.buffer[0].dtype
        else:
            self.dset = file["buffer"][self.name].create_dataset(self.id, (self.size,) + self.shape, dtype=self.dtype, chunks=True, compression="lzf")
            self.buffered = True

            self.buffer = [ np.array([-1]) ] * self.size
            self.index = 0

            self.buffered = True
            self.changed = False

        return

    def recall(self):
        if self.buffered:
            return True

        print("Storage: recalling [" + self.name + "|" + self.id + "]")

        self.index = self.dset.attrs["index"]
        self.size = self.dset.attrs["size"]

        if not self.buffer:
            self.buffer = [ np.array([-1]) ] * self.size

        self.buffer[0:self.index] = self.dset
        self.buffered = True
        self.changed = False

        return True

    def store(self):
        if not self.buffered:
            return True

        print("Storage: storing [" + self.name + "|" + self.id + "]")

        self.dset.attrs["index"] = self.index
        self.dset.attrs["size"] = self.size

        if self.changed:
            for i in range(self.index + 1):
                self.dset[i] = self.buffer[i]
        self.buffer = None
        self.buffered = False
        self.changed = False

        return True


    def set(self, index, val):
        if index < 0 or index > self.size or index > self.index + 1:
            return False

        if self.shape != val.shape:
            return False

        if not self.buffered:
            return False

        self.buffer[index] = val
        self.changed = True

        if index == self.index + 1:
            self.index += 1

        return True

    def get(self, index):
        if index < 0 or index > self.index:
            return None

        if not self.buffered:
            return None

        return self.buffer[index]
