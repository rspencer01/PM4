import hashlib
import os
import cPickle as pickle
import numpy as np
import logging

if not os.path.exists('./_assets'):
  os.mkdir('./_assets')

def getInternalAssetID(assetID):
  return hashlib.sha256(repr(assetID)).hexdigest()[:16]

def getFilename(assetID):
  return './_assets/{}'.format(assetID)

def loadFromFile(filename):
  try:
    obj = np.load(filename+'.npy')
    logging.info("Loaded object as numpy array")
    return obj
  except IOError as e:
    pass
  try:
    obj = pickle.load(open(filename, 'rb'))
    logging.info("Loaded object as python pickle")
    return obj
  finally:
    pass
  raise Exception("Unknown format.")

def saveToFile(obj, filename):
  if type(obj) in [np.ndarray]:
    logging.info("Saving object as numpy array")
    np.save(filename, obj)
  else:
    logging.info("Saving object as python pickle")
    pickle.dump(obj, open(filename, 'wb'))

def getAsset(assetID, function=None, args=(), forceReload=False):
  logging.info("Loading asset '{}'".format(assetID))
  assetID = getInternalAssetID(assetID)
  if forceReload and function is None:
    raise Exception("Must specify generation function if reloading asset.")

  filename = getFilename(assetID)
  if os.path.exists(filename) or os.path.exists(filename+'.npy') and not forceReload:
    return loadFromFile(filename)

  obj = function(*args)

  saveToFile(obj, filename)

  return obj
