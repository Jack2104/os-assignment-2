from mmu import MMU

class ClockMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.page_table = [None] * frames
        self.dirty_bits = [0] * frames
        
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug_mode = False
        
        self.use_bits = [0] * frames
        self.frame_pointer = 0
        
    def set_debug(self):
        self.debug_mode = True

    def reset_debug(self):
        self.debug_mode = False
        
    def read_memory(self, page_number):
        self.__get_page(page_number, False)
            
    def write_memory(self, page_number):
        self.__get_page(page_number, True)

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
    
    def __print_debug(self, message):
        if self.debug_mode:
            print(f"{message}")
    
    def __get_page(self, page_number, write):
        if (write == True):
            self.__print_debug("write_memory: page no " + str(page_number))
        elif (write == False):
            self.__print_debug("read_memory: page no " + str(page_number))
        
        page_index = 0
        
        try:
            # check if page in table
            page_index = self.page_table.index(page_number)
            self.__print_debug("page in table")
            # set use bit
            self.use_bits[page_index] = 1
            
            # if writing, set dirty bit
            if (write == True):
                self.dirty_bits[page_index] = 1
            
        except ValueError:
            self.__print_debug("page not in table")
            self.__increment_page_fault_count()
            self. __set_frame_to_replace()
            self.__write_if_dirty_page()

            # read page in to frame
            self.page_table[self.frame_pointer] = page_number
            # increment disk reads
            self.disk_reads += 1
            # set use bit
            self.use_bits[self.frame_pointer] = 1
            
            # if writing, set dirty bit
            if (write == True):
                self.dirty_bits[self.frame_pointer] = 1
            
            # move frame pointer to next frame
            self.__increment_frame_pointer()    
    
    def __increment_frame_pointer(self):
            self.frame_pointer = (self.frame_pointer + 1) % self.frames
    
    def __set_frame_to_replace(self):
        # cycle through frames until we find a frame with use bit set to 0
        # if use bit has been set to 1, set to 0 and move to next frame
        while (self.use_bits[self.frame_pointer] == 1):
            self.use_bits[self.frame_pointer] = 0
            self.__increment_frame_pointer()
        
    def __write_if_dirty_page(self):
        # check if page dirty
        # if so, increment disk writes and reset dirty bit
        if (self.dirty_bits[self.frame_pointer] == 1):
            self.disk_writes += 1
            self.dirty_bits[self.frame_pointer] = 0
    
    def __increment_page_fault_count(self):
        self.__print_debug("**page fault**")
        self.page_faults += 1