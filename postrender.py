import numpy as np
import Texture
from Shaders import *
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
  
shader = getShader('postrender',forceReload=True)
renderID = shader.setData(data,indices)
lightingShader = getShader('lighting',forceReload=True)
lightingRenderID = lightingShader.setData(data,indices)
mapShader = getShader('map',forceReload=True)
mapRenderID = mapShader.setData(data,indices) 

exposure = 1.0

def display(colorTexture,depthTexture):
  depthTexture.load()
  colorTexture.load()
  colorTexture.makeMipmap()
  data = gl.glGetTexImage(gl.GL_TEXTURE_2D,3,gl.GL_RGBA,gl.GL_FLOAT)
  s = data.sum(axis=0).sum(axis=0)/(data.shape[0]*data.shape[1])
  s = s[:3].dot(s[:3])**0.5
  data = data.max(axis=0).max(axis=0)
  b = data[:3].dot(data[:3])**0.5
  b = b*0.8+0.2*s
  global exposure
  if b==b:
    if 1/b + 0.1 < exposure:
      exposure = (1/b + 0.3)* 0.09 + exposure * 0.91
    else:
      exposure = (1/b + 0.3)* 0.005 + exposure * 0.995
  shader.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['colormap'] = Texture.COLORMAP_NUM
  shader['depthmap'] = Texture.DEPTHMAP_NUM
  shader['brightness'] = min(5.0,max(0.1,exposure))
  shader.draw(gl.GL_TRIANGLES,renderID,1)
  mapShader.load()
  mapShader['heightmap'] = Texture.HEIGHTMAP_NUM
  mapShader.draw(gl.GL_TRIANGLES,mapRenderID,1)

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
  lightingShader['ambientLight'] = 0.1
  lightingShader['sunLight'] = 0.9
  shader.draw(gl.GL_TRIANGLES,lightingRenderID,1)
