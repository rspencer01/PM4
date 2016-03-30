import OpenGL.GL as gl
import numpy as np

HEIGHTMAP = gl.GL_TEXTURE0
HEIGHTMAP_NUM = 0
SHADOWS1 = gl.GL_TEXTURE1
SHADOWS1_NUM = 1
SHADOWS2 = gl.GL_TEXTURE2
SHADOWS2_NUM = 2
SHADOWS3 = gl.GL_TEXTURE3
SHADOWS3_NUM = 3
NOISE = gl.GL_TEXTURE4
NOISE_NUM = 4
BUMPMAP = gl.GL_TEXTURE5
BUMPMAP_NUM = 5
COLORMAP = gl.GL_TEXTURE6
COLORMAP_NUM = 6
DEPTHMAP = gl.GL_TEXTURE7
DEPTHMAP_NUM = 7
COLORMAP2 = gl.GL_TEXTURE8
COLORMAP2_NUM = 8
COLORMAP3 = gl.GL_TEXTURE9
COLORMAP3_NUM = 9


class Texture:
  def __init__(self,type):
    self.textureType =  type
    self.id = gl.glGenTextures(1)
    self.size = ()
    
    self.load()
    #gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)    
  def loadData(self,width,height,data):
    self.load()
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0 ,gl.GL_RGBA32F, width, height, 0, gl.GL_RGBA, gl.GL_FLOAT, data)
    self.size = (width,height)
    self.makeMipmap()
  def makeMipmap(self):
    self.load()
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
  def load(self):
    gl.glActiveTexture(self.textureType)
    gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
  def getData(self):
    self.load()
    return gl.glGetTexImage(gl.GL_TEXTURE_2D,0,gl.GL_RGBA,gl.GL_FLOAT)
  def saveToFile(self,fileName):
    np.save(fileName,self.getData())
  def loadFromFile(self,fileName):
    data = np.load(fileName)
    self.loadData(data.shape[0],data.shape[1],data)
  def __del__(self):
    print "Freeing texture",self.id
    gl.glDeleteTextures(self.id)
