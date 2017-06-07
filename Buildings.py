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
from configuration import config
import Road
import tqdm

BuildingSpec = namedtuple('BuildingSpec', ('position','angle', 'direction', 'bidirection'))
ClumpSpec = namedtuple('ClumpSpec', ('position', 'buildings'))

clumpCount = config.building_clump_count
if clumpCount > 100:
  logging.warn("Requested more than 100 building clumps.  Clamping")
  clumpCount = 100
minClumpSize = config.building_clump_min_size
maxClumpSize = config.building_clump_max_size
logging.info("Creating {} clumps of buildings".format(clumpCount))

Shaders.updateUniversalUniform('villageCount', clumpCount)

clumpSpecs = []
for _ in xrange(clumpCount):
  gr = [100,100]
  while gr[0]**2 + gr[1]**2 >1:
    clumpPosition = np.array([random.randint(-30000,30000), 0,
                     random.randint(-30000,30000)])
    clumpPosition[1] = Terrain.getAt(clumpPosition[0], clumpPosition[2])
    gr = Terrain.getGradAt(clumpPosition[0], clumpPosition[2])
  buildings = []
  for _ in xrange(random.randint(minClumpSize, maxClumpSize)):
    pos = [random.randint(-200, 200)+clumpPosition[0],
           0,
           random.randint(-200, 200)+clumpPosition[2]]
    pos[1] = Terrain.getAt(pos[0], pos[2])
    angle = random.random()*2*3.14
    direction = [np.sin(angle),0.,np.cos(angle)]
    bidirection = [np.cos(angle),0.,-np.sin(angle)]
    spec = BuildingSpec(pos, angle, direction, bidirection)
    buildings.append(spec)
  spec = ClumpSpec(clumpPosition, buildings)
  clumpSpecs.append(spec)

Shaders.updateUniversalUniform('villagePosition', np.array([
  i.position for i in clumpSpecs
  ]))

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

logging.info("Generating roads connecting villages")
roads = []
for i in tqdm.trange(len(clumpSpecs), leave=False):
    p = sorted(clumpSpecs, key=lambda c: np.linalg.norm(clumpSpecs[i].position-c.position))
    for j in p[1:4]:
        roads.append(Road.Road(
            (clumpSpecs[i].position[0], clumpSpecs[i].position[2]),
            (j.position[0], j.position[2])))

def flattenGround(x, y, width, height):
  """This function writes to the paged texture to flatten the ground underneath
  the buildings."""
  for clump in clumpSpecs[:5]:
    for spec in clump.buildings:
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
  stepSort('buildingsClumpDistance', clumpSpecs, key=lambda x: np.linalg.norm(x.position-camera.position))
  for clump in clumpSpecs[:3]:
    for spec in clump.buildings:
      building.position    = spec.position
      building.direction   = spec.direction
      building.bidirection = spec.bidirection
      building.display()
