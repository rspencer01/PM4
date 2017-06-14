import hashlib
import os
import cPickle as pickle
import numpy as np

if not os.path.exists('./_assets'):
  os.mkdir('./_assets')

def getInternalAssetID(assetID):
  return hashlib.sha256(repr(assetID)).hexdigest()[:16]

def getFilename(assetID):
  return './_assets/{}'.format(assetID)

def loadFromFile(filename):
  try:
    return np.load(filename)
  except IOError as e:
    pass
  try:
    return pickle.load(open(filename, 'rb'))
  finally:
    pass
  raise Exception("Unknown format.")

def saveToFile(obj, filename):
  if type(obj) in [np.array]:
    np.save(filename, obj)
  else:
    pickle.dump(obj, open(filename, 'wb'))

def getAsset(assetID, function=None, args=(), forceReload=False):
  assetID = getInternalAssetID(assetID)
  if forceReload and function is None:
    raise Exception("Must specify generation function if reloading asset.")

  filename = getFilename(assetID)
  if os.path.exists(filename) and not forceReload:
    return loadFromFile(filename)

  obj = function(*args)

  saveToFile(obj, filename)

  return obj
