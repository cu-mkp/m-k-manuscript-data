# Last Updated | 2020-03-24
# Python Modules
import os
import sys
import re
from typing import List

sys.path.insert(1, './manuscript-object/')

# Third Party Modules
import pandas as pd
from datetime import datetime

# Local Modules
from digital_manuscript import BnF
from recipe import Recipe

versions = ['tc', 'tcn', 'tl']
properties = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name', 'profession', 'sensory', 'tool', 'time', 'weapon']

m_path = f'{os.getcwd()}'

def update_entries(manuscript: BnF) -> None:
  """
  Update /m-k-manuscript-data/entries/ with the current manuscript from /ms-xml/. For each version, delete all existing
  entries. Regenerate folio text entry by entry, and save the file. 

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """

  for path in [f'{m_path}/entries', f'{m_path}/entries/txt', f'{m_path}/entries/xml']:
    if not os.path.exists(path):
      os.mkdir(path)

  for version in versions: # TODO: fix this when you're done with the body
    txt_path = f'{m_path}/entries/txt/{version}'
    xml_path = f'{m_path}/entries/xml/{version}'

    # If the entries/txt or xml directory does not exist, create it. Otherwise, clear the directory.
    for path in [txt_path, xml_path]:
      if not os.path.exists(path):
        os.mkdir(path)
      elif len(os.listdir(path)) > 0: # remove existing files
        for f in os.listdir(path):
          os.remove(os.path.join(path, f))

    # Write new files with manuscript object
    for identity, entry in manuscript.entries.items():
      if identity: # TODO: resolve issue of unidentified entries
        # TODO: ask for a naming convention
        filename_txt = f'{txt_path}/{version}_{entry.identity}.txt'
        filename_xml = f'{xml_path}/{version}_{entry.identity}.xml'

        content_txt = entry.text(version, xml=False)
        content_xml = entry.text(version, xml=True)

        f_txt = open(filename_txt, 'w')
        f_txt.write(content_txt)
        f_txt.close()

        f_xml = open(filename_xml, 'w')
        f_xml.write(content_xml)
        f_xml.close()

def update_time():
  """ Extract timestamp at the top of this file and update it. """
  # Initialize date to write and container for the text
  now_str = str(datetime.now()).split(' ')[0]
  lines = []

  # open file, extract text, and modify
  with open('./update.py', 'r') as f:
    lines = f.read().split('\n')
    lines[0] = f'# Last Updated | {now_str}'
  
  # write modified text
  f = open('./update.py', 'w')
  f.write('\n'.join(lines))
  f.close

def update():

  manuscript = BnF(apply_corrections=True)

  update_entries(manuscript)
  print('Updated /entries/')

  update_time()

update()
