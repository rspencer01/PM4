import numpy as np
import OpenGL.GL as gl
import Texture
import Shaders
import random
import noise
from transforms import *

RELOAD = 1
size = 1600
numSwatches = 15

numBlades = 140
vertexData = np.zeros(11*numBlades,dtype=[("position" , np.float32,3),("normal" , np.float32,3),("color" , np.float32,4)])

I = []
for i in xrange(numBlades):
  vertexData['position'][i*11] = (0,0,0.015)
  vertexData['position'][i*11+1] = (0,0,-0.015)
  vertexData['position'][i*11+2] = (0.02,0.1,0.013)
  vertexData['position'][i*11+3] = (0.02,0.1,-0.013)
  vertexData['position'][i*11+4] = (0.02,0.1,0.013)
  vertexData['position'][i*11+5] = (0.02,0.1,-0.013)
  vertexData['position'][i*11+6] = (0.05,0.18,0.009)
  vertexData['position'][i*11+7] = (0.05,0.18,-0.009)
  vertexData['position'][i*11+8] = (0.05,0.18,-0.009)
  vertexData['position'][i*11+9] = (0.05,0.18,0.009)
  vertexData['position'][i*11+10] = (0.09,0.25,0)
  ps = np.array([random.random()-0.5,0,random.random()-0.5])
  height = random.random() * 0.5 + 0.5
  theta = random.random()*3.14159*2
  mat = np.array(((np.cos(theta),0,np.sin(theta)),(0,1,0),(-np.sin(theta),0,np.cos(theta))))
  for j in xrange(11):
    vertexData['color'][i*11+j] = np.array([0.4,0.9,0.6,1])*(0.7+0.3*vertexData['position'][i*11+j][1]/0.25)
    vertexData['color'][i*11+j][3] = 1

    vertexData['position'][i*11+j] = mat.dot(vertexData['position'][i*11+j])
    vertexData['position'][i*11+j][1] *= height



  vertexData['position'][i*11:i*11+11] += ps 
  I += range(i*11,i*11+3)
  I += range(i*11+1,i*11+4)[::-1]
  I += range(i*11+4,i*11+7)
  I += range(i*11+5,i*11+8)[::-1]
  I += range(i*11+8,i*11+11)[::-1]

for i in xrange(len(I)/3):
  norm = np.cross(vertexData['position'][I[3*i]] - vertexData['position'][I[3*i+1]],
                  vertexData['position'][I[3*i+2]] - vertexData['position'][I[3*i+1]])
  norm = norm/(norm.dot(norm))**0.5
  vertexData['normal'][I[3*i]] = norm
  vertexData['normal'][I[3*i+1]] = norm
  vertexData['normal'][I[3*i+2]] = norm

swatches = np.zeros((numSwatches**2),dtype=[('model',np.float32,(4,4))])
for i in range(numSwatches):
  for j in range(numSwatches):
    swatches[i*numSwatches+j] = np.eye(4,dtype=np.float32)
    translate(swatches[i*numSwatches+j]['model'],i-numSwatches/2.0,0,j-numSwatches/2.0)
indices = np.array(I,dtype=np.int32)

shader = Shaders.getShader('grass',instance=True, geom=True)
renderID = shader.setData(vertexData,indices,swatches)

if RELOAD:
  data = np.zeros((size,size,4),dtype=np.float32)
  for i in xrange(size):
    for j in xrange(size):
      data[i][j][3] = noise.pnoise2(float(i)/size*50,float(j)/size*50,octaves=4)*20
  data = np.around(data)
  data = np.clip(data,0,1)


  np.save('foliage.npy',data)
else:
  data=np.load('foliage.npy')
# Warning.  Must redo this Overdone in Forest
foliageMap = Texture.Texture(Texture.FOLIAGEMAP)

foliageMap.loadData(size,size,data)

def display(cameraPos):
  foliageMap.load()
  for i in range(numSwatches):
    for j in range(numSwatches):
      swatches[i*numSwatches+j] = np.eye(4,dtype=np.float32)
      yrotate(swatches[i*numSwatches+j]['model'], (13*(i- int(cameraPos[0]))+11*(j- int(cameraPos[2]))**2)*90.0)
      translate(swatches[i*numSwatches+j]['model'],i-numSwatches/2.0 - int(cameraPos[0]),0,j-numSwatches/2.0 + int(cameraPos[2]))
  shader.setInstances(swatches,renderID)
  Shaders.setUniform('foliageMap',Texture.FOLIAGEMAP_NUM)
  shader.draw(gl.GL_TRIANGLES,renderID,len(swatches))
