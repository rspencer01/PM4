import numpy as np
from Shaders import *
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
  
shader = getShader('sky')
renderID = shader.setData(data,indices)
def display():
  shader.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader.draw(gl.GL_TRIANGLES,renderID,1)
