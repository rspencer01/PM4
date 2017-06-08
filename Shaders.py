import ctypes
import logging
import numpy as np
import OpenGL.GL as gl
from ctypes import c_void_p, sizeof
import re
from collections import namedtuple

currentShader = None
universalUniforms = {}

objectInfo = namedtuple("ObjectInfo",
    ("numVertices",
      "numIndices",
      "vbo",
      "vertexArray",
      "ibo",
      "renderVerts",
      "instbo",
      "transformBufferObject"))

class ShaderCompileException(Exception):
  def __init__(self, args):
    message, source = args
    errp = re.compile(r"0\((.+?)\)(.*)")
    m = errp.match(message)
    if not m or not source:
      Exception.__init__(self, message)
      return
    line = int(m.groups()[0])
    ret = '\n\n'+message+'\n'
    sourceLines = source.split('\n')
    for i in xrange(max(0,line-4),min(len(sourceLines)-1,line+5)):
      ret += ('>>|' if i == line-1 else '  |') + sourceLines[i]+'\n'
    Exception.__init__(self, ret)

class Shader(object):
  def __init__(self, name):
    # Who are we
    self.name = name
    # What do we stand for?
    self.program = gl.glCreateProgram()
    self.programs = []
    # Where the uniform variables live
    self.locations = {}
    # The info for the objects of this shader
    self.objInfo = []
    # The errorful variables we have seen before
    self.warned = set()
    # Uniforms that are still to be set
    self.unsetUniforms = {}

  def addProgram(self, type, source):
    """Creates a shader, compiles the given shader source and attaches it
    to this program."""
    prog = gl.glCreateShader(type)
    gl.glShaderSource(prog, source)
    gl.glCompileShader(prog)
    # Find compile errors
    if gl.glGetShaderiv(prog, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
        raise ShaderCompileException((gl.glGetShaderInfoLog(prog), source))
    gl.glAttachShader(self.program, prog)

  def build(self):
    # Link!  Everything else is done in addProgram
    gl.glLinkProgram(self.program)
    if gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS) != gl.GL_TRUE:
      raise RuntimeError(gl.glGetProgramInfoLog(self.program))
    for prog in self.programs:
      gl.glDetachShader(self.program, prog)

  def load(self):
    # Check if we are loaded already.  If not do so.
    global currentShader
    if currentShader != self:
      gl.glUseProgram(self.program)
      currentShader = self

  def setData(self,data, indices=[], instanced=False):
    """Given vertex data and triangle indices, gives a unique identifier to be
    used when rendering this object."""
    vbo = gl.glGenBuffers(1)
    ibo = gl.glGenBuffers(1)
    vertexArray = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vertexArray)
    self.objInfo.append( objectInfo(len(data),
                                    len(indices),
                                    vbo,
                                    vertexArray,
                                    ibo,
                                    len(indices)*3,
                                    None, None
                                    ) )

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
    stride = data.strides[0]
    offsetc = 0
    for i in data.dtype.names:
      offset = ctypes.c_void_p(offsetc)
      loc = gl.glGetAttribLocation(self.program, i)
      if loc==-1:
        # Not in shader
        offsetc += data.dtype[i].itemsize
        continue
      gl.glEnableVertexAttribArray(loc)
      gl.glBindBuffer(gl.GL_ARRAY_BUFFER,vbo)
      gl.glVertexAttribPointer(loc, int(np.prod(data.dtype[i].shape)), gl.GL_FLOAT, False, stride, offset)
      gl.glVertexAttribDivisor(loc, 0)
      offsetc += data.dtype[i].itemsize

    if indices != []:
      gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
      gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STREAM_DRAW);

    return len(self.objInfo)-1

  def deleteData(self,dataId):
    obj = self.objInfo[dataId]
    gl.glDeleteBuffers([obj.vbo,obj.ibo])
    gl.glDeleteVertexArrays(obj.vertexArray)

  def __setitem__(self,i,v):
    """Sets the uniform lazily.  That is, we store the uniform CPU side, and 
    only blit it once we are about to render.  See `_setitem`."""
    self.unsetUniforms[i] = v

  def _setitem(self,i,v):
    """Sets the uniform in the shader.  Due to GPU overhead, this is not called 
    via the [] notation, but only when we render."""
    if i not in self.locations:
      self.locations[i] = gl.glGetUniformLocation(self.program, i)
    loc = self.locations[i]
    if loc==-1:
      if not i in self.warned:
        self.warned.add(i)
    elif type(v) == np.ndarray and v.shape == (4, 4):
      gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, v)
    elif type(v) == np.ndarray and len(v.shape)==2 and v.shape[1]==3:
      gl.glUniform3fv(loc, v.shape[0], v)
    elif type(v) == np.ndarray and len(v.shape)==2 and v.shape[1]==4:
      gl.glUniform4fv(loc, v.shape[0], v)
    elif type(v) in [float, np.float32, np.float64]:
      gl.glUniform1f(loc,v)
    elif type(v) in [np.ndarray] and v.shape==(3,):
      gl.glUniform3f(loc, v[0], v[1], v[2])
    elif type(v) in [int]:
      gl.glUniform1i(loc, v)

  def _setitems(self):
    """Blits all the lazyloaded uniforms to the GPU.    """
    for i,v in self.unsetUniforms.items():
      self._setitem(i,v)
    self.unsetUniforms = {}

  def draw(self,type,objectIndex,num=0):
    self.load()
    self._setitems()
    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glDrawElements(type,self.objInfo[objectIndex].numIndices,gl.GL_UNSIGNED_INT,None)

