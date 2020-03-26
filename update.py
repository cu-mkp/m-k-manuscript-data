<<<<<<< HEAD
# Last Updated | 2020-03-25
=======
# Last Updated | 2020-03-26
>>>>>>> update-infra
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

def update_ms(manuscript: BnF) -> None:
  for version in versions: 
    for r, d, f in os.walk(f'{m_path}/ms-xml/{version}'):
      for filename in f: # iterate through /ms-xml/{version} folder
        # read xml file
        text = ''
        filepath = f'{m_path}/ms-xml/{version}/{filename}'
        with open(filepath, encoding="utf-8", errors="surrogateescape") as f:
          text = f.read()
        
        # remove xml, normalize whitespace
        text = text.replace('\n', '**NEWLINE**')
        text = re.sub(r'<.*?>', '', text)
        text = text.replace('**NEWLINE**', '\n')
        text = text.strip(' \n')

        # write txt file
        txt_filepath = filepath.replace('xml', 'txt')
        f = open(txt_filepath, 'w')
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

  manuscript = BnF(apply_corrections=True)

  update_ms(manuscript)
  print('Updated /ms-txt/')

  update_time()

update()
