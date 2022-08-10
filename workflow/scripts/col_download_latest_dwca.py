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
# modified : 2022-08-05
#------------------------------------------------------------------------------

import os, sys
import click
import requests
from bs4 import BeautifulSoup
import re

# ------------------------------------------------------------------------------
#                               GLOBAL VARIABLES
# ------------------------------------------------------------------------------

url = 'https://download.checklistbank.org/col/monthly/'

# ------------------------------------------------------------------------------
#                               UTILITY FUNCTIONS
# ------------------------------------------------------------------------------

def download_file(filename, base_url, out_dir):
  """
  Download a file from a given base URL to an output folder.
  
  Args:
    filename: File to be downloaded (without directory)
    base_url: Base URL under which file is stored
    out_dir:  Output directory to write downloaded file.

  Returns:
    Local path of the downloaded file.
  """
  if not os.path.exists(out_dir):
    print(f'[ERROR] Directory does not exist: {out_dir}.')
    sys.exit(1)

  # build URL to download from
  url_dl = f'{base_url}/{filename}'
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
@click.option('--version-file', help='Current version of downloaded CoL data.')
@click.option('--out-dir', required=True, help='Output directory to download to.')
def main(version_file, out_dir):
  """Download Catalogue of Life (CoL) resources."""
  version = ''
  # read version file if given
  if version_file:
    with open(version_file, 'rt') as f:
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
    fn_out = download_file(web_version, url, out_dir)
    print(f'Download successful. Find new data at:\n{os.path.join(out_dir, web_version)}')
    if version_file:
      print(f'Storing latest version in version file {version_file}.')
      with open(version_file, 'wt') as f:
        f.write(f'{web_version}\n')
      print(f'Writing sentinel file: "{fn_out}.new".')
      with open(f'{fn_out}.new', 'wt') as f:
        pass
  else:
    print(f'Already on latest version:\n{web_version}')
    print()
    print('Doing nothing.')
  

if __name__ == '__main__':
  main()
