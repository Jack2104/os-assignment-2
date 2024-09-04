from mmu import MMU


class LruMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.page_table = [None] * frames
        self.dirty_bits = [0] * frames

        # Takes inspiration from Lamport time - incremented after each "event" (read/write) to determine logical ordering
        self.logical_time = 0
        self.page_timestamps = [None] * frames

        self.total_disk_reads = 0
        self.total_disk_writes = 0
        self.total_page_faults = 0

        self.debug_mode = False

    def set_debug(self):
        self.debug_mode = True

    def reset_debug(self):
        self.debug_mode = False

    # Returns a frame that can be replaced - either an empty page table entry, or the least
    # recently used (LRU) one
    def __get_replaceable_frame(self):
        # First check to see if there are any free frames, and if so replace it
        for frame_num, page in enumerate(self.page_table):
            if page == None:
                return frame_num

        # If no free frames are found, find the LRU frame based on the logical timestamps
        lru_frame = 0
        lowest_timestamp = self.page_timestamps[0]

        for frame_num, timestamp in enumerate(self.page_timestamps):
            if timestamp < lowest_timestamp:
                lru_frame = frame_num
                lowest_timestamp = timestamp

        return lru_frame

    # Simulates writing a page to disk (if it's dirty), and reading a new page from disk, from
    # page table entry frame_number
    def __replace_frame(self, frame_number):
        # If the replaced page has any changes, write it to disk
        if self.dirty_bits[frame_number] == 1:
            self.total_disk_writes += 1
            self.dirty_bits[frame_number] = 0

            if self.debug_mode:
                self.__log_debug_message(
                    f"Page {self.page_table[frame_number]} (frame {frame_number}) dirty - wrote to disk"
                )

        # Read in new page from disk
        self.total_disk_reads += 1

        # We've added a page to the page table, hence page faulted
        self.total_page_faults += 1

    def __log_debug_message(self, msg):
        print(f"{self.logical_time}: {msg}")

    # Simulates reading from page page_number, and writing to page_number if write is trur
    def __get_page(self, page_number, write):
        self.logical_time += 1

        # Check if the page number is already in the page table
        for frame_num, page_num in enumerate(self.page_table):
            if page_num == page_number:
                self.page_timestamps[frame_num] = self.logical_time

                if write:
                    self.dirty_bits[frame_num] = 1

                return

        # Otherwise, we have to fetch the page from disk and replace an occupied frame
        lru_frame = self.__get_replaceable_frame()  # Get the least recently used page

        if self.debug_mode:
            self.__log_debug_message(
                f"Replacing page {self.page_table[lru_frame]} (frame {lru_frame}) with page {page_number}..."
            )

        # Perform necessary reads/writes to disk to replace the frame
        self.__replace_frame(lru_frame)

        # Update new page in page table
        self.page_table[lru_frame] = page_number
        self.page_timestamps[lru_frame] = self.logical_time

        if write:
            self.dirty_bits[lru_frame] = 1

    def read_memory(self, page_number):
        self.__get_page(page_number=page_number, write=False)

    def write_memory(self, page_number):
        self.__get_page(page_number=page_number, write=True)

    def get_total_disk_reads(self):
        return self.total_disk_reads

    def get_total_disk_writes(self):
        return self.total_disk_writes

    def get_total_page_faults(self):
        return self.total_page_faults
