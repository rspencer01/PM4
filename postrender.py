import numpy as np
import Texture
from Shaders import *
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
  
shader = getShader('postrender')
renderID = shader.setData(data,indices)
lightingShader = getShader('lighting')
lightingRenderID = shader.setData(data,indices)

def display(colorTexture,depthTexture):
  depthTexture.load()
  colorTexture.load()
  colorTexture.makeMipmap()
  shader.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['colormap'] = Texture.COLORMAP_NUM
  shader['depthmap'] = Texture.DEPTHMAP_NUM
  shader.draw(gl.GL_TRIANGLES,renderID,1)

def lighting(colorTexture,normTexture,posTexture,depthTexture):
  depthTexture.load()
  colorTexture.load()
  normTexture.load()
  posTexture.load()
  lightingShader.load()
  lightingShader['model'] = np.eye(4,dtype=np.float32)
  lightingShader['colormap'] = Texture.COLORMAP_NUM
  lightingShader['normmap'] = Texture.COLORMAP2_NUM
  lightingShader['posmap'] = Texture.COLORMAP3_NUM
  lightingShader['depthmap'] = Texture.DEPTHMAP_NUM
  lightingShader['ambientLight'] = 0.3
  lightingShader['sunLight'] = 0.7
  shader.draw(gl.GL_TRIANGLES,lightingRenderID,1)
