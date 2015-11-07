import ctypes
import numpy as np
import OpenGL.GL as gl
from ctypes import c_void_p, sizeof

currentShader = None

class objectInfo:
  def __init__(self,nv,ni,vbo,ver,ibo,renderVerts,instbo=None):
    self.numVertices = nv
    self.numIndices = ni
    self.vbo = vbo
    self.vertexArray = ver
    self.ibo = ibo
    self.instbo = instbo
    self.renderVerts = renderVerts
  def __repr__(self):
    return "<objectInfo (v/i {:d}/{:d} | vbo/ibo/ver/instbo {:d}/{:d}/{:d}/{:d}>".format(self.numVertices,self.numIndices,self.vbo,self.ibo,self.vertexArray,self.instbo)

class Shader(object):
  def __init__(self,name):
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

  def addProgram(self,type,source):
    prog = gl.glCreateShader(type)
    gl.glShaderSource(prog,source)
    gl.glCompileShader(prog)
    if gl.glGetShaderiv(prog, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
        raise RuntimeError(gl.glGetShaderInfoLog(prog))
    gl.glAttachShader(self.program,prog)
  
  def build(self):
    # Link!  Everything else is done in addProgram
    gl.glLinkProgram(self.program)
    if gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS) != gl.GL_TRUE:
      raise RuntimeError(gl.glGetProgramInfoLog(self.program))
    for prog in self.programs:
      gl.glDetachShader(self.program,prog)

  def load(self):
    # Check if we are loaded already.  If not do so.
    global currentShader
    if currentShader != self:
      gl.glUseProgram(self.program)
      currentShader = self

  def setData(self,data,indices,instanced=False):
    vbo = gl.glGenBuffers(1)
    ibo = gl.glGenBuffers(1)
    vertexArray = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vertexArray)
    self.objInfo.append( objectInfo(len(data),
                                    len(indices),
                                    vbo,
                                    vertexArray,
                                    ibo,
                                    len(indices)*3
                                    ) ) 

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER,vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER,data.nbytes,data,gl.GL_STATIC_DRAW)
    stride = data.strides[0]
    offsetc = 0
    for i in data.dtype.names:
      offset = ctypes.c_void_p(offsetc)
      loc = gl.glGetAttribLocation(self.program,i)
      if loc==-1:
        print "Error setting "+i+" in shader " + self.name
        offsetc += data.dtype[i].itemsize
        continue
      gl.glEnableVertexAttribArray(loc)
      gl.glBindBuffer(gl.GL_ARRAY_BUFFER,vbo)
      gl.glVertexAttribPointer(loc,np.prod(data.dtype[i].shape),gl.GL_FLOAT,False,stride,offset)
      gl.glVertexAttribDivisor(loc,0)
      offsetc += data.dtype[i].itemsize

    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER,ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,indices.nbytes,indices, gl.GL_STREAM_DRAW); 

    return len(self.objInfo)-1

  def deleteData(self,dataId):
    obj = self.objInfo[dataId]
    gl.glDeleteBuffers([obj.vbo,obj.ibo])
    gl.glDeleteVertexArrays(obj.vertexArray)

  def __setitem__(self,i,v):
    self.load()
    if i not in self.locations:
      self.locations[i] = gl.glGetUniformLocation(self.program,i)
    loc = self.locations[i]
    if loc==-1:
      if not i in self.warned:
        print "Error setting variable "+i+" in "+self.name+".  Maybe optimised out?"
        self.warned.add(i)
      return
    if type(v) == np.ndarray and v.shape == (4,4):
      gl.glUniformMatrix4fv(loc,1,gl.GL_FALSE,v)
      return      
    if type(v) in [float,np.float32,np.float64]:
      gl.glUniform1f(loc,v)
      return
    if type(v) in [np.ndarray] and v.shape==(3,):
      gl.glUniform3f(loc,v[0],v[1],v[2])
      return
    if type(v) in [int]:
      gl.glUniform1i(loc,v)
      return

  def draw(self,type,objectIndex,num=0):
    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glDrawElements(type,self.objInfo[objectIndex].numIndices,gl.GL_UNSIGNED_INT,None)

