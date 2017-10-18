import numpy as np
import dent.args as args
from PIL import Image
import logging
from dent.Shaders import *
import OpenGL.GL as gl
import dent.Texture as Texture
import noiseG
from math import *
from dent.configuration import config
from pagedTextures import *
import tqdm
import dent.assets as assets

logging.info("Constructing Terrain")

planetSize              = 60000
patches                 = config.terrain_num_patches
patchSize               = planetSize/patches
logging.info(" + {:d} (={:d}x{:d}) patches at {:d}m on a side".format((patches-1)**2,patches-1,patches-1,patchSize))

updateUniversalUniform('heightmap', Texture.HEIGHTMAP_NUM)
updateUniversalUniform('worldSize', planetSize)

# Construct patches
logging.info("Constructing geometry")
def getPatchData():
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
  return patchData

patchData = assets.getAsset('terrain_patch_data', getPatchData, (), args.args.remake_terrain)
patchIndices = np.array([],dtype=np.int32)

# Set up renderer
shader = getShader('terrain',tess=True,geom=False)
shader['colormap'] = Texture.COLORMAP_NUM
shader['normalmap'] = Texture.NORMALMAP_NUM
shader['noisemap'] = Texture.NOISE_NUM
renderID = shader.setData(patchData, patchIndices)

# Texture sizes
heightmap = Texture.Texture(Texture.HEIGHTMAP)
textWidth = 800
textRes = float(planetSize) / textWidth
logging.info(" + Heightmap texture size {:d}x{:d} for a resolution of {:.1f}m per pixel".format(textWidth,textWidth,textRes))
textHeight = textWidth
sign = lambda x: 1 if x>0 else -1
def generateHeightmap():
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
  del im
  return d

d = assets.getAsset('heightmap', generateHeightmap, (), args.args.remake_terrain)
heightmap.loadData(d, keep_copy=True)

logging.info("Loading textures")

texture = Texture.Texture(Texture.COLORMAP)
normalTexture = Texture.Texture(Texture.NORMALMAP)

def getTexData():
  colorMapSize = 1000
  texData = np.zeros((colorMapSize,colorMapSize,4),dtype=np.float32)

  a = Image.open('textures/grass.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  forest = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((forest.shape[0],1),dtype=np.float32)
  forest = np.append(forest,add,axis=1)
  forest = np.array([forest[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

  a = Image.open('textures/clay.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  clay = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((clay.shape[0],1),dtype=np.float32)
  clay = np.append(clay,add,axis=1)
  clay = np.array([clay[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

  a = Image.open('textures/stone.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  stone = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((stone.shape[0],1),dtype=np.float32)
  stone = np.append(stone,add,axis=1)
  stone = np.array([stone[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

  a = Image.open('textures/cobblestones.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  cobblestone = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((cobblestone.shape[0],1),dtype=np.float32)
  cobblestone = np.append(cobblestone,add,axis=1)
  cobblestone = np.array([cobblestone[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

  texData[0:colorMapSize/2,0:colorMapSize/2] = forest
  texData[0:colorMapSize/2,colorMapSize/2:] = stone
  texData[colorMapSize/2:,0:colorMapSize/2] = clay
  texData[colorMapSize/2:,colorMapSize/2:] = cobblestone

  return texData

def getTexNormData():
  colorMapSize = 1000
  texNormData = np.zeros((colorMapSize,colorMapSize,4),dtype=np.float32) +0.5
  texNormData[:,:,2:] = 1

  a = Image.open('textures/forest-normal.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  forest_normal = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((forest_normal.shape[0],1),dtype=np.float32)
  forest_normal = np.append(forest_normal,add,axis=1)
  forest_normal = np.array([forest_normal[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

  a = Image.open('textures/clay-normal.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  clay_normal = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((clay_normal.shape[0],1),dtype=np.float32)
  clay_normal = np.append(clay_normal,add,axis=1)
  clay_normal = np.array([clay_normal[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

  a = Image.open('textures/cobblestones-normal.jpg')
  a.thumbnail((colorMapSize/2,colorMapSize/2),Image.ANTIALIAS)
  cobblestone_normal = np.array(a.getdata()).astype(np.float32)
  add = np.zeros((cobblestone_normal.shape[0],1),dtype=np.float32)
  cobblestone_normal = np.append(cobblestone_normal,add,axis=1)
  cobblestone_normal = np.array([cobblestone_normal[i*a.size[0]:(i+1)*a.size[0]] for i in xrange(a.size[1])])/256

#  texNormData[0:colorMapSize/2,0:colorMapSize/2] = forest_normal
  texNormData[colorMapSize/2:,:colorMapSize/2] = clay_normal
  texNormData[colorMapSize/2:,colorMapSize/2:] = cobblestone_normal

  return texNormData

texData = assets.getAsset('terrain_diffuse', getTexData)
texNormData = assets.getAsset('terrain_normal', getTexNormData)

texture.loadData(texData)
normalTexture.loadData(texNormData)
del texData

def display(camera):
  if np.sum(camera.position*camera.position) > 6e6**2:
    return
  shader.load()
  texture.load()
  normalTexture.load()
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
      return 20
  return 20 + (theta - 0.4)*100 + 10*(theta-0.4)*getCurvature(x,y);

def getAt(x,y):
  x += planetSize / 2
  y += planetSize / 2
  s = heightmap.read(float(x)/planetSize, float(y)/planetSize)[3] + 1000

  offset = noiseG.noiseTexture.read(x/6000., y/6000.)[3] * getFineAmount(x, y)

  return s + offset

def getGradAt(x,y):
  dx = (getAt(x+0.1,y)-getAt(x,y))/0.1
  dy = (getAt(x,y+0.1)-getAt(x,y))/0.1
  return [dx,dy]

