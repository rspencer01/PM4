import numpy as np
import Image
import logging
from Shaders import *
import OpenGL.GL as gl
import Texture
import noise
import os
import sys

logging.info("Constructing Terrain")

planetSize = 60000
resolution = 160
patches = 200
patchSize = planetSize/patches
logging.info(" + {:d} (={:d}x{:d}) patches at {:d}m on a side".format((patches-1)**2,patches-1,patches-1,patchSize))

# Construct patches
logging.info(" + Constructing geometry")
data = np.zeros((patches-1)**2*6,dtype=[("position" , np.float32,3)])
for i in range(patches-1):
  for j in range(patches-1):
    data['position'][(i*(patches-1)+j)*6] = (i,0,j)
    data['position'][(i*(patches-1)+j)*6+1] = (i,0,j+1)
    data['position'][(i*(patches-1)+j)*6+2] = (i+1,0,j)
    data['position'][(i*(patches-1)+j)*6+3] = (i+1,0,j)
    data['position'][(i*(patches-1)+j)*6+4] = (i,0,j+1)
    data['position'][(i*(patches-1)+j)*6+5] = (i+1,0,j+1)
data['position']=(data['position']-np.array([patches/2,0,patches/2]))*patchSize
indices = np.array([],dtype=np.int32)

# Set up renderer
shader = getShader('terrain',tess=True,geom=False,forceReload=True)
renderID = shader.setData(data,indices)

# Texture sizes
heightmap = Texture.Texture(Texture.HEIGHTMAP)
textWidth = 800
textRes = float(planetSize) / textWidth
logging.info(" + Heightmap texture size {:d}x{:d} for a resolution of {:.1f}m per pixel".format(textWidth,textWidth,textRes))
textHeight = textWidth
sign = lambda x: 1 if x>0 else -1
if not os.path.exists('terrain.npy'):
  d = np.zeros((textWidth,textHeight,4),dtype=np.float32)
  logging.info(" + Calculating heightmap")
  im = Image.open("assets/Cederberg Mountains Height Map (Merged).png")
  im.thumbnail((textHeight,textWidth),Image.ANTIALIAS)
  pix = im.load()
  for i in range(textWidth):
    for j in range(textHeight):
      t = pix[i,j]
      d[textWidth-1-i,j] = (t,t,t,t)
  """
  for i in range(textWidth):
    sys.stdout.write(str(i)+" / "+str(textWidth))
    sys.stdout.write('\r')
    sys.stdout.flush()
    for j in range(textHeight):
      # Larger, general shape
      t = 17*noise.pnoise2(float(i)/textWidth*3.5,float(j)/textWidth*3.5+0.34,octaves=5)**2
      t += 5*noise.pnoise2(float(i)/textWidth*7.5,float(j)/textWidth*7.5,octaves=4)**2
      r = textWidth*(0.4 + 0.0*
              (
                np.cos(float(3.1415*i*1.3)/textWidth)+
                np.cos(float(3.1415*j*1.5)/textWidth)+
                np.sin(float(3.1415*j*8.5)/textWidth+2) * 0.2+
                np.sin(float(3.1415*i*7.5)/textWidth+4) * 0.2+
                np.sin(float(3.1415*(i+3*j)*3.5)/textWidth+4) * 0.1
              )
          )
      t += 1.5*np.exp( -0.00008**2*abs((i-textWidth/2)**2+(j-textWidth/2)**2 - (r)**2)**2)
      t = np.sin(t/4.5 * 3.1415/2)
      d[i,j] = (t,t,t,t)

  print np.max(d),np.min(d)
  """
  d -= np.min(d)
  d /= np.max(d)
  d = np.sin(d*3.1415/2)
  d *= 1920
  #d *= 1620
  for i in xrange(textWidth):
    d[i,0] = -1000
    d[i,-1] = -1000
  for i in xrange(textHeight):
    d[0,i] = -1000
    d[-1,i] = -1000

  d[textWidth/2-1,textHeight/2-1] = 3000
  d[textWidth/2-1,textHeight/2] = 3000
  d[textWidth/2,textHeight/2] = 3000
  logging.info(" + Calculating normalmap")
  for i in range(textWidth-1):
    sys.stdout.write(' | '+str(i)+" / "+str(textWidth))
    sys.stdout.write('\r')
    sys.stdout.flush()
    for j in range(textHeight-1):
      v1= np.array([float(i  )/textWidth*planetSize  , d[i,j][3]   , float(j  )/textWidth*planetSize])
      v2= np.array([float(i+1)/textWidth*planetSize  , d[i+1,j][3] , float(j  )/textWidth*planetSize])
      v3= np.array([float(i  )/textWidth*planetSize  , d[i,j+1][3] , float(j+1)/textWidth*planetSize])
      d[i,j][:3] = np.cross(v3-v1,v2-v1)
  np.save('terrain.npy',d)
  del im
else:
  d=np.load('terrain.npy')

#print d
heightmap.loadData(d.shape[0],d.shape[1],d)

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
texture.loadData(texData.shape[0],texData.shape[1],texData)
del texData

def display():
  setUniform('heightmap',Texture.HEIGHTMAP_NUM)
  shader.load()
  texture.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['heightmap'] = Texture.HEIGHTMAP_NUM
  shader['colormap'] = Texture.COLORMAP_NUM
  heightmap.load()
  shader.draw((patches-1)**2*6,renderID)
  
def getAt(x,y):
  x,y = x,y
  x+=planetSize/2
  y+=planetSize/2
  y = float(y) / planetSize*textWidth
  x = float(x) / planetSize*textWidth
  x = min(textWidth-2,x)
  y = min(textWidth-2,y)
  f1 = (x-int(x))
  f2 = (y-int(y))
  return (d[int(y),int(x)] * (1-f2) + d[int(y+1),int(x)] * f2) * (1-f1)+\
         (d[int(y),int(x+1)] * (1-f2) + d[int(y+1),int(x+1)] * f2) * f1+\
         1000

def getGradAt(x,y):
  dx = (getAt(x+0.1,y)-getAt(x,y))/0.1
  dy = (getAt(x,y+0.1)-getAt(x,y))/0.1
  return [dx[3],dy[3]]
