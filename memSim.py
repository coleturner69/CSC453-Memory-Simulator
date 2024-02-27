import sys

class TLB: 
    def __init__(self, size=16):
        self.size = size
        self.buffer = []

    def add(self, page_num, physical_frame_num):
        if (0 <= page_num <= 255):
            if (len(self.buffer) >= self.size):
                self.buffer.pop(0)

            self.buffer.append((page_num, physical_frame_num))
        else:
            raise ValueError("Invalid page number, must be between 0 and 255")
        
    def get_frame(self, page_num):
        if (0 <= page_num <= 255):
            for tup in self.buffer:
                if (tup[0] == page_num):
                    return tup[1]
            return None
        else:
            raise ValueError("Invalid page number, must be between 0 and 255")


class PageTable:
    def __init__(self):
        self.table = [None] * 256

    def add(self, page_num, physical_frame_num, loaded):
        if (0 <= page_num <= 255):
            self.table[page_num] = (physical_frame_num, loaded)
        else:
            raise ValueError("Invalid page number, must be between 0 and 255")
    
    def remove(self, page_num):
        if (0 <= page_num <= 255):
            self.table[page_num] = None
        else:
            raise ValueError("Invalid page number, must be between 0 and 255")
        
    def get_frame(self, page_num):
        if (0 <= page_num <= 255):
            frame_num = self.table[page_num]

            if (frame_num == None):
                return None
            else:
                return frame_num
        else:
            raise ValueError("Invalid page number, must be between 0 and 255")
    
    def update_loaded(self, page_num, loaded):
        if (0 <= page_num <= 255):
            if (self.table[page_num] != None):
                self.table[page_num] = (self.table[page_num][0], loaded)
            else:
                raise ValueError("Given page is not in Page Table")
        else:
            raise ValueError("Invalid page number, must be between 0 and 255")
        
class Frame:
    def __init__(self):
        self.is_occupied = False
        self.page_content = None

class PhysicalMemory:
    def __init__(self, frames_num):
        self.frames = [Frame() for i in range(frames_num)]

    def load(self, page):
        for frame_num, frame in enumerate(self.frames):
            if (frame.is_occupied == False):
                frame.is_occupied = True
                frame.page_content = page
                return frame_num
        return None
    
    def check_full(self):
        for frame in self.frames:
            if (frame.is_occupied == False):
                return False
        return True
    
def read_file(filename):
    with open(filename, 'r') as f:
        ref_seq = [int(line.strip()) for line in f]
        return ref_seq
    
def read_bin(bin_name):
    with open(bin_name, 'rb') as b:
        return b.read()


def main():
    if (len(sys.argv) < 2 or len(sys.argv) > 4):
        print("Usage: memSim <reference-sequence-file.txt> <FRAMES> <PRA>")
        sys.exit(1)

    frames = 256
    pra = "fifo"

    if (len(sys.argv) >= 3):
        frames = int(sys.argv[3])

        if (frames <= 0 or frames > 256):
            print("FRAMES must be an integer > 0 and <= 256")
            sys.exit(1)

    if (len(sys.argv) == 4):
        pra = sys.argv[3]
        
        if pra not in ["fifo", "lru", "opt"]:
            print("PRA must be either 'fifo', 'lru', or 'opt'")
            sys.exit(1)
        
    page_size = 256
    frame_size = 256

    ref_seq_file = sys.argv[1]
    addresses = read_file(ref_seq_file)

    backing_store = read_bin('BACKING_STORE.bin')

    physical_mem_size = 256 * frames
    physical_memory = PhysicalMemory(frames)

    tlb = TLB()
    page_table = PageTable()

    page_faults = 0
    tlb_hits = 0
    tlb_misses = 0

    for address in addresses:
        page_num = address // page_size
        offset = address % page_size

        #not implemented
        value = 0
        physical_frame_num = 0
        page_content = 0

        physical_frame_num = tlb.get_frame(page_num)
        if (physical_frame_num != None):
            tlb_hits += 1
            value = physical_memory.frames[physical_frame_num].page_content[offset]
        else:
            tlb_misses += 1

            frame_tup = page_table.get_frame(page_num)
            if (frame_tup == None):
                page_faults += 1

                page_content = backing_store[page_num * page_size : (page_num+1) * page_size]
                is_full = physical_memory.check_full()
                if (is_full):
                    #use PRA here
                    physical_frame_num = 0
                else:
                    physical_frame_num = physical_memory.load(page_content)

                page_table.add(page_num, physical_frame_num, 1)
                value = page_content[offset]
                
                tlb.add(page_num, physical_frame_num)
            else:
                physical_frame_num, loaded = frame_tup
                if(loaded):
                    value = physical_memory.frames[physical_frame_num].page_content[offset]
                else:
                    page_faults += 1

                    page_content = backing_store[page_num * page_size : (page_num+1) * page_size]
                    is_full = physical_memory.check_full()
                    if (is_full):
                        #use PRA here
                        physical_frame_num = 0
                    else:
                        physical_frame_num = physical_memory.load(page_content)

                    page_table.add(page_num, physical_frame_num, 1)
                    value = page_content[offset]
                    
                    tlb.add(page_num, physical_frame_num)

        signed_value = value - 256 if value > 127 else value
        print(f"{address}, {signed_value}, {physical_frame_num}, \n{page_content.hex().upper()}")

    print(f"Number of Translated Addresses = {len(addresses)}")
    print(f"Page Faults = {page_faults}")
    print(f"Page Fault Rate = {(page_faults / len(addresses)):.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"TLB Hit Rate = {(tlb_hits / tlb_misses):.3f}")

if __name__ == "__main__":
    main()
