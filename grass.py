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
patchSize = 1.
logging.info(" + {:d} ({:d}x{:d}) patches at {:f}m on a side".format((numberOfPatches)**2,numberOfPatches,numberOfPatches,patchSize))

data = np.zeros(numberOfPatches**2,dtype=[("position" , np.float32,3)])
for i in range(numberOfPatches):
  for j in range(numberOfPatches):
    data['position'][i*numberOfPatches+j] = (i,0,j)
data['position']=(data['position']-np.array([numberOfPatches/2,0,numberOfPatches/2]))*patchSize
indices = np.array(range(numberOfPatches**2),dtype=np.int32)

shader = getShader('grass3',geom=True,forceReload=True)
Terrain.setTerrainUniforms(shader)
shader['patchSize'] = patchSize
shader['colormap'] = Texture.COLORMAP_NUM

renderID = shader.setData(data,indices)

def display(cam):
  if np.sum(cam.pos*cam.pos) > 6e4**2 or cam.pos[1]>4e3:
    return
  texture.load()
  shader.load()
  shader.draw(gl.GL_POINTS, renderID, numberOfPatches**2)
