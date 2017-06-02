import numpy as np
import OpenGL.GL as gl
import Shaders
import Texture

data = np.zeros(4,dtype=[("position" ,np.float32, 3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

shader = Shaders.getShader('map')
renderID = shader.setData(data,indices) 

fullscreenAmount = 0.
targetFullScreenAmount = 0.

iconsTexture = Texture.Texture(Texture.COLORMAP)
iconsTexture.loadFromImage('assets/icons/village.png', daemon=False)

def update(ms):
  global fullscreenAmount
  f = 30*ms
  fullscreenAmount = fullscreenAmount * (1-f) + targetFullScreenAmount * f

def display():
  iconsTexture.load()
  shader['icons'] = Texture.COLORMAP_NUM
  shader['fullscreen'] = fullscreenAmount
  shader.draw(gl.GL_TRIANGLES, renderID, 1)
