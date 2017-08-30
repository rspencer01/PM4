import OpenGL.GL as gl
import dent.Texture as Texture
from dent.RectangleObjects import RectangleObject

obj = RectangleObject('map')
obj.shader['icons'] = Texture.COLORMAP_NUM

fullscreenAmount = 0.
targetFullScreenAmount = 0.

iconsTexture = Texture.Texture(Texture.COLORMAP)
iconsTexture.loadFromImage('assets/icons/village.png', daemon=False)

def update(ms):
  global fullscreenAmount
  f = 30 * ms
  fullscreenAmount = fullscreenAmount * (1-f) + targetFullScreenAmount * f

def display():
  iconsTexture.load()
  obj.shader['fullscreen'] = fullscreenAmount
  obj.display()
