import numpy as np
import Texture
import graphicsOps
from Shaders import *
import Map

data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

shader = getShader('postrender',forceReload=True)
shader['model'] = np.eye(4,dtype=np.float32)
shader['colormap'] = Texture.COLORMAP_NUM
shader['blurredColorMap'] = Texture.COLORMAP3_NUM
shader['depthmap'] = Texture.DEPTHMAP_NUM
shader['highCol'] = Texture.COLORMAP2_NUM
renderID = shader.setData(data,indices)

lightingShader = getShader('lighting',forceReload=True)
lightingShader['model'] = np.eye(4,dtype=np.float32)
lightingShader['colormap'] = Texture.COLORMAP_NUM
lightingShader['normmap'] = Texture.COLORMAP2_NUM
lightingShader['posmap'] = Texture.COLORMAP3_NUM
lightingShader['depthmap'] = Texture.DEPTHMAP_NUM
lightingRenderID = lightingShader.setData(data,indices)

setUniform('ambientLight',0.1)
setUniform('sunLight',1.0)

exposure = 1.0

highColTexture = Texture.Texture(Texture.COLORMAP2)
blurredHighColTexture = Texture.Texture(Texture.COLORMAP2)

showNormals = 0

def display(previousStage,windowWidth,windowHeight):
  previousStage.displayDepthTexture.load()
  previousStage.displayColorTexture.load()
  previousStage.displayColorTexture.makeMipmap()

  data = gl.glGetTexImage(gl.GL_TEXTURE_2D,3,gl.GL_RGBA,gl.GL_FLOAT)
  s = data.sum(axis=0).sum(axis=0)/(data.shape[0]*data.shape[1])
  s = s[:3].dot(s[:3])**0.5
  data = data.max(axis=0).max(axis=0)
  b = data[:3].dot(data[:3])**0.5
  b = b*0.8+0.2*s
  global exposure
  if b==b:
    if b!=0:
      exposure = (1/b + 0.3)* 0.1 + exposure * 0.9
  exposure = min(10.0,max(0.001,exposure))

  shader.load()
  shader['brightness'] = exposure
  shader.draw(gl.GL_TRIANGLES,renderID,1)

def lighting(colorTexture,normTexture,posTexture,depthTexture):
  depthTexture.load()
  colorTexture.load()
  normTexture.load()
  posTexture.load()
  setUniform('ambientLight',0.1)
  setUniform('sunLight',1.0)
  lightingShader.load()
  lightingShader['ambientLight'] = 0.1;
  lightingShader['sunLight'] = 0.9
  lightingShader['options'] = showNormals
  lightingShader.draw(gl.GL_TRIANGLES,lightingRenderID,1)
