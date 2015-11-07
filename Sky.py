import numpy as np
from Shaders import *
data = np.zeros(8,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,1),(-1,1,1),(1,-1,1),(1,1,1),
                    (-1,-1,-1),(-1,1,-1),(1,-1,-1),(1,1,-1),
                   ]
data['position'] *= 4000
I = [0,1,2, 1,2,3, 4,5,6 ,5,6,7, 0,1,4, 1,4,5, 0,2,4, 2,4,6, 3,7,6, 3,6,2, 1,5,7, 1,7,3]
indices = np.array(I,dtype=np.int32)
  
shader = getShader('sky')
renderID = shader.setData(data,indices)
def display():
  shader.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader.draw(gl.GL_TRIANGLES,renderID,1)
