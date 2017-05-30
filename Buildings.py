import Terrain
import logging
import Shaders
import numpy as np
import Object
import random
import OpenGL.GL as gl
from transforms import *

positions = [[0, 0, -2938]]
for _ in xrange(10):
  positions.append([random.randint(-200, 200),
                    0,
                    random.randint(-3200, -2700)])
for position in positions:
  position[1] = Terrain.getAt(position[0], position[2])

building = \
  Object.Object(
    'assets/house1/PMedievalHouse.FBX',
    'House',
    scale=0.0012,
    offset=(3.4, 0, -6))

pagingShader = Shaders.getShader('buildingPaging', forceReload=True)
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
pagingRenderID = pagingShader.setData(data,indices)

def flattenGround(x, y, width, height):
  """This function writes to the paged texture to flatten the ground underneath
  the buildings."""
  for position in positions:
    model = np.eye(4, dtype=np.float32)
    scale(model, 15, 20, 1)
    translate(model, position[0], position[2]);
    translate(model, 30000 - y - height/2, x +width/2- 30000 );
    scale(model, 1.6/width, -1.6/height, 1)

    pagingShader.load()
    pagingShader['model'] = model
    pagingShader['level'] = position[1] - 1000
    pagingShader.draw(gl.GL_TRIANGLES, pagingRenderID)

Terrain.registerCallback(flattenGround)

def display():
  for position in positions:
    building.position = position
    building.display()
