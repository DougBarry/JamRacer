import time

# Hex math helper
def add_hex2(hex1, hex2):
    """add two hexadecimal string values and return as such"""
    return hex(int(hex1, 16) + int(hex2, 16))

current_milli_time = lambda: int(round(time.time() * 1000))
        
class PyLogger:
    indent_level = 4

    def __init__(self, source):
        self.file_handle = open('Python_Log.txt', 'a')
        self.source=source
        self.buf = []

    def write(self, data):
        self.buf.append(data)
        if data.endswith('\n'):
            self.file_handle = open('Python_Log.txt', 'a')
            self.file_handle.write('\t' * indent_level)
            self.file_handle.write(self.source + "::" + ''.join(self.buf))
            self.file_handle.close()
            self.buf = []

    def __del__(self):
        if self.buf != []:
            self.file_handle = open('Python_Log.txt', 'a')
            self.file_handle.write('\t' * indent_level)
            self.file_handle.write(self.source + "::" + ''.join(self.buf) + '\n')
            self.file_handle.close()      
            self.file_handle.close()
