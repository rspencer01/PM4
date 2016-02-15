import numpy as np
import random
import Image
import Camera 
import noiseG
import MultiObject
from pyassimp import *

print "Loading trees"

import Terrain
import Texture 
from transforms import *
from Shaders import *

class Tree(MultiObject.MultiObject):
  def __init__(self):
    super(Tree,self).__init__(80)

tree1 = Tree()
tree1.loadFromScene('assets/tree1/Tree N110314.3DS',scale=50)
#tree1.loadFromScene('assets/bush1/Bush 1 N230814.3DS',scale=0.1)

startIndex = 0
for i in xrange(80):
  for j in xrange(80):
    points = []
    for ii in xrange(3):
      for ij in xrange(3):
        posx = i*100 - 4000 +ii*(8000/80)/3+random.random()*30
        posy = j*100 - 4000 +ij*(8000/80)/3+random.random()*30
        if sum(map(lambda x:x**2,Terrain.getGradAt(-posx,-posy)))>0.4:
          continue;
        if noiseG.get(posx/30000.0, posy/30000.0)[3]**2 < 0.01:
          continue
        points.append([-posx,Terrain.getAt(-posx,-posy)[3]+9,-posy])

    startIndex = tree1.addSwatch((i,j),startIndex,points)

tree1.freeze()
def display(pos,shadows=False):
  tree1.display(pos,shadows)