class GenericShader(Shader):
  def __init__(self, name, frag, vert, geom):
    super(GenericShader,self).__init__(name)
    self.addProgram(gl.GL_VERTEX_SHADER, vert)
    if geom:
      self.addProgram(gl.GL_GEOMETRY_SHADER, geom)
    self.addProgram(gl.GL_FRAGMENT_SHADER, frag)
    self.build()

class InstancedShader(GenericShader):
  def __init__(self,name,frag,vert,geom):
    super(InstancedShader,self).__init__(name,frag,vert,geom)
    self.instbo = None

  def setData(self,data,indices,instanced):
    renderId = super(InstancedShader,self).setData(data,indices)
    self.setInstances(instanced,renderId)
    return renderId

  def setInstances(self,instances,renderId):
    gl.glBindVertexArray(self.objInfo[renderId].vertexArray)
    self.instbo = gl.glGenBuffers(1)
    self.objInfo[renderId] = self.objInfo[renderId]._replace(instbo=self.instbo)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.instbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, instances.nbytes, instances, gl.GL_STREAM_DRAW)
    stride = instances.strides[0]
    offsetc = 0
    for i in instances.dtype.names:
      offset = ctypes.c_void_p(offsetc)
      loc = gl.glGetAttribLocation(self.program, i)
      if loc==-1:
        print "Error setting "+i+" in shader "+self.name
        continue
      gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.instbo)
      if instances.dtype[i].shape == (4, 4):
        for j in range(4):
          offset = ctypes.c_void_p(j*stride/4)
          gl.glEnableVertexAttribArray(loc+j)
          gl.glVertexAttribPointer(loc+j, 4, gl.GL_FLOAT, False, stride, offset)
          gl.glVertexAttribDivisor(loc+j, 1)
          offsetc += 4*2
      else:
        raise Exception("Type wrong for instanced variable")
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER,0)

  def draw(self, type, objectIndex, num=0, offset=0):
    self.load()
    self._setitems()
    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glDrawElementsInstancedBaseInstance(
                               type,
                               self.objInfo[objectIndex].renderVerts,
                               gl.GL_UNSIGNED_INT,
                               None,
                               num,
                               offset
                               )

class TesselationShader(Shader):
  def __init__(self, name, frag, vert, geom, tessC, tessE):
    super(TesselationShader, self).__init__(name)
    self.addProgram(gl.GL_VERTEX_SHADER, vert)
    if geom:
      self.addProgram(gl.GL_GEOMETRY_SHADER, geom)
    self.addProgram(gl.GL_FRAGMENT_SHADER, frag)
    self.addProgram(gl.GL_TESS_CONTROL_SHADER, tessC)
    self.addProgram(gl.GL_TESS_EVALUATION_SHADER, tessE)
    self.build()

  def draw(self, number, objectIndex):
    self.load()
    self._setitems()
    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glPatchParameteri(gl.GL_PATCH_VERTICES, 3)
    gl.glDrawArrays(gl.GL_PATCHES, 0, number)

