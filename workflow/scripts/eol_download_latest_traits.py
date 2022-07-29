#!/usr/bin/env python3
# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Download Encyclopedia of Life (EOL) resources.
#   https://editors.eol.org/other_files/SDR/traits_all.zip
# Check if already on newest version before downloading
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-07-29
#------------------------------------------------------------------------------

import os, sys
import argparse
import requests
from dateutil.parser import parse
#from bs4 import BeautifulSoup
#import pandas as pd
import re

# ------------------------------------------------------------------------------
#                               GLOBAL VARIABLES
# ------------------------------------------------------------------------------

url = 'https://editors.eol.org/other_files/SDR/traits_all.zip'

# ------------------------------------------------------------------------------
#                            COMMAND-LINE INTERFACE
# ------------------------------------------------------------------------------

def parse_args():
  parser = argparse.ArgumentParser(description='Download Encyclopedia of Life (EOL) resources.')
  parser.add_argument('--version-file', help='Current version of downloaded EOL data.')
  parser.add_argument('out_dir', help='Output directory to download to.')

  args = parser.parse_args()
  return args

def download_file(url, out_dir):
    if not os.path.exists(args.out_dir):
      print(f'[ERROR] Directory does not exist: {args.out_dir}.')
      sys.exit(1)
    
    # build URL to download from
    url_dl = f'{base_url}/{filename}'
    # build file path to write to
    fn_out = os.path.join(args.out_dir, filename)
    
    print(f'source: {url_dl}')
    print(f'target: {fn_out}')
    print()

    response = requests.get(url_dl, stream=True)
    with open(fn_out, 'wb') as f:
      i = 0
      for chunk in response.iter_content(chunk_size=512*1024):
        f.write(chunk)
        i += 1
        print(f'{512 * i} kb downloaded...', end='\r')
      LINE_CLEAR = '\x1b[2K' # <-- ANSI sequence
      print(end=LINE_CLEAR)

def main(args):
  version = ''
  # read version file if given
  if args.version_file:
    with open(args.version_file, 'rt') as f:
      version = f.readline().strip()
      dt_version = parse(version)
  print(f'Latest version downloaded:\n{dt_version}\n---')

  # read header of resource URL
  response = requests.get(url, stream=True)
  assert 'Last-Modified' in response.headers
  txt_mod_date = response.headers['Last-Modified']
  dt_mod_date = parse(txt_mod_date)
  
  if dt_mod_date > dt_version:
    print('Online version is newer than local version:')
    print(f'  Online version: {dt_mod_date}')
    print(f'  Local version:  {dt_version}')
    print()
    print('---\nNow downloading data...')
    #out_fn = download_file(url, args.out_dir)
    #print(f'Download successful. Find new data at:\n{os.path.join(args.out_dir, web_version)}')
    if args.version_file:
      print(f'Storing latest version in version file {args.version_file}.')
  #    with open(args.version_file, 'wt') as f:
  #      f.write(f'{web_version}\n')
  else:
    print(f'Already on latest version:\n{dt_mod_date}')
    print()
    print('Doing nothing.')
  

if __name__ == '__main__':
  args = parse_args()
  main(args)
