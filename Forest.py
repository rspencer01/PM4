import numpy as np
import os
import sys
import logging
import random
import noiseG
import MultiObject
import args
import Terrain

logger = logging.getLogger('PM4')

logging.info("Loading trees")

planetSize = 60000
patches = 100
patchSize = planetSize/patches
treesPerPatchSide = 4
textSize = 1000

logging.info("{:d} ({:d}x{:d}) patches at {:d}m on a side".format(
  (patches-1)**2,
  patches-1,
  patches-1,
  patchSize))
logging.info("Maximum {:d} trees per patch".format(treesPerPatchSide**2))
logging.info("Maximum {:d} total trees".format(treesPerPatchSide**2 * patches**2))

tree = MultiObject.MultiObject('assets/tree5/Conifers tree 1 N1006162.3DS', patches-1, scale=20)

logging.info(" + Creating trees")
totalTrees = 0
if not os.path.exists('trees.npy') or args.args.remake_trees:
  data = -1000004*np.ones((patches-1, patches-1, treesPerPatchSide**2, 3), dtype=float)
  for i in xrange(patches-1):
    sys.stdout.write(str(i)+" / "+str(patches-1))
    sys.stdout.write('\r')
    sys.stdout.flush()
    for j in xrange(patches-1):
      c = 0
      for ii in xrange(treesPerPatchSide):
        for ij in xrange(treesPerPatchSide):
          posx = i*patchSize - planetSize/2 +ii*patchSize/treesPerPatchSide+random.random()*patchSize/treesPerPatchSide*0.9
          posy = j*patchSize - planetSize/2 +ij*patchSize/treesPerPatchSide+random.random()*patchSize/treesPerPatchSide*0.9
          if sum(map(lambda x: x**2, Terrain.getGradAt(-posx, -posy))) > 0.4:
            continue
          if noiseG.get(posx/30000.0, posy/30000.0)[3]**2 < 0.07:
            continue
          totalTrees += 1
          data[i, j, c, :] = np.array([posx, 0, posy])
          c += 1
  np.save('trees.npy', data)
else:
  logging.info("Loading from file")
  data = np.load('trees.npy')

textData = np.zeros((textSize, textSize, 4), dtype=np.float32)

startIndex = 0
totalTrees = 0
for i in xrange(patches-1):
  for j in xrange(patches-1):
    k = 0
    while (k < treesPerPatchSide**2 and data[i, j, k][0] >= -1000000):
      k += 1
    startIndex = tree.addSwatch((i, j), startIndex, data[i, j, :k])
    for t in data[i, j, :k]:
      xx = textSize*(t[0]+30000)/60000
      yy = textSize*(t[2]+30000)/60000
      textData[xx, yy][0] = 1
logging.info(" + Total trees {:d}".format(totalTrees))
tree.freeze()
logging.info(" + Created trees")
del data

def display(pos, shadows=False):
  tree.display(pos, shadows)
