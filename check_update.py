# Last Updated | 2019-11-10

import os
from datetime import datetime

import pandas as pd

def check_time():
  now = datetime.strptime(str(datetime.now()).split(' ')[0], '%Y-%m-%d')
  with open('./update.py', 'r') as f:
    text = f.read()
    comment = text.split('\n')[0]
    timestamp = datetime.strptime(comment.split('|')[1].strip(), '%Y-%m-%d')

    if timestamp < now:
      print('The repository has not been updated since ' + str(timestamp) + '. Please run update.py on the day of merging the branch.')
      assert False

def check_metadata():
  dummy_metadata = './dummy/entry_metadata.csv'
  real_metadata = './metadata/entry_metadata.csv'

  dummy_df = pd.read_csv(dummy_metadata)
  dummy_df.fillna('', inplace=True)
  real_df = pd.read_csv(real_metadata)
  real_df.fillna('', inplace=True)

  if dummy_df.shape != real_df.shape:
    return False

  dummy_cols = dummy_df.columns
  real_cols = real_df.columns

  for i, col in enumerate(dummy_cols):
    if col != real_cols[i]:
      return False
  
  for i, row in dummy_df.iterrows():
    dummy_row = dummy_df.loc[i, : ]
    real_row = real_df.loc[i, : ]

    for j, col in enumerate(dummy_cols):
      dummy_cell = set(list(dummy_row[col]))
      real_cell = set(list(real_row[col]))

      if dummy_cell != real_cell:        
        return False

  return True

def check_all_folios():
  for folder in ['xml', 'txt']:
    for version in ['tc', 'tcn', 'tl']:
      real_file = f'./allFolios/{folder}/all_{version}.{folder}'
      dummy_file = f'./dummy/all_{version}.{folder}'

      real_text = ''
      with open(real_file) as rf:
        real_text = rf.read()

      dummy_text = ''
      with open(dummy_file) as df:
        dummy_text = df.read()

      if real_text != dummy_text:
        return False
  return True

def check_update():
  os.system('python update.py dummy')
  
  files = [f for f in os.listdir('.') if os.path.isfile(f)]
  for f in files:
    print(f)
  # passed = check_metadata() and check_all_folios()
  # if not passed:
  #   os.system('rm -r dummy')
  #   assert False

  os.system('rm -r dummy')

check_update()
