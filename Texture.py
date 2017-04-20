import OpenGL.GL as gl
import numpy as np
import Image
import logging
import sys

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
FOLIAGEMAP = gl.GL_TEXTURE10
FOLIAGEMAP_NUM = 10
EARTHMAP = gl.GL_TEXTURE11
EARTHMAP_NUM = 11

textureUnits = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_IMAGE_UNITS)
logging.info("Found {} texture units".format(textureUnits))
if textureUnits < 32:
  logging.fatal("Insufficient texture units.  Require 32, have {}".format(textureUnits))
  sys.exit(1)

class Texture:
  def __init__(self,type):
    self.textureType =  type
    self.id = gl.glGenTextures(1)
    self.size = ()

    self.load()

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)


  def loadData(
      self,
      width,
      height,
      data,
      internal_format=gl.GL_RGBA32F,
      type=gl.GL_FLOAT):
    self.load()
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0 ,internal_format, width, height, 0, gl.GL_RGBA, type, data)
    self.size = (width,height)
    self.makeMipmap()


  def makeMipmap(self):
    self.load()
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)


  def load(self):
    self.loadAs(self.textureType)


  def loadAs(self, type):
    gl.glActiveTexture(type)
    gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)


  def getData(self):
    self.load()
    return gl.glGetTexImage(gl.GL_TEXTURE_2D,0,gl.GL_RGBA,gl.GL_FLOAT)


  def saveToFile(self,fileName):
    np.save(fileName,self.getData())


  def loadFromFile(self,fileName):
    data = np.load(fileName)
    self.loadData(data.shape[0],data.shape[1],data)
    del data


  def loadFromImage(self, filename):
    teximag = Image.open(filename)
    texdata = np.array(teximag.getdata()).astype(np.float32)
    # Make this a 4 color file
    if (texdata.shape[1]!=4):
      add = np.zeros((texdata.shape[0],1),dtype=np.float32)+256
      texdata = np.append(texdata,add,axis=1)

    texdata = texdata.reshape(teximag.size[0], teximag.size[1], 4)
    self.loadData(texdata.shape[0],texdata.shape[1],texdata/256)


  def __del__(self):
    print "Freeing texture",self.id
    gl.glDeleteTextures(self.id)
