import numpy as np
import args
import Image
import logging
from Shaders import *
import OpenGL.GL as gl
import Texture
import RenderStage
import noise
import os
import sys
import Pager

logging.info("Constructing Terrain")

planetSize = 60000
patches = 200
patchSize = planetSize/patches
pageSize = 1000
pagesAcross = planetSize / pageSize
pageResoultion = 256
numPages = 5
pageMapping = Pager.Pager(numPages**2)
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
shader['model'] = np.eye(4,dtype=np.float32)
shader['heightmap'] = Texture.HEIGHTMAP_NUM
shader['colormap'] = Texture.COLORMAP_NUM
shader['worldSize'] = planetSize
shader['numPages'] = numPages
shader['pageSize'] = pageSize
renderID = shader.setData(data,indices)

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

  # Boundary conditions
  for i in xrange(textWidth):
    d[i,0] = -1000
    d[i,-1] = -1000
  for i in xrange(textHeight):
    d[0,i] = -1000
    d[-1,i] = -1000

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
setUniform('heightmap',Texture.HEIGHTMAP_NUM)

pageTableTexture = Texture.Texture(Texture.COLORMAP2)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST_MIPMAP_NEAREST)
pageRenderStage = RenderStage.RenderStage()
pageRenderStage.reshape(pageResoultion*numPages,pageResoultion*numPages)
pageTexture = pageRenderStage.displayAuxColorTexture

setUniform('pageTable',Texture.COLORMAP2_NUM)
setUniform('pageTexture',Texture.COLORMAP3_NUM)

pagingShader = getShader('pagingShader', forceReload=True)
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
pagingRenderID = pagingShader.setData(data,indices)

def getCoordinate(id):
  return id % numPages, id / numPages

def generatePage(page):
  assert page in pageMapping
  c = getCoordinate(pageMapping[page])
  pageRenderStage.load(pageResoultion,pageResoultion, pageResoultion*c[0],pageResoultion*(numPages-c[1]-1),False)
  pagingShader.load()
  pagingShader['pagePosition'] = np.array([page[0],0.,page[1]],dtype=np.float32)
  pagingShader['id'] = pageMapping[page]
  pagingShader['pageSize'] = pageSize
  pagingShader['numPages'] = numPages
  pagingShader['pagesAcross'] = pagesAcross
  pagingShader['worldSize'] = planetSize
  pagingShader.draw(gl.GL_TRIANGLES, pagingRenderID)
  pageTexture.makeMipmap()

def updatePageTable(camera):
  currentPage = (pagesAcross - int(camera.pos[2] / (pageSize) + pagesAcross/2) , int(camera.pos[0] / (pageSize) + pagesAcross/2))
  data = np.zeros((pagesAcross, pagesAcross, 4),dtype=np.float32) - 1
  toredo = False
  for i in xrange(max(0,currentPage[0]-numPages/2),min(pagesAcross,currentPage[0]+numPages/2+1)):
    for j in xrange(max(0,currentPage[1]-numPages/2),min(pagesAcross,currentPage[1]+numPages/2+1)):
      page = (i,j)
      if page not in pageMapping:
        toredo = True
  if not toredo: return

  #pageMapping.clear()

  for i in xrange(max(0,currentPage[0]-numPages/2),min(pagesAcross,currentPage[0]+numPages/2+1)):
    for j in xrange(max(0,currentPage[1]-numPages/2),min(pagesAcross,currentPage[1]+numPages/2+1)):
      page = (i,j)
      if page not in pageMapping:
        pageMapping.add(page)
        generatePage(page)
      index = pageMapping[page]
      data[i][j][0] = index / float(numPages**2)
  pageTableTexture.loadData(data.shape[0], data.shape[1], data[::-1,:])

def display(camera):
  if np.sum(camera.pos*camera.pos) > 6e6**2:
    return
  shader.load()
  texture.load()
  heightmap.load()
  pageTableTexture.load()
  pageTexture.load()
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
