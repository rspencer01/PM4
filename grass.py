import logging
from PIL import Image
import numpy as np
import Texture
import Terrain
from Shaders import *

logging.info("Loading grass")

texture = Texture.Texture(Texture.COLORMAP)
texture.loadFromImage('assets/grass.png')

numberOfPatches = 100
patchSize = .3
logging.info(" + {:d} ({:d}x{:d}) patches at {:.3f}m on a side".format((numberOfPatches)**2,numberOfPatches,numberOfPatches,patchSize))

data = np.zeros(numberOfPatches**2,dtype=[("position" , np.float32,3),
                                          ("occlusion" , np.float32,3)])
count = 0
for i in range(-numberOfPatches/2, numberOfPatches/2):
  for j in range(-numberOfPatches/2, numberOfPatches/2):
    if i**2 + j**2 < (numberOfPatches/2)**2:
      data['position'][count] = (i,0,j)
      data['occlusion'][count] = 0
      if i**2 + j**2 > (numberOfPatches/3)**2:
        data['occlusion'][count] = ((i**2 + j**2)**0.5 - numberOfPatches/3) / (numberOfPatches/6)

      count += 1
data = data[:count]
logging.info(" + Due to circular, only {} grass patches".format(count))

data['position'] = data['position']*patchSize

indices = np.array(range(count),dtype=np.int32)

shader = getShader('grass3',geom=True,forceReload=True)
shader['patchSize'] = patchSize
shader['colormap'] = Texture.COLORMAP_NUM
shader['noisemap'] = Texture.NOISE_NUM

renderID = shader.setData(data,indices)

def display(cam):
  if np.sum(cam.position*cam.position) > 6e4**2 or cam.position[1]>4e3:
    return
  texture.load()
  shader.load()
  shader.draw(gl.GL_POINTS, renderID, numberOfPatches**2)
