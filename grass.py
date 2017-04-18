import logging
from PIL import Image
import numpy as np
import Texture
from Shaders import *

logging.info("Loading grass")

texture = Texture.Texture(Texture.COLORMAP)
grass_image = Image.open('assets/grass.png')
texdata = np.array(grass_image.getdata()).astype(np.float32)
# Make this a 4 color file
if (texdata.shape[1]!=4):
  add = np.zeros((texdata.shape[0],1),dtype=np.float32)+256
  texdata = np.append(texdata,add,axis=1)
texdata = texdata.reshape(grass_image.size[0], grass_image.size[1], 4)
texture.loadData(texdata.shape[0],texdata.shape[1],texdata/256)

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
renderID = shader.setData(data,indices)

def display(cam):
  if np.sum(cam.pos*cam.pos) > 6e4**2 or cam.pos[1]>4e3:
    return
  texture.load()
  shader.load()
  shader['patchSize'] = patchSize
  shader['colormap'] = Texture.COLORMAP_NUM
  shader.draw(gl.GL_POINTS, renderID, numberOfPatches**2)
