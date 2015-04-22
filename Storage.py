import numpy as np
import h5py

class Storage():
    def __init__(self, file_name = "record.hdf5", buffer_size = 100):
        self.file = h5py.File(file_name, "a")

        self.buffer_index = 0
        self.buffer_size = buffer_size

        self.buffer = {}
        self.buffer_next = None

        self.length = 0

        if "buffer" in self.file and "keyval" in self.file:
            print("Storage: recalling " + file_name)
            self.length = self.file["buffer"].attrs["length"]
        else:
            print("Storage: creating " + file_name)
            self.file.create_group("buffer")
            self.file.create_group("keyval")

        for name in groups:
            self.buffer[name] = Buffer(self.file, name, self.buffer_index, groups[name], size=self.buffer_size)
            self.buffer_next[name] = Buffer(self.file, name, self.buffer_index + 1, groups[name], size=self.buffer_size)

        return

    def __del__(self):
        self.file.close()

    def finish(self):
        # save relevant fields for recall
        self.file["buffer"].attrs["length"] = self.length

        # write remainig data to disk
        for name in self.buffer:
            self.buffer[name].store()
            self.buffer_next[name].store()

        return

    def keyval_set(self, key, val):
        self.file["keyval"].attrs[key] = val
        return

    def keyval_get(self, key):
        return self.file["keyval"].attrs[key]

    def set(self, group, index, val):
        if index < 0 or index > self.length:
            return False

        

    def get(self, group, index):
        if index < 0 or index > self.length:
            return None

        buffer_index = index // self.buffer_size

        if buffer_index != self.buffer_index:
            # load correct buffer
            if buffer_index == self.buffer_index + 1 and self.buffer_next != None:
                self.buffer = self.buffer_next
                self.buffer_index = buffer_index
                for group in self.buffer:
                    self.buffer_next[group] = Buffer(self.file, group, self.buffer_index + 1, self.shape[group], size=self.buffer_size)
            else:



        return self.buffer[group].get(index - (buffer_index * self.buffer_size))



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
