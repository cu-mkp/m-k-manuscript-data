# Last Updated | 2020-03-25
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

def is_continued(entry: Recipe) -> bool:
  return all('continued="yes"' in entry.text(v, True) for v in versions)

def is_parts(entry: Recipe) -> bool:
  return all('part="y"' in entry.text(v, True) for v in versions)

def get_margin_placements(entry: Recipe) -> str:
  return [margin.position for margin in entry.margins['tl']]

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
  df['heading_tc'] = df.entry.apply(lambda x: x.title['tc'])
  df['heading_tcn'] = df.entry.apply(lambda x: x.title['tcn'])
  df['heading_tl'] = df.entry.apply(lambda x: x.title['tl'])
  df['categories'] = df.entry.apply(lambda x: (';'.join(x.categories)))
  df['continued'] = df.entry.apply(lambda x: is_continued(x))
  df['parts'] = df.entry.apply(lambda x: is_parts(x))
  df['margins'] = df.entry.apply(lambda x: ' '.join(get_margin_placements(x)))
  print(manuscript.entry('053v_1').get_prop('currency', 'tl'))
  for prop in properties:
    for version in versions:
      key = f'{prop}_{version}'
      # print(key)
      for iden, entry in manuscript.entries.items():
        val = entry.get_prop(prop, version)
        try:
          val = (' '.join(val))
        except:
          print(iden)
      # df[key] = df.entry.apply(lambda x: str(';'.join(x.get_prop(prop, version))))
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
