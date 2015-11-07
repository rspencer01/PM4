import numpy as np
import Image
from Shaders import *
import OpenGL.GL as gl
import Texture
import noise

RELOAD = False
print "Constructing Terrain"
#if (gl.glGetIntegerv(gl.GL_MAX_PATCH_VERTICES) < 4):
#  raise "Error.  Cannot make patches."

planetSize = 8000
size = 160
distance = planetSize/size
data = np.zeros((size-1)**2*6,dtype=[("position" , np.float32,3)])
                         #("normal"  , np.float32,ss3),
                         #("color"    , np.float32,4)])
I = []
for i in range(size-1):
  for j in range(size-1):
    data['position'][(i*(size-1)+j)*6] = (i,0,j)
    data['position'][(i*(size-1)+j)*6+1] = (i,0,j+1)
    data['position'][(i*(size-1)+j)*6+2] = (i+1,0,j)
    data['position'][(i*(size-1)+j)*6+3] = (i+1,0,j)
    data['position'][(i*(size-1)+j)*6+4] = (i,0,j+1)
    data['position'][(i*(size-1)+j)*6+5] = (i+1,0,j+1)    
    #data['normal'][i*size+j] = (0,1,0)

data['position']=(data['position']-np.array([size/2,0,size/2]))*distance
#data['color'][:]    = [(0,1,1,1)]
indices = np.array(I,dtype=np.int32)

shader = getShader('terrain',tess=True,geom=False)
renderID = shader.setData(data,indices)

heightmap = Texture.Texture(Texture.HEIGHTMAP)
textWidth = 1000
textHeight = textWidth
sign = lambda x: 1 if x>0 else -1
if RELOAD:
  d = np.zeros((textWidth,textHeight,4),dtype=np.float32)
  for i in range(textWidth):
    if (100*i/textWidth-1)%5==0:
      print str(50*i/(textWidth-1))+'%'  
    for j in range(textHeight):
      t = noise.pnoise2(float(i)/textWidth*5,float(j)/textWidth*5,octaves=4)**2
      s = (noise.pnoise2(float(i)/textWidth*60,float(j)/textWidth*60,octaves=5,persistence=0.35))*1.5
      s = (0.3*s+1)* t
      d[i,j] = (s,s,s,s)
  print np.max(d)

  d/=np.max(d)
  d = np.sin(d*3.1415/2)
  d*=320
  for i in range(textWidth-1):
    if (100*i/textWidth-1)%5==0:
      print str(50+50*i/(textWidth-1))+'%'
    for j in range(textHeight-1):
      v1= np.array([float(i)/textWidth*size*distance   , d[i,j][3]   , float(j)/textWidth*size*distance]) 
      v2= np.array([float(i+1)/textWidth*size*distance , d[i+1,j][3] , float(j)/textWidth*size*distance]) 
      v3= np.array([float(i)/textWidth*size*distance   , d[i,j+1][3] , float(j+1)/textWidth*size*distance]) 
      d[i,j][:3] = np.cross(v3-v1,v2-v1)
  np.save('terrain.npy',d)
else:
  d=np.load('terrain.npy')

#print d
heightmap.loadData(d.shape[0],d.shape[1],d)

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

def display():
  shader.load()
  texture.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['heightmap'] = Texture.HEIGHTMAP_NUM
  shader['colormap'] = Texture.COLORMAP_NUM
  heightmap.load()
  shader.draw((size-1)**2*6,renderID)
  
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
         (d[int(y),int(x+1)] * (1-f2) + d[int(y+1),int(x+1)] * f2) * f1

def getGradAt(x,y):
  dx = (getAt(x+0.1,y)-getAt(x,y))/0.1
  dy = (getAt(x,y+0.1)-getAt(x,y))/0.1
  return [dx[3],dy[3]]
