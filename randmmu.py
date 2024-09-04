from mmu import MMU
from random import randint

class RandMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.page_table = [None] * frames
        self.dirty_bits = [0] * frames
        self.use_bits = [0] * frames

        # Pick random value for randmmu
        self.random_value = randint(0,len(self.page_table)-1)

        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0

        self.debug_mode = False

    def set_debug(self):
        self.debug_mode = True

    def reset_debug(self):
        self.debug_mode = False

    def read_memory(self, page_number):
        page_index = 0

        try:
            # Check if the page is in the table and set use bit
            page_index = self.page_table.index(page_number)
            self.use_bits[page_index] = 1
    
        except ValueError:
            self.page_faults += 1
            self.__set_frame_to_replace()
            self.__write_if_dirty_page()

            # Read the page and perform operations
            self.page_table[self.random_value] = page_number
            self.disk_reads += 1
            self.use_bits[self.random_value] = 1
            self.__change_random_value()


    def write_memory(self, page_number):
        page_index = 0

        try:
            # Check if the page is in the table
            page_index = self.page_table.index(page_number)
            self.use_bits[page_index] = 1
            self.dirty_bits[page_index] = 1

        except ValueError:
            self.page_faults += 1
            self.__set_frame_to_replace()
            self.__write_if_dirty_page()

            # Read the page into the frame
            self.page_table[self.random_value] = page_number
            
            # Perform operations
            self.disk_reads += 1
            self.use_bits[self.random_value] = 1
            self.dirty_bits[self.random_value] = 1

            # Change the random value
            self.__change_random_value()


    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
    
    def __change_random_value(self):
        # pick a new random value
        self.random_value = randint(0,len(self.page_table)-1)        

    def __set_frame_to_replace(self):
        # Change the random value until we find a free frame to replace
        while (self.use_bits[self.random_value] == 1):
            self.use_bits[self.random_value] = 0
            self.__change_random_value()
        
    def __write_if_dirty_page(self):
       # Write to the current random value selected
        if (self.dirty_bits[self.random_value] == 1):
            self.disk_writes = self.disk_writes + 1
            self.dirty_bits[self.random_value] = 0
