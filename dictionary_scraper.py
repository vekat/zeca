import re, sys, requests, pprint

import html2text

from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from unidecode import unidecode

from word import Word, Entry

headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

h2t = html2text.HTML2Text()
h2t.ignore_images = True


def dicio(raw_input):
  clean_input = quote_plus(raw_input)
  url = f'https://www.dicio.com.br/pesquisa.php?q={clean_input}'
  res = requests.get(url, headers=headers)

  if res.status_code >= 400:
    return None

  soup = BeautifulSoup(res.content, 'html.parser')
  card = soup.select('#content .card')[0]
  heading = card.find('h1')

  if heading.has_attr('class') and not heading.has_attr('itemprop'):
    results = card.select('.resultados li a')

    if not results or len(results) == 0:
      return None

    suggestion = results[0]['href']
    url = f'https://www.dicio.com.br{suggestion}'
    res = requests.get(url, headers=headers)

    if res.status_code >= 400:
      return None

    soup = BeautifulSoup(res.content, 'html.parser')
    card = soup.select('#content .card')[0]
    heading = card.find('h1', attrs={'itemprop': 'name'})

  term = heading.get_text().strip()
  funcs = {}
  current_func = 0
  func_definitions = {}

  tags = card.select('.significado > span:not(.etim):not(.cl-block)')

  for tag in tags:
    if tag.has_attr('class') and 'cl' in tag.attrs['class']:
      current_func = current_func + 1
      func_name = tag.get_text().strip()
      funcs[current_func] = func_name
      if current_func not in func_definitions:
        func_definitions[current_func] = []
      continue

    definition = h2t.handle(str(tag)).strip()
    definition = re.sub(r'[\n\s•]+', ' ', definition)

    if current_func == 0:
      current_func = current_func + 1
      func_name = 'sem categoria'
      funcs[current_func] = func_name
      func_definitions[current_func] = []

    func_definitions[current_func].append(definition)

  entry = Entry({'br': term}, funcs, func_definitions)

  return Word(term, [entry], url)


def priberam(raw_input):
  clean_input = unidecode(raw_input)
  url_input = quote_plus(clean_input)
  url = f'https://www.priberam.pt/dlpo/dlpo.aspx?pal={url_input}'
  res = requests.get(url, headers=headers)

  if res.status_code >= 400:
    return None

  soup = BeautifulSoup(res.content, 'html.parser')
  div = soup.find('div', id='resultados')
  content = div.find('div', class_='pb-sugestoes-afastadas')

  if content:
    results = content.select('.resultados a')

    if not results or len(results) == 0:
      return None

    suggestion = results[0]['href']
    url = f'https://dicionario.priberam.org{suggestion}'
    res = requests.get(url, headers=headers)

    if res.status_code >= 400:
      return None

    soup = BeautifulSoup(res.content, 'html.parser')
    div = soup.find('div', id='resultados')

  content = div.select('div > div:last-child')[0]
  entry_divs = content.select('br + div')
  entries = []

  for tdiv in entry_divs:
    terms = {}
    funcs = {}
    current_func = 0
    func_definitions = {}

    termpt = tdiv.select('.varpt > span > b')[0].get_text()
    termpt = re.sub(r'·', '', termpt)
    terms['pt'] = termpt

    termbr = tdiv.select('.varpb > span > b')[0].get_text()
    termbr = re.sub(r'·', '', termbr)
    terms['br'] = termbr

    tdefs = tdiv.select(
        'p > span:not(.def) + .def, .varpt > div:not(.aAO), .varpt + p > .def'
    )

    for tdef in tdefs:
      p = tdef.parent

      if p.name == 'span':
        current_func = current_func + 1
        func_name = p.select('div:not(.aAO)')[0].get_text().strip()
        funcs[current_func] = func_name
        if current_func not in func_definitions:
          func_definitions[current_func] = []
        continue

      for span in p.find_all('span', class_='varpb'):
        span.decompose()

      definition = re.sub(r'[\n\s•]+', ' ', p.get_text().strip())
      definition = re.sub(r'^\d+\.\s*', '', definition)

      if current_func == 0:
        current_func = current_func + 1
        func_name = 'sem categoria'
        funcs[current_func] = func_name
        func_definitions[current_func] = []

      func_definitions[current_func].append(definition)

    entry = Entry(terms, funcs, func_definitions)
    entries.append(entry)

  return Word(clean_input, entries, url)


if __name__ == '__main__':
  try:
    if sys.argv[1] == 'd':
      print(dicio(sys.argv[2]))
    else:
      print(priberam(sys.argv[2]))
  except Exception as err:
    print('error', err)
