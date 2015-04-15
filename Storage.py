import numpy as np
import h5py

class Storage():
    '''
    A class to abstract away from memory access for very large continous buffers that cannot easiely be held in memory at once
    '''

    def __init__(self, file_name = "record.hdf5", buffer_size = 100):
        '''Constructor
        filename:       the filename or path of the file to write and read
        buffer_size:    max size of the buffer to hold before writing to disk
        '''
        self.index = 0

        self.file = h5py.File(file_name, "a")

        if not "data" in self.file:
            self.data_group = self.file.create_group("data")
        else:
            self.data_group = self.file["data"]

        if not "meta" in self.file:
            self.meta_group = self.file.create_group("meta")
        else:
            self.meta_group = self.file["meta"]
            try:
                self.index = self.get_attr("meta", "storage_index")
            except:
                pass

        self.dset_current = 0
        self.dset_index = 0

        self.buffer_size = buffer_size
        self.buffer_index = 0
        self.buffer_offset = 0
        self.buffer = {}
        for group_name in self.data_group:
            self.buffer[group_name] = [ np.zeros((1)) ] * self.buffer_size

        return

    def __del__(self):
        self.file.close()

    def finish(self):
        '''Make sure all reamaining write operations are finished before returning.
        '''

        self.set_attr("meta", "storage_index", self.index)

        # write remainig data to disk
        self.write_dset(self.dset_index)
        return


    def get_attr(self, group_name, attr_name):
        '''Get attribute of h5py group to read metadata
        attr_name:  string
        '''
        if group_name == "meta":
            return self.meta_group.attrs[attr_name]
        else:
            return self.data_group[group_name].attrs[attr_name]

    def set_attr(self, group_name, attr_name, attr_value):
        '''Set attribute of h5py group to store metadata
        attr_name:  string
        attr_value: array_like
        '''
        if group_name == "meta":
            self.meta_group.attrs[attr_name] = attr_value
        else:
            self.data_group[group_name].attrs[attr_name] = attr_value
        return


    def create_group(self, group_name):
        '''Create a new h5py group
        group_name: name of the new group
        '''
        if not group_name in self.data_group:
            self.data_group.create_group(group_name)
            self.buffer[group_name] = [ np.zeros((1)) ] * self.buffer_size
        return

    def delete_group(self, group_name):
        '''Delete a new h5py group
        group_name: name of the group
        '''
        del self.buffer[group_name]
        del self.data_group[group_name]
        return

    def append(self, dict):
        '''Appends to the end of the buffer at in dict specified groups. Not included groups will be zero
        dict:   dictionary with group_name as index and nparray to write as payload
        '''

        # we may have to load from disk
        if self.buffer_index == self.buffer_size:
            dset_index = (self.index - 1) // self.buffer_size
        else:
            dset_index = self.index // self.buffer_size
        done = self.read_dset(dset_index)
        if not done:
            return False

        if self.buffer_index >= self.buffer_size:
            # write to disk
            self.write_dset(self.dset_index)
            self.dset_index += 1
            self.dset_current = self.dset_index

            # reset buffer
            self.buffer_index = 0
            self.buffer_offset += self.buffer_size

        for group_name in dict:
            self.buffer[group_name][self.buffer_index] = dict[group_name]

        self.buffer_index += 1
        self.index += 1

        # check if buffer full


        return True

    def set(self, i, dict):
        '''Sets index i of the continous buffer to given object. This can involve a trip to the hard drive.
        i:      the index in the continous buffer
        dict:   dictionary with group_name as index and nparray to write as payload
        '''

        # i out of bounds
        if i < 0 or i > self.index:
            return False

        # just append, were at the current position anyway
        if i == self.index:
            return self.append(dict)

        # we may have to load from disk
        done = self.read_dset(i // self.buffer_size)
        if not done:
            return False

        for group_name in dict:
            self.buffer[group_name][i - self.buffer_offset] = dict[group_name]
        return True

    def get(self, group_name, i):
        '''Gets object at index i of the continous buffer. This can invole a trip to the hard drive.
        i:      the index in the continous buffer
        '''
        # i out of bounds
        if i < 0 or i > self.index - 1:
            return None

        # we may have to load from disk
        done = self.read_dset(i // self.buffer_size)
        if not done:
            return None
        return self.buffer[group_name][i - self.buffer_offset]

    def write_dset(self, dset_index):
        dset_name = str(dset_index)
        print("writing dset " + dset_name)

        for group_name in self.data_group:
            if not dset_name in self.data_group[group_name]:
                # assuming all entries of one group have the same shape
                dset_shape = (self.buffer_size,) + self.buffer[group_name][0].shape
                # new dataset with first dimensions length of buffer to write
                dset = self.data_group[group_name].create_dataset(dset_name, dset_shape, chunks=True, compression="lzf")
            else:
                dset = self.data_group[group_name][dset_name]

            for i in range(self.buffer_index):
                dset[i] = self.buffer[group_name][i]
            dset.attrs["storage_buffer_index"] = self.buffer_index
        return

    def read_dset(self, dset_index):
        if self.dset_current == dset_index:
            return True
        self.write_dset(self.dset_current)
        dset_name = str(dset_index)
        print("reading dset " + dset_name)

        for group_name in self.data_group:
            if not dset_name in self.data_group[group_name]:
                return False

            self.buffer_index = self.data_group[group_name][dset_name].attrs["storage_buffer_index"]
            del self.data_group[group_name][dset_name].attrs["storage_buffer_index"]
            for i in range(self.buffer_index):
                self.buffer[group_name][i] = self.data_group[group_name][dset_name][i]

        self.dset_current = dset_index
        self.buffer_offset = dset_index * self.buffer_size
        return True


    def test(self, n):
        self.create_group("test");
        d = {}

        for i in range(n):
            d["test"] = np.array([[i, i], [i, i]])
            self.append(d)
        return

