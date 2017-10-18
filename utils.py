stepSortIndices = {}

def stepSort(name, x, key=lambda x:x):
  global stepSortIndices
  if name not in stepSortIndices:
    stepSortIndices[name] = 1

  if len(x) <= 1: return
  i = stepSortIndices[name]

  if key(x[i]) < key(x[i-1]):
    x[i], x[i-1] = x[i-1], x[i]

  stepSortIndices[name] = (i + 1) % len(x)
  if stepSortIndices[name] == 0:
    stepSortIndices[name] = 1
