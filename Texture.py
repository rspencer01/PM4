import OpenGL.GL as gl
import numpy as np
import Image
import logging
import sys
import threading
import taskQueue
from math import fmod

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
OPTICAL_DEPTHMAP = gl.GL_TEXTURE12
OPTICAL_DEPTHMAP_NUM = 12
NIGHTSKY = gl.GL_TEXTURE13
NIGHTSKY_NUM = 13
NORMALMAP = gl.GL_TEXTURE14
NORMALMAP_NUM = 14

textureUnits = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_IMAGE_UNITS)
logging.info("Found {} texture units".format(textureUnits))
if textureUnits < 32:
  logging.fatal("Insufficient texture units.  Require 32, have {}".format(textureUnits))
  sys.exit(1)

class Texture:
  def __init__(self, type, nonblocking=False):
    """Creates a new texture of the given type.  If nonblocking is specified
    true, the creation of the texture handle will be added to the GPU queue.  If
    this is done, all texture loads _must_ occur after the handle has been
    acquired."""
    self.textureType =  type
    self.id = None
    self._data = None

    if nonblocking:
      taskQueue.addToMainThreadQueue(self.initialise)
    else:
      self.initialise()


  def initialise(self):
    self.id = gl.glGenTextures(1)
    self.load()

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)

    logging.info("New texture {}".format(self.id))


  def loadData(
      self,
      data,
      width=None,
      height=None,
      internal_format=gl.GL_RGBA32F,
      type=gl.GL_FLOAT,
      keep_copy=False,
      make_mipmap=True):
    """Loads data to the GPU.  Parameter `data` may either be a numpy array of
    shape `(width,height,4)` or `None` (in which case `width` and `height` must
    be specified)."""
    if width == None:
      width = data.shape[0]
    if height == None:
      height = data.shape[1]
    self.load()
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0 ,internal_format, width, height, 0, gl.GL_RGBA, type, data)
    if keep_copy:
      self._data = data.copy()
    if make_mipmap:
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
    self.loadData(data)
    del data


  def loadFromImage(self, filename, daemon=True):
    def preloadFile():
      logging.info("Preloading {} into texture {}".format(filename, self.id))

      teximag = Image.open(filename)
      data = np.array(teximag.getdata()).astype(np.float32)

      ## Make this a 4 color file
      if (data.shape[1] != 4):
        add = np.zeros((data.shape[0],1),dtype=np.float32)+256
        data = np.append(data, add, axis=1)

      data = data.reshape(teximag.size[0], teximag.size[1], 4)

      def uploadToGPU(data):
        logging.info("Uploading texture {}".format(self.id))
        self.loadData(data/256)

      # We have now loaded the image data.  We need to upload it to the GPU.
      # Either we do this on the main thread, or if we are not using a daemon
      # style, we are the main thread and we must do it now.
      if daemon:
        taskQueue.addToMainThreadQueue(uploadToGPU, (data,))
      else:
        uploadToGPU(data)

    # If we are doing this daemon style, we start a new thread.
    if daemon:
      thread = threading.Thread(target=preloadFile)
      thread.setDaemon(True)
      thread.start()
    else:
      preloadFile()


  def read(self, x, y, interpolate=True):
    assert self._data is not None

    x = fmod(x, 1)
    if x < 0: x += 1
    y = fmod(y, 1)
    if y < 0: y += 1

    y = float(y) * self._data.shape[0] - 0.5
    x = float(x) * self._data.shape[1] - 0.5

    f1 = (x-int(x))
    f2 = (y-int(y))

    if not interpolate:
      f1 = 1 if f1 > 0.5 else 0
      f2 = 1 if f2 > 0.5 else 0

    r = (self._data[int(y),int(x)] * (1-f2) + self._data[int(y+1),int(x)] * f2) * (1-f1)+\
        (self._data[int(y),int(x+1)] * (1-f2) + self._data[int(y+1),int(x+1)] * f2) * f1
    return r


  def __del__(self):
    logging.info("Freeing texture {}".format(self.id))
    gl.glDeleteTextures(self.id)
