import time
import random
random.seed(0)

class Pager(object):
  def __init__(self, size):
    self.mapping = {}
    self.available_indices = set(range(size))


  def remove_oldest(self):
    oldest = sorted(self.mapping.items(),key = lambda x: x[1][0])[0][0]
    self.remove(oldest)


  def remove(self, item):
    if item not in self: return
    self.available_indices.add(self.mapping[item][1])
    del self.mapping[item]


  def add(self, item):
    if len(self.available_indices) == 0:
      self.remove_oldest()
    index = random.choice(list(self.available_indices))
    self.available_indices.remove(index)
    self.mapping[item] = (time.time(), index)
    return index


  def __getitem__(self, item):
    v = self.mapping[item][1]
    self.mapping[item] = (time.time(),v)
    return v


  def __contains__(self, item):
    return item in self.mapping


  def __len__(self):
    return len(self.mapping)


  def clear(self):
    while len(self):
      self.remove_oldest()
