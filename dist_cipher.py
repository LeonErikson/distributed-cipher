'''3/4 Distributed Cipher'''


# Copyright 2019 Leon Scott Erikson

# This program creates a distributed cipher ("DC") of a specified source file.
# The distributed cipher is spread among four separate newly created DC files.
# A minimum of any three of the four DC files are needed to create a copy of
# the original source file. No information regarding the contents of the source
# file can be gleaned from inspection of a mere two of the DC files (except the
# size of the original file).

# The DC encoding process works as follows:
# For each bit of the source file we randomly select one set of the following
# sets of quadrinary symbols depending on whether the bit is a 0 or 1:
# Zero Sets = 0101, 1212, 2323, 0202, 1313, 0303
# One Sets = 0123, 0000, 1111, 2222, 3333
# We then assign one of the quadrinary symbols of the selected set to each of
# the four DC files. This results in four new files, each twice as large as the
# original file, so it is somewhat storage space intensive.

import os
import sys
import random
import argparse
import time

ZERO_CODES = [
    ['00', '00', '01', '01'],
    ['01', '01', '10', '10'],
    ['10', '10', '11', '11'],
    ['00', '00', '10', '10'],
    ['01', '01', '11', '11'],
    ['00', '00', '11', '11'],
    ]

ONE_CODES = [
    ['00', '00', '00', '00'],
    ['01', '01', '01', '01'],
    ['10', '10', '10', '10'],
    ['11', '11', '11', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ['00', '01', '10', '11'],
    ]

NUM_ZERO_CODES = len(ZERO_CODES) - 1
NUM_ONE_CODES = len(ONE_CODES) - 1

DC_FILE_EXT_PRE = 'dc'
RESTORED_FILE_SUF = '_restored'

READ_CHUNK_SIZE = 1024 * 32

def encode(filename):
    '''Encode zeros and ones in the file from a random set of the respective
    ZERO_CODES or ONES_CODES'''

    source_file_obj = open(filename, 'rb')
    dc_file0_obj = open(filename + '.' + DC_FILE_EXT_PRE + '0', 'wb')
    dc_file1_obj = open(filename + '.' + DC_FILE_EXT_PRE + '1', 'wb')
    dc_file2_obj = open(filename + '.' + DC_FILE_EXT_PRE + '2', 'wb')
    dc_file3_obj = open(filename + '.' + DC_FILE_EXT_PRE + '3', 'wb')

    in_buffer = source_file_obj.read(READ_CHUNK_SIZE)
    while in_buffer:
        out_buffer0 = []
        out_buffer1 = []
        out_buffer2 = []
        out_buffer3 = []

        for _, byte_val in enumerate(in_buffer):
            bit_string = '{0:08b}'.format(byte_val)

            for bit in bit_string:
                if bit == '0':
                    code_index = random.randint(0, NUM_ZERO_CODES)
                    code_set = ZERO_CODES[code_index]
                else:
                    code_index = random.randint(0, NUM_ONE_CODES)
                    code_set = ONE_CODES[code_index]

                random.shuffle(code_set)
                out_buffer0.append(code_set[0])
                out_buffer1.append(code_set[1])
                out_buffer2.append(code_set[2])
                out_buffer3.append(code_set[3])

        twice_in_buffer_size = len(in_buffer) * 2
        dc_file0_obj.write(int(''.join(out_buffer0), 2).to_bytes(twice_in_buffer_size, 'big'))
        dc_file1_obj.write(int(''.join(out_buffer1), 2).to_bytes(twice_in_buffer_size, 'big'))
        dc_file2_obj.write(int(''.join(out_buffer2), 2).to_bytes(twice_in_buffer_size, 'big'))
        dc_file3_obj.write(int(''.join(out_buffer3), 2).to_bytes(twice_in_buffer_size, 'big'))

        in_buffer = source_file_obj.read(READ_CHUNK_SIZE)

    dc_file0_obj.close()
    dc_file1_obj.close()
    dc_file2_obj.close()
    dc_file3_obj.close()

def decode(filename, dc_files):
    '''Decode to '0' if we have two of any symbol and one of another,
    otherwise decode to '1'.'''

    restored_source_file_obj = open(filename + RESTORED_FILE_SUF, 'wb')
    dc_file_objs = [open("{}".format(file), 'rb') for file in dc_files]

    in_buffers = [file.read(READ_CHUNK_SIZE) for file in dc_file_objs]

    while in_buffers[0]:
        in_bit_strings = [[] for _ in range(len(in_buffers))]
        # in_bit_strings will be a nested list, the inner lists containg
        # multiple 'binary' strings of length 8, each inner list
        # corresponding to one of the dc files.
        for buf_num in range(len(in_buffers)):
            for byte_val in in_buffers[buf_num]:
                in_bit_strings[buf_num].append('{0:08b}'.format(byte_val))

        restore_buffer = []
        for i in range(len(in_bit_strings[0])): # num of 8-bit binary strings per dc file.
            for j in range(4): # loop through each 8-bit binary string 2 bits at a time.
                # two_bits will contain a corresponding two char binary string
                # for each dc file.
                two_bits = []
                for k in range(len(in_bit_strings)): # for each dc file
                    two_bits.append(in_bit_strings[k][i][j*2:j*2+2])
                two_same = 0
                two_diff = 0
                for index1 in range(len(two_bits)-1):
                    for index2 in range(index1 + 1, len(two_bits)):
                        if two_bits[index1] == two_bits[index2]:
                            two_same += 1
                        else:
                            two_diff += 1
                if (two_same == 1 and two_diff == 5) or (two_same == 3 and two_diff == 3):
                    print("Error: DC files are corrupted.\n")
                    for file in dc_file_objs:
                        file.close()
                    restored_source_file_obj.close()
                    sys.exit(1)

                if (two_same >= 1 and two_diff >= 1):
                    restore_buffer.append('0')
                else:
                    restore_buffer.append('1')

        restore_buffer_bytes = int(len(restore_buffer)/8)
        restored_source_file_obj.write(int(''.join(restore_buffer),
                                           2).to_bytes(restore_buffer_bytes, 'big'))
        in_buffers = [file.read(READ_CHUNK_SIZE) for file in dc_file_objs]

    for file in dc_file_objs:
        file.close()

    restored_source_file_obj.close()

def find_dc_files(filename):
    '''Returns a list of DC files for the given filename'''
    dc_files = []
    for i in range(4):
        dc_filename = filename + '.' + DC_FILE_EXT_PRE + str(i)
        if os.path.exists(dc_filename):
            dc_files.append(dc_filename)
    return dc_files

def main():
    '''Performs encoding of a file or decoding of DC files.'''
    global args
    start_time = time.time()
    if args.e:
        if not os.path.exists(args.filename):
            print("Error: Filename: %s not found." %(args.filename))
            sys.exit(1)
        else:
            dc_files_count = len(find_dc_files(args.filename))
            if dc_files_count == 0:
                encode(args.filename)
                print("%s successfully encoded into 4 distributed cipher files." %(args.filename))
            else:
                print("Error: %s DC files for %s already in path. \
                      Remove before retrying." %(dc_files_count, args.filename))
                sys.exit(1)

    if args.d:
        if os.path.exists(args.filename + RESTORED_FILE_SUF):
            print("Error: Restored file %s in path." % (args.filename + RESTORED_FILE_SUF))
            sys.exit(1)
        else:
            dc_files = find_dc_files(args.filename)
            dc_file_count = len(dc_files)
            if dc_file_count >= 3:
                decode(args.filename, dc_files)
                print("%s successfully recovered.\n" %(args.filename + RESTORED_FILE_SUF))
            else:
                print("Error: At least 3 DC files are needed to decode a copy \
                      of the original file.\n")
                sys.exit(1)

    if not args.e and not args.d:
        print("-e or -d required.")
        sys.exit()

    end_time = time.time()
    print("Total execution time: %s seconds.\n" %(end_time - start_time))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Encrypts or Decrypts a 3/4 Distributed Cipher. '
                                     'Encoding creates 4 new files named (source filename).DC[1-4]',
                                     epilog='Note: Original source filename must \
                                     be specified for all options. No need to include \
                                     the DC extensions for option d')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', help='Encode a source file.', action='store_true')
    group.add_argument('-d', help='Decode DC files.', action='store_true')
    parser.add_argument("filename", type=str, help="source filename")
    args = parser.parse_args()
    main()
