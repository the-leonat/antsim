import numpy as np
import h5py

def test(n):
    groups = {}
    groups["test"] = (2, 2)
    s = Storage(groups, file_name="test.hdf5")

    for i in range(n):
        s.set("test", i, np.array([[i, i],[i, i]]))

    return s

class Storage():
    def __init__(self, groups, file_name = "record.hdf5", buffer_size = 100):
        self.file = h5py.File(file_name, "a")
        self.groups = groups

        self.buffer_size = buffer_size

        self.current_id = 0
        self.buffer = None
        self.buffer_next = None
        self.buffer_prev = None

        self.length = 0

        if "buffer" in self.file and "keyval" in self.file:
            print("Storage: recalling " + file_name)
            self.length = self.file["buffer"].attrs["length"]
            self.buffer_size = self.file["buffer"].attrs["buffer_size"]
        else:
            print("Storage: creating " + file_name)
            self.file.create_group("buffer")
            self.file.create_group("keyval")

        self.recall(self.current_id)
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

        self.buffer[group].set(index - (id * self.buffer_size), val)
        return True
        

    def get(self, group, index):
        if index < 0 or index > self.length:
            return None

        id = index // self.buffer_size
        self.recall(id)

        return self.buffer[group].get(index - (buffer_index * self.buffer_size))


    def recall(self, id):
        if id == self.current_id:
            return True

        if id < 0 or id > self.length:
            return False

        if id == self.current_id + 1:
            self.buffer_prev.store()
            self.buffer_prev = self.buffer
            self.buffer = self.buffer_next
            self.buffer_next = None
        elif id == self.current_id - 1:
            self.buffer_next.store()
            self.buffer_next = self.buffer
            self.buffer = self.buffer_prev
            self.buffer_prev = None
        else:
            self.buffer.store()
            self.buffer = None
            self.buffer_next.store()
            self.buffer_next = None
            self.buffer_prev.store()
            self.buffer_prev = None

        self.current_id = id

        if self.buffer_prev == None and id - 1 >= 0:
            for name in self.groups:
                self.buffer_prev[name] = Buffer(self.file, name, id - 1, self.groups[name], size=self.buffer_size)
        if self.buffer == None and id >= 0:
            for name in self.groups:
                self.buffer[name] = Buffer(self.file, name, id, self.groups[name], size=self.buffer_size)
        if self.buffer_next == None and id + 1 >= 0:
            for name in self.groups:
                self.buffer_next[name] = Buffer(self.file, name, id + 1, self.groups[name], size=self.buffer_size)

        return False

    def store(self):
        # save relevant fields for recall
        self.file["buffer"].attrs["length"] = self.length
        self.file["buffer"].attrs["buffer_size"] = self.buffer_size

        for name in self.groups:
            self.file["buffer"].attrs["group_" + name + "_shape"] = self.groups[name]

        # write remainig data to disk
        self.buffer.store()
        self.buffer_next.store()
        self.buffer_prev.store()

        return


class Buffer():
    def __init__(self, file, name, id, shape, size=100):
        self.id = str(id)
        self.name = name
        self.shape = shape
        self.size = size

        if self.id in file["buffer"][self.name]:
            self.dset = file["buffer"][self.name][self.id]

            self.recall()
        else:
            self.dset = file["buffer"][self.name].create_dataset(self.id, self.shape, chunks=True, compression="lzf")

            self.index = 0
            self.buffer = []

        return

    def recall(self):
        if self.buffered:
            return True

        print("Storage: recalling [" + self.name + "|" + self.id + "]")

        self.index = self.dset.attrs["index"]
        self.size = self.dset.attrs["size"]
        self.buffer = self.dset
        self.buffered = True

        return True

    def store(self):
        if not self.buffered:
            return True

        print("Storage: storing [" + self.name + "|" + self.id + "]")

        self.dset.attrs["index"] = self.index
        self.dset.attrs["size"] = self.size
        self.dset = self.buffer
        self.buffer = []
        self.buffered = False

        return True


    def set(self, index, val):
        if index < 0 or index > self.size:
            return False

        if self.shape != val.shape:
            return False

        if not self.buffered:
            return False

        self.buffer[index] = val
        return True

    def get(self, index):
        if index < 0 or index > self.size:
            return None

        if not self.buffered:
            return None

        return self.buffer[index]
