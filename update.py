# Last Updated | 2020-08-21
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
              'music', 'plant', 'place', 'personal_name', 'profession', 'sensory', 'tool', 'time', 'weapon',
              'german', 'greek', 'italian', 'latin', 'occitan', 'poitevin']
prop_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'df',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp', 'weapon': 'wp',
              'german': 'de', 'greek': 'el', 'italian': 'it', 'latin': 'la', 'occitan': 'oc', 'poitevin': 'po',}

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
  # create DataFrame (spreadsheet) with one entry per row
  df = pd.DataFrame(columns=['entry'], data=manuscript.entries.values())
  df['folio'] = df.entry.apply(lambda x: x.folio)
  df['folio_display'] = df.entry.apply(lambda x: x.folio.lstrip('0'))
  df['div_id'] = df.entry.apply(lambda x: x.identity)
  df['categories'] = df.entry.apply(lambda x: (';'.join(x.categories)))
  df['heading_tc'] = df.entry.apply(lambda x: x.find_title(x.versions['tc'], remove_del_text=True))
  df['heading_tcn'] = df.entry.apply(lambda x: x.find_title(x.versions['tcn'], remove_del_text=True))
  df['heading_tl'] = df.entry.apply(lambda x: x.find_title(x.versions['tl'], remove_del_text=True))

  for prop, tag in prop_dict.items():
    for version in versions:
      df[f'{tag}_{version}'] = df.entry.apply(lambda x: '; '.join(x.get_prop(prop=prop, version=version)))
  # remove entry column, since it only displays memory address
  df.drop(columns=['entry'], inplace=True)

  df.to_csv(f'{m_path}/metadata/entry_metadata.csv', index=False)

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

  for version in versions:
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

def update_all_folios(manuscript: BnF) -> None:
  """
  Update /m-k-manuscript-data/allFolios/ with the current manuscript from /ms-xml/.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
  for b in [True, False]: # xml and txt respectively
    for version in versions:
      text = ''
      folder = 'xml' if b else 'txt'

      # add text entry by entry, with two line breaks in between each
      for identity, entry in manuscript.entries.items():
        new_text = entry.text(version, xml=b)
        text = f'{text}\n\n{new_text}' if text else new_text

      # write file
      f = open(f'{m_path}/allFolios/{folder}/all_{version}.{folder}', 'w')
      f.write(text)
      f.close()

def update_ms(manuscript: BnF) -> None:
  """
  Update /m-k-manuscript-data/update_ms/ with the current manuscript from /ms-xml/.
  Iterate through /ms-xml/ for each version, remove tags, and save to /ms-txt/.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
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

  manuscript = BnF(apply_corrections=False)

  print('Updating metadata')
  update_metadata(manuscript)

  print('Updating entries')
  update_entries(manuscript)

  print('Updating ms-txt')
  update_ms(manuscript)

  print('Updating allFolios')
  update_all_folios(manuscript)

  update_time()

if __name__ == "__main__":
  update()
