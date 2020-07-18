class Word:
  def __init__(self, query, entries, source):
    self.query = query
    self.entries = entries
    self.source = source

  def __str__(self):
    entries = [str(e) for e in self.entries]
    return f'palavra: {self.query}\nfonte: {self.source}\n' + '\n'.join(entries)


class Entry:
  def __init__(self, terms, functions, definitions):
    self.terms = terms
    self.functions = functions
    self.definitions = definitions

  def __str__(self):
    return f'terms: {self.terms}\nfuncs: {self.functions}\ndefs: {self.definitions}'
