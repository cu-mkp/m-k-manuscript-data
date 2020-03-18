# Last Updated | 2020-03-18
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

def update_all_folios(manuscript: BnF) -> None:
  """
  Update /m-k-manuscript-data/allFolios/ with the current manuscript from /ms-xml/. 

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
  for b in [True, False]:
    for version in versions:
      text = ''
      folder = 'xml' if b else 'txt'

      for identity, entry in manuscript.entries.items():
        new_text = entry.text(version, xml=b)
        text = f'{text}\n\n{new_text}' if text else new_text

      f = open(f'{m_path}/allFolios/{folder}/all_{version}.{folder}', 'w')
      f.write(text)
      f.close()

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

  manuscript = BnF(apply_corrections=False)

  update_all_folios(manuscript)
  print('Updated /allFolios/')

  update_time()

update()
