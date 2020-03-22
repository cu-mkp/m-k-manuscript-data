# Last Updated | 2020-03-21
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

def update_metadata(manuscript: BnF) -> None:
  """
  Update /m-k-manuscript-data/metadata/entry_metadata.csv with the current manuscript. Create a Pandas DataFrame
  indexed by entry. Create data columns, and remove the column that contains the entry objects. Save File.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
  df = pd.DataFrame(columns=['entry'], data=manuscript.entries.values())
  df['folio'] = df.entry.apply(lambda x: x.folio)
  df['folio_display'] = df.entry.apply(lambda x: x.folio.lstrip('0'))
  df['div_id'] = df.entry.apply(lambda x: x.identity)
  df['categories'] = df.entry.apply(lambda x: (';'.join(x.categories)))
  df['heading_tc'] = df.entry.apply(lambda x: x.title['tc'])
  df['heading_tcn'] = df.entry.apply(lambda x: x.title['tcn'])
  df['heading_tl'] = df.entry.apply(lambda x: x.title['tl'])
  df['margins'] = df.entry.apply(lambda x: len(x.margins))
  df['del_tags'] = df.entry.apply(lambda x: '; '.join(x.del_tags))
  for prop in properties:
    for version in versions:
      df[f'{prop}_{version}'] = df.entry.apply(lambda x: '; '.join(x.get_prop(prop=prop, version=version)))
  df.drop(columns=['entry'], inplace=True)

  df.to_csv(f'{m_path}/metadata/entry_metadata.csv', index=False)

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

  update_metadata(manuscript)
  print('Updated metadata.')

  update_time()

update()
