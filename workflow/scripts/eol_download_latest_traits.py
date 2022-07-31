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
# modified : 2022-07-31
#------------------------------------------------------------------------------

import click
import os, sys
import requests
from dateutil.parser import parse
import re

# ------------------------------------------------------------------------------
#                               GLOBAL VARIABLES
# ------------------------------------------------------------------------------

url = 'https://editors.eol.org/other_files/SDR/traits_all.zip'

# ------------------------------------------------------------------------------
#                               UTILITY FUNCTIONS
# ------------------------------------------------------------------------------

def download_file(url_dl, out_dir):
  if not os.path.exists(out_dir):
    print(f'[ERROR] Directory does not exist: {out_dir}.')
    sys.exit(1)

  # get filename from URL
  filename = url_dl.strip().rsplit('/', 1)[1]
  # build file path to write to
  fn_out = os.path.join(out_dir, filename)
  
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
  
  return fn_out
  
# ------------------------------------------------------------------------------
#                            COMMAND-LINE INTERFACE
# ------------------------------------------------------------------------------

@click.command()
@click.option('--version-file', '-v', help='File containing version of downloaded EOL resources.')
@click.option('--out-dir', '-o', required=True, help='Output directory to download to.')
def main(version_file, out_dir): #def main(args):
  """Download Encyclopedia of Life (EOL) resources."""
  version = '1970-01-01 00:00:00 GMT'
  dt_version = parse(version)
  # read version file if given
  if version_file:
    with open(version_file, 'rt') as f:
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
    fn_out = download_file(url, out_dir)
    print(f'Download successful. Find new data at:\n{fn_out}')
    if version_file:
      print(f'Storing latest version in version file {version_file}.')
      with open(version_file, 'wt') as f:
        f.write(f'{dt_mod_date}\n')
  else:
    print(f'Already on latest version:\n{dt_mod_date}')
    print()
    print('Doing nothing.')
  

if __name__ == '__main__':
  #args = parse_args()
  #main(args)

  main()
