import logging
import numpy as np
import dent.Texture as Texture
from dent.args import args
from dent.Shaders import *
from dent.configuration import config

logging.info("Loading grass")

texture = Texture.Texture(Texture.COLORMAP)
if not args.whitewash:
  texture.loadFromImage('assets/grass.png')
else:
  texture = Texture.getWhiteTexture()

numberOfPatches = int(100 * config.grass_amount)
patchSize = .3
logging.info(" {:d} ({:d}x{:d}) patches at {:.3f}m on a side".format(
  (numberOfPatches)**2,
  numberOfPatches,
  numberOfPatches,
  patchSize))

data = np.zeros(numberOfPatches**2,dtype=[("position" , np.float32,3),
                                          ("occlusion" , np.float32,3)])
count = 0
for i in range(-numberOfPatches/2, numberOfPatches/2):
  for j in range(-numberOfPatches/2, numberOfPatches/2):
    if i**2 + j**2 < (numberOfPatches/2)**2:
      data['position'][count] = (i * patchSize, 0, j * patchSize)
      if i**2 + j**2 > (numberOfPatches/3)**2:
        data['occlusion'][count] = ((i**2 + j**2)**0.5 - numberOfPatches/3) / (numberOfPatches/6)
      else:
        data['occlusion'][count] = 0
      count += 1

data = data[:count]
logging.info(" Due to circular, only {} grass patches".format(count))

indices = np.array(range(count), dtype=np.int32)

shader = getShader('grass3', geom=True)
shader['patchSize'] = patchSize
shader['colormap'] = Texture.COLORMAP_NUM

renderID = shader.setData(data,indices)

def display(cam):
  if abs(cam.position[0]) > config.world_size or \
     abs(cam.position[2]) > config.world_size or \
     cam.position[1]>4e3:
    return
  texture.load()
  shader.load()
  shader.draw(gl.GL_POINTS, renderID, numberOfPatches**2)
