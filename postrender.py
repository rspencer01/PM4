import numpy as np
import dent.Texture as Texture
from Shaders import *
from dent.configuration import config

Re = config.earth_radius
Ra = config.atmosphere_radius

data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

shader = getShader('postrender')
shader['colormap'] = Texture.COLORMAP_NUM
shader['depthmap'] = Texture.DEPTHMAP_NUM
renderID = shader.setData(data,indices)

lightingShader = getShader('lighting')
lightingShader['colormap'] = Texture.COLORMAP_NUM
lightingShader['normmap'] = Texture.COLORMAP2_NUM
lightingShader['posmap'] = Texture.COLORMAP3_NUM
lightingShader['depthmap'] = Texture.DEPTHMAP_NUM
lightingShader['opticaldepthmap'] = Texture.OPTICAL_DEPTHMAP_NUM
lightingShader['Re'] = Re
lightingShader['Ra'] = Ra
lightingRenderID = lightingShader.setData(data,indices)

exposure = 1.0

highColTexture = Texture.Texture(Texture.COLORMAP2)
blurredHighColTexture = Texture.Texture(Texture.COLORMAP2)

showNormals = 0

def display(previousStage,windowWidth,windowHeight):
  previousStage.displayDepthTexture.load()
  previousStage.displayColorTexture.load()
  previousStage.displayColorTexture.makeMipmap()
  shader.draw(gl.GL_TRIANGLES,renderID,1)

def lighting(previousStage):
  previousStage.displayDepthTexture.load()
  previousStage.displayColorTexture.load()
  previousStage.displaySecondaryColorTexture.load()
  previousStage.displayAuxColorTexture.load()
  setUniform('ambientLight',0.1)
  lightingShader.load()
  lightingShader['ambientLight'] = 0.1;
  lightingShader['options'] = showNormals
  lightingShader.draw(gl.GL_TRIANGLES,lightingRenderID,1)
