import numpy as np
import args
import Image
import logging
from Shaders import *
import OpenGL.GL as gl
import Texture
import RenderStage
import noiseG
from math import *
import os
import sys
from configuration import config
from pagedTextures import *
import tqdm

logging.info("Constructing Terrain")

planetSize              = 60000
patches                 = config.terrain_num_patches
patchSize               = planetSize/patches
logging.info(" + {:d} (={:d}x{:d}) patches at {:d}m on a side".format((patches-1)**2,patches-1,patches-1,patchSize))

updateUniversalUniform('heightmap', Texture.HEIGHTMAP_NUM)
updateUniversalUniform('worldSize', planetSize)

# Construct patches
logging.info(" + Constructing geometry")
patchData = np.zeros((patches-1)**2*6,dtype=[("position" , np.float32,3)])
for i in range(patches-1):
  for j in range(patches-1):
    patchData['position'][(i*(patches-1)+j)*6] = (i,0,j)
    patchData['position'][(i*(patches-1)+j)*6+1] = (i,0,j+1)
    patchData['position'][(i*(patches-1)+j)*6+2] = (i+1,0,j)
    patchData['position'][(i*(patches-1)+j)*6+3] = (i+1,0,j)
    patchData['position'][(i*(patches-1)+j)*6+4] = (i,0,j+1)
    patchData['position'][(i*(patches-1)+j)*6+5] = (i+1,0,j+1)
patchData['position']=(patchData['position']-np.array([patches/2,0,patches/2]))*patchSize
patchIndices = np.array([],dtype=np.int32)

# Set up renderer
shader = getShader('terrain',tess=True,geom=False,forceReload=True)
shader['model'] = np.eye(4,dtype=np.float32)
shader['colormap'] = Texture.COLORMAP_NUM
renderID = shader.setData(patchData, patchIndices)

# Texture sizes
heightmap = Texture.Texture(Texture.HEIGHTMAP)
textWidth = 800
textRes = float(planetSize) / textWidth
logging.info(" + Heightmap texture size {:d}x{:d} for a resolution of {:.1f}m per pixel".format(textWidth,textWidth,textRes))
textHeight = textWidth
sign = lambda x: 1 if x>0 else -1
if not os.path.exists('terrain.npy') or args.args.remake_terrain:
  d = np.zeros((textWidth,textHeight,4), dtype=np.float32)
  logging.info(" + Calculating heightmap")
  im = Image.open("assets/Cederberg Mountains Height Map (Merged).png")
  im.thumbnail((textHeight,textWidth),Image.ANTIALIAS)
  pix = im.load()
  for i in range(textWidth):
    for j in range(textHeight):
      t = pix[i,j]
      d[textWidth-1-i,j] = (t,t,t,t)

  # Normalize to 0-1 range
  d -= np.min(d)
  d /= np.max(d)
  d *= 1920

  if args.args.monolith:
    for i in xrange(20):
      for j in xrange(20):
        d[d.shape[0]/2+i][d.shape[1]/2+j] = 3e3

  # Boundary conditions
  for i in xrange(textWidth):
    d[i,0] = -1000
    d[i,-1] = -1000
  for i in xrange(textHeight):
    d[0,i] = -1000
    d[-1,i] = -1000

  logging.info(" + Calculating normalmap")
  for i in tqdm.trange(textWidth-1, leave=False):
    for j in range(textHeight-1):
      v1= np.array([float(i  )/textWidth*planetSize  , d[i,j][3]   , float(j  )/textWidth*planetSize])
      v2= np.array([float(i+1)/textWidth*planetSize  , d[i+1,j][3] , float(j  )/textWidth*planetSize])
      v3= np.array([float(i  )/textWidth*planetSize  , d[i,j+1][3] , float(j+1)/textWidth*planetSize])
      d[i,j][:3] = np.cross(v3-v1,v2-v1)
  np.save('terrain.npy',d)
  del im
else:
  d=np.load('terrain.npy')

heightmap.loadData(d, keep_copy=True)

logging.info(" + Loading textures")

texture = Texture.Texture(Texture.COLORMAP)
colorMapSize = 1000
texData = np.zeros((colorMapSize,colorMapSize,4),dtype=np.float32)

a = Image.open('textures/grass.jpg')
a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
grass = np.array(a.getdata()).astype(np.float32)

add = np.zeros((grass.shape[0],1),dtype=np.float32)
grass = np.append(grass,add,axis=1)
grass = np.array([grass[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

a = Image.open('textures/dirt.jpg')
a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
dirt = np.array(a.getdata()).astype(np.float32)
add = np.zeros((dirt.shape[0],1),dtype=np.float32)
dirt = np.append(dirt,add,axis=1)
dirt = np.array([dirt[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

a = Image.open('textures/stone.jpg')
a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
stone = np.array(a.getdata()).astype(np.float32)
add = np.zeros((stone.shape[0],1),dtype=np.float32)
stone = np.append(stone,add,axis=1)
stone = np.array([stone[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256


texData[0:colorMapSize/2,0:colorMapSize/2] = grass
texData[0:colorMapSize/2,colorMapSize/2:] = stone
texData[colorMapSize/2:,0:colorMapSize/2] = dirt
texture.loadData(texData)
del texData


def display(camera):
  if np.sum(camera.position*camera.position) > 6e6**2:
    return
  shader.load()
  texture.load()
  heightmap.load()
  shader.draw((patches-1)**2*6,renderID)

def getCurvature(x, y):
  x,y = float(x), float(y)
  c = heightmap.read(x/planetSize,      y/planetSize)[3]
  d = heightmap.read((x+10)/planetSize, y/planetSize)[3]+\
      heightmap.read(x/planetSize,      (y+10)/planetSize)[3]+\
      heightmap.read((x-10)/planetSize, y/planetSize)[3]+\
      heightmap.read(x/planetSize,      (y-10)/planetSize)[3];
  d/=4;
  return c-d if c>d else d-c;

def getFineAmount(x, y):
  s = heightmap.read(float(x)/planetSize, float(y)/planetSize)
  s[:3] /= s[:3].dot(s[:3])**0.5
  theta = acos(s[1])
  if theta < 0.4:
      return 30
  return 30 + (theta - 0.4)*100 + 10*(theta-0.4)*getCurvature(x,y);

def getAt(x,y):
  x += planetSize / 2
  y += planetSize / 2
  s = heightmap.read(float(x)/planetSize, float(y)/planetSize)[3] + 1000

  offset = noiseG.noiseTexture.read(x/1000., y/1000.)[3] * getFineAmount(x, y)

  return s + offset

def getGradAt(x,y):
  dx = (getAt(x+0.1,y)-getAt(x,y))/0.1
  dy = (getAt(x,y+0.1)-getAt(x,y))/0.1
  return [dx,dy]

