import numpy as np
import OpenGL.GL as gl
from dent.Shaders import *
import dent.Texture as Texture
from dent.transforms import *
import Terrain

data = np.zeros(24,dtype=[("position" , np.float32,3),
                         ("normal"  , np.float32,3)])
I = []
for i in range(8):
  I += [i*3,i*3+1,i*3+2]
h =  2 ** 0.5
data['position'] = [(-1,0,-1),(0,h,0),(-1,0,1),
                    (-1,0,1),(0,h,0),(1,0,1),
                    (1,0,1),(0,h,0),(1,0,-1),
                    (1,0,-1),(0,h,0),(-1,0,-1),
                    (-1,0,-1),(0,-h,0),(-1,0,1),
                    (-1,0,1),(0,-h,0),(1,0,1),
                    (1,0,1),(0,-h,0),(1,0,-1),
                    (1,0,-1),(0,-h,0),(-1,0,-1)]
data['normal']   = [(-1,1,0)] * 3 +\
                   [(0,1,1)] * 3 + \
                   [(1,1,0)] * 3 + \
                   [(0,1,-1)] * 3 + \
                   [(-1,-1,0)] * 3 + \
                   [(0,-1,1)] * 3 + \
                   [(1,-1,0)] * 3 + \
                   [(0,-1,-1)] * 3 
indices = np.array(I,dtype=np.int32)

shader = getShader('general',instance=True)
time = 0
markers = np.zeros(0,dtype=[('model',np.float32,(4,4))])

def addMarker(pos):
  markers.resize(len(markers)+1)
  b = np.eye(4,dtype=np.float32)
  translate(b,pos[0],Terrain.getAt(pos[0],pos[2])+3,pos[2])
  markers['model'][-1] = b

def freeze():
  global renderID
  renderID = shader.setData(data,indices,markers)

def display():
  Texture.getWhiteTexture().load()
  shader.draw(gl.GL_TRIANGLES, renderID, len(markers))
