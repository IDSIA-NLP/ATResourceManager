#!/usr/bin/env python3
# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Download Catalogue of Life (CoL) resources.
#   https://download.checklistbank.org/col/
# Check if already on newest version before downloading
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-07-26
#------------------------------------------------------------------------------

import os, sys
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# ------------------------------------------------------------------------------
#                               GLOBAL VARIABLES
# ------------------------------------------------------------------------------

url = 'https://download.checklistbank.org/col/monthly/'

# ------------------------------------------------------------------------------
#                            COMMAND-LINE INTERFACE
# ------------------------------------------------------------------------------

def parse_args():
  parser = argparse.ArgumentParser(description='Download Catalogue of Life (CoL) resources.')
  parser.add_argument('--version-file', help='Current version of downloaded CoL data.')
  parser.add_argument('out_dir', help='Output directory to download to.')

  args = parser.parse_args()
  return args

def download_file(filename, base_url, out_dir):
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
  print(f'Latest version downloaded:\n{version}\n---')

  # read HTML from resource URL
  html = requests.get(url).text
  soup = BeautifulSoup(html, 'html.parser')
  data = []
  regex = r'\d{4}-\d{2}-\d{2}_dwca\.zip'
  
  # parse table from HTML
  for tr in soup.find('table').find_all('tr'):
    row = [td.text for td in tr.find_all('td')]
    if len(row) < 2:
      continue
    m = re.search(regex, row[1])
    if m:
      data.append(m.group())

  # check if web version is newer than local copy
  web_version = sorted(data)[-1]
  if web_version > version:
    print('Online version is newer than local version:')
    print(f'  Online version: {web_version}')
    print(f'  Local version:  {version}')
    print()
    print('---\nNow downloading data...')
    download_file(web_version, url, args.out_dir)
    print(f'Download successful. Find new data at:\n{os.path.join(args.out_dir, web_version)}')
    if args.version_file:
      print(f'Storing latest version in version file {args.version_file}.')
      with open(args.version_file, 'wt') as f:
        f.write(f'{web_version}\n')
  else:
    print(f'Already on latest version:\n{web_version}')
    print()
    print('Doing nothing.')
  

if __name__ == '__main__':
  args = parse_args()
  main(args)