class TransformFeedbackShader(Shader):
  def addOutput(self, name):
    """Registers an output of the transform shader."""
    varyings = ctypes.c_char_p(name)
    varyings_pp = ctypes.cast(ctypes.pointer(varyings), ctypes.POINTER(ctypes.POINTER(gl.GLchar)))
    gl.glTransformFeedbackVaryings(self.program, 1, varyings_pp, gl.GL_INTERLEAVED_ATTRIBS)

  def getOutputBufferObject(self, objectIndex, max_size):
    """Gets an output buffer for the given input object.

    TODO Not sure about this here.  How should we be doing this better?"""
    tbo = gl.glGenBuffers(1)

    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glBindBuffer(gl.GL_TRANSFORM_FEEDBACK_BUFFER, tbo)
    gl.glBufferData(gl.GL_TRANSFORM_FEEDBACK_BUFFER, max_size, None, gl.GL_STATIC_READ)
    gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, tbo)

    return tbo

  def draw(self, type, objectIndex, count=0):
    """Starts a transform feedback draw.  Return the number of items actually
    created (may differ from `num` due to geometry shaders)."""
    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glEnable(gl.GL_RASTERIZER_DISCARD)
    query = gl.glGenQueries(1)
    gl.glBeginQuery(gl.GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN, query)
    gl.glBeginTransformFeedback(type)
    gl.glDrawArrays(gl.GL_POINTS, 0, count)
    gl.glEndTransformFeedback()
    gl.glEndQuery(gl.GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN)
    gl.glDisable(gl.GL_RASTERIZER_DISCARD)
    gl.glFlush()
    count = gl.glGetQueryObjectiv(query, gl.GL_QUERY_RESULT)
    gl.glDeleteQueries(1, [query])
    return count

gl.glFlush()

shaders = {}

def setUniversalUniforms(shader):
  for key, value in universalUniforms.items():
    shader[key] = value

def updateUniversalUniform(key, value):
  for name, shader in shaders.items():
    shader[key] = value
  universalUniforms[key] = value

def readShaderFile(filename):
  source = open(filename).read()
  p = re.compile(r"#include\W(.+);")
  m = p.search(source)
  while m:
    included = readShaderFile(m.group(1))
    source = source.replace("#include {};".format(m.group(1)), included)
    m = p.search(source)
  return source

def getShader(name, tess=False, instance=False, geom=False, forceReload=True):
  global shaders
  if name not in shaders or forceReload:
    logging.info("Loading shader '{:s}'".format(name))
    if not tess:
      if not instance:
        shaders[name] = GenericShader(
                               name,
                               readShaderFile('shaders/'+name+'/fragment.shd'),
                               readShaderFile('shaders/'+name+'/vertex.shd'),
                               geom and readShaderFile('shaders/'+name+'/geometry.shd')
                               )
      else:
        shaders[name] = InstancedShader(
                               name,
                               readShaderFile('shaders/'+name+'/fragment.shd'),
                               readShaderFile('shaders/'+name+'/vertex.shd'),
                               geom and readShaderFile('shaders/'+name+'/geometry.shd')
                               )
    else:
      shaders[name] = TesselationShader(
                               name,
                               readShaderFile('shaders/'+name+'/fragment.shd'),
                               readShaderFile('shaders/'+name+'/vertex.shd'),
                               geom and readShaderFile('shaders/'+name+'/geometry.shd'),
                               readShaderFile('shaders/'+name+'/tesscontrol.shd'),
                               readShaderFile('shaders/'+name+'/tesseval.shd')
                               )
    setUniversalUniforms(shaders[name])
  return shaders[name]

def setUniform(name,value):
  for i in shaders:
    shaders[i][name] = value