class GenericShader(Shader):
  def __init__(self,name,frag,vert,geom):
    super(GenericShader,self).__init__(name)
    self.addProgram(gl.GL_VERTEX_SHADER,vert)
    if geom:
      self.addProgram(gl.GL_GEOMETRY_SHADER,geom)
    self.addProgram(gl.GL_FRAGMENT_SHADER,frag)
    self.build()

class InstancedShader(GenericShader):
  def setData(self,data,indices,instanced):
    renderId = super(InstancedShader,self).setData(data,indices)
    instbo = gl.glGenBuffers(1)
    self.objInfo[renderId].instbo = instbo

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER,instbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER,instanced.nbytes,instanced,gl.GL_STREAM_DRAW)
    stride = instanced.strides[0]
    offsetc = 0
    for i in instanced.dtype.names:
      offset = ctypes.c_void_p(offsetc)
      loc = gl.glGetAttribLocation(self.program,i)
      if loc==-1:
        print "Error setting "+i+" in shader "+self.name
        continue
      gl.glBindBuffer(gl.GL_ARRAY_BUFFER,instbo)
      if instanced.dtype[i].shape==(4,4):
        for j in range(4):
          offset = ctypes.c_void_p(j*stride/4)
          gl.glEnableVertexAttribArray(loc+j)
          gl.glVertexAttribPointer(loc+j,4,gl.GL_FLOAT,False,stride,offset)
          gl.glVertexAttribDivisor(loc+j,1)
          offsetc+=4*2
      else:
        raise Exception("Type wrong for instanced variable")
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER,0)
    return renderId
  def draw(self,type,objectIndex,num=0,offset=0):
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
  def __init__(self,name,frag,vert,geom,tessC,tessE):
    super(TesselationShader, self).__init__(name)
    self.addProgram(gl.GL_VERTEX_SHADER,vert)
    if geom:
      self.addProgram(gl.GL_GEOMETRY_SHADER,geom)
    self.addProgram(gl.GL_FRAGMENT_SHADER,frag)
    self.addProgram(gl.GL_TESS_CONTROL_SHADER,tessC)
    self.addProgram(gl.GL_TESS_EVALUATION_SHADER,tessE)
    self.build()

  def draw(self,number,objectIndex):
    gl.glBindVertexArray(self.objInfo[objectIndex].vertexArray)
    gl.glPatchParameteri(gl.GL_PATCH_VERTICES,3)
    gl.glDrawArrays(gl.GL_PATCHES,0,number)


shaders = {}

def getShader(name,tess=False,instance=False,geom=False):
  global shaders
  if name not in shaders:
    print "Loading shader",name
    if not tess:
      if not instance:
        shaders[name] = GenericShader(
                               name,
                               open('shaders/'+name+'/fragment.shd','r').read(),
                               open('shaders/'+name+'/vertex.shd','r').read(),
                               geom and open('shaders/'+name+'/geometry.shd','r').read()
                               )
      else:
        shaders[name] = InstancedShader(
                               name,
                               open('shaders/'+name+'/fragment.shd','r').read(),
                               open('shaders/'+name+'/vertex.shd','r').read(),
                               geom and open('shaders/'+name+'/geometry.shd','r').read()
                               )
    else:
      shaders[name] = TesselationShader(
                               name,
                               open('shaders/'+name+'/fragment.shd','r').read(),
                               open('shaders/'+name+'/vertex.shd','r').read(),
                               geom and open('shaders/'+name+'/geometry.shd','r').read(),
                               open('shaders/'+name+'/tesscontrol.shd','r').read(),
                               open('shaders/'+name+'/tesseval.shd','r').read()
                               )
      
  return shaders[name]

def setUniform(name,value):
  for i in shaders:
    shaders[i][name] = value
