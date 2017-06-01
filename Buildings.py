import Terrain
import logging
import Shaders
import numpy as np
import Object
import random
from utils import stepSort
import OpenGL.GL as gl
from transforms import *
from collections import namedtuple

BuildingSpec = namedtuple('BuildingSpec', ('position','angle', 'direction', 'bidirection'))

specs = []
for _ in xrange(30):
  pos = [random.randint(-500, 500),
         0,
         random.randint(-3500, -2500)]
  pos[1] = Terrain.getAt(pos[0], pos[2])
  angle = random.random()*2*3.14
  direction = [np.sin(angle),0.,np.cos(angle)]
  bidirection = [np.cos(angle),0.,-np.sin(angle)]
  spec = BuildingSpec(pos, angle, direction, bidirection)
  specs.append(spec)

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
  for spec in specs:
    model = np.eye(4, dtype=np.float32)
    zrotate(model, spec.angle*180/3.14)
    scale(model, 6, 10, 1)
    translate(model, spec.position[0], spec.position[2]);
    translate(model, 30000 - y - height/2, x +width/2- 30000 );
    scale(model, 1.6/width, -1.6/height, 1)

    pagingShader.load()
    pagingShader['model'] = model
    pagingShader['level'] = spec.position[1] - 1000
    pagingShader.draw(gl.GL_TRIANGLES, pagingRenderID)

Terrain.registerCallback(flattenGround)

def display(camera):
  stepSort('buildingsDistance', specs, key=lambda x: np.linalg.norm(x.position-camera.position))
  for spec in specs[:10]:
    building.position = spec.position
    building.direction = spec.direction
    building.bidirection = spec.bidirection
    building.display()
