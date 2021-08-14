#!/usr/bin/env python3

import argparse
import sys, os
import re

parser = argparse.ArgumentParser(description='Doubles the sample rate of a lip file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('ifile', help='input lip file')
parser.add_argument('-r', '--reverse', action='store_true', help='reverse', default=False)
args = parser.parse_args()

ifile = args.ifile
reverse = args.reverse
if not re.search(r"\.lip$", ifile.lower()):
  print("INVALID FILE EXTENSION\nWARNING, YOU COULD DAMAGE YOUR FILES")
  exit(1)

acm_length_off = 16
acm_length_len = 4
acm_offset_off = 44 #offset phoneme 0 or end header
acm_offset_len = 4
total_phonems_off = 20
total_phonems_len = 4
marker_len = 4
file_len = os.stat(ifile).st_size

def read_double_write(fh, foff, flen, rev):
  fh.seek(foff)
  fval = (int.from_bytes(fh.read(flen), byteorder='big', signed=False))
  if rev and fval:
    fval = int(fval/2)
  elif not rev:
    fval = int(fval*2)
  fh.seek(foff)
  fh.write((fval.to_bytes(flen, byteorder='big', signed=False)))

with open(ifile, 'r+b') as lip:
  lip.seek(total_phonems_off)
  acm_offset_off = int((int.from_bytes(lip.read(total_phonems_len), byteorder='big', signed=False))+acm_offset_off)
  lip.seek(acm_offset_off)
  if (lip.read(marker_len + acm_offset_len)) == (b'\x00\x00\x00\x01\x00\x00\x00\x00'):
    read_double_write(lip, acm_length_off, acm_length_len, reverse)
    while(True):
      acm_offset_off += marker_len
      if acm_offset_off >= file_len:
        print("EOF!")
        break
      read_double_write(lip, acm_offset_off, acm_offset_len, reverse)
      acm_offset_off += acm_offset_len
  else:
    print("unknown marker and offset, please tell the developer")
    exit(1)
exit(0)


