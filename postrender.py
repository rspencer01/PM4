import numpy as np
import Texture
from Shaders import *
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
  
shader = getShader('postrender')
renderID = shader.setData(data,indices)
def display(colorTexture,depthTexture):
  colorTexture.makeMipmap()
  level = int(np.log(max(colorTexture.size))/np.log(2))
  data = gl.glGetTexImage(gl.GL_TEXTURE_2D,level,gl.GL_RGB,gl.GL_FLOAT)
  intensity = sum(data[0][0])/3
  exposure = intensity
  print exposure
  depthTexture.load()
  colorTexture.load()
  shader.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['colormap'] = Texture.COLORMAP_NUM
  shader['depthmap'] = Texture.DEPTHMAP_NUM
  shader['exposure'] = exposure
  shader.draw(gl.GL_TRIANGLES,renderID,1)
