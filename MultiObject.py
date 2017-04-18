import numpy as np
from pyassimp import *
import math
import Camera
import pdb
import Terrain
import random
import noiseG
import Texture
import Image
import os
import Shaders
from transforms import *
import OpenGL.GL as gl

shader          = Shaders.getShader('general',instance=True,forceReload=True)
shader['colormap'] = Texture.COLORMAP_NUM
billboardShader = Shaders.getShader('billboard',instance=True,forceReload=True)
billboardShader['colormap'] = Texture.COLORMAP_NUM
billboardShader['bumpmap'] = Texture.BUMPMAP_NUM
makeBillboardShader = Shaders.getShader('makeBillboard',instance=True,forceReload=True)

class MultiObject(object):
  def __init__(self,numSwatches):
    self.meshes = []
    self.renderIDs = []
    self.textures = []
    self.billboardMesh = None
    self.billboardRenderID = None
    self.billboardTexture = None
    self.instances = np.zeros(0,dtype=[('model',np.float32,(4,4))])
    self.numSwatches = numSwatches
    self.swatches = [[None for i in xrange(numSwatches)] for j in xrange(numSwatches)]
    self.frozen = False

  def loadFromScene(self,scenePath,scale):
    scene = load(scenePath)
    self.scale = scale
    self.directory = os.path.dirname(scenePath)
    self.boundingBox = (helper.get_bounding_box(scene))
    for i in xrange(3):
      self.boundingBox[0][i] *= scale
      self.boundingBox[1][i] *= scale
    def addNode(node,trans):
      newtrans = trans.dot(node.transformation)
      for msh in node.meshes:
        self.addMesh(msh,newtrans)
      for nod in node.children:
        addNode(nod,newtrans)
    addNode(scene.rootnode,np.eye(4))
    self.makeBillboard()
    self.makeBillboardMesh() 

  def addMesh(self,mesh,trans):
    data = np.zeros(len(mesh.vertices),
                      dtype=[("position" , np.float32,3),
                             ("normal"  , np.float32,3),
                             ("textcoord"  , np.float32,2),
                             ("color"    , np.float32,4)])
    # Get the vertex positions and add a w=1 component
    vertPos = mesh.vertices
    add = np.zeros((vertPos.shape[0],1),dtype=np.float32)+1
    vertPos = np.append(vertPos,add,axis=1)
    # Get the vertex normals and add a w=1 component
    vertNorm = mesh.normals
    add = np.zeros((vertNorm.shape[0],1),dtype=np.float32)
    vertNorm = np.append(vertNorm,add,axis=1)
    # Transform all the vertex positions.
    for i in xrange(len(vertPos)):
      vertPos[i] = trans.dot(vertPos[i])
      vertNorm[i] = trans.dot(vertNorm[i])
    # Splice correctly
    vertPos = vertPos[:,0:3]
    vertNorm = vertNorm[:,0:3]

    # Set the data
    data["position"] = vertPos*self.scale
    data["normal"] = vertNorm
    data["textcoord"] = mesh.texturecoords[0][:,[0,1]]
    data["color"] = [(1,1,1,1)]*len(mesh.vertices)

    # Get the indices
    indices = mesh.faces

    # Load the texture
    texture = Texture.Texture(Texture.COLORMAP)
    teximag = Image.open(self.directory+'/'+dict(mesh.material.properties.items())['file'])
    texdata = np.array(teximag.getdata()).astype(np.float32)
    # Make this a 4 color file
    if (texdata.shape[1]!=4):
      add = np.zeros((texdata.shape[0],1),dtype=np.float32)+256
      texdata = np.append(texdata,add,axis=1)
    texdata = texdata.reshape(teximag.size[0], teximag.size[1], 4)
    texture.loadData(texdata.shape[0],texdata.shape[1],texdata/256)

    #Add the textures and the mesh data
    self.textures.append(texture)
    self.meshes.append((data,indices,texture))

  def addInstance(self,model):
    self.instances.resize(len(self.instances)+1)
    self.instances['model'][-1] = model
    return len(self.instances)-1

  def freeze(self):
    for data,indices,texture in self.meshes:
      self.renderIDs.append(shader.setData(data,indices,self.instances))
    self.billboardRenderID = billboardShader.setData(self.billboardMesh[0],self.billboardMesh[1],self.instances)
    self.frozen = True

  def render(self,offset,num=None):
    shader.load()
    if num==None: num = len(self.instances)
    for mesh,renderID in zip(self.meshes,self.renderIDs):
      # Load texture
      mesh[2].load()
      shader.draw(gl.GL_TRIANGLES,renderID,num,offset)

  def renderBillboards(self,offset,num=None):
    if num==None: num = len(self.instances)
    # Load texture
    billboardShader.load()
    self.billboardTexture.load()
    self.billboardnormalTexture.load()
    billboardShader.draw(gl.GL_TRIANGLES,self.billboardRenderID,num,offset)

  def makeBillboard(self):
    numberOfSwatches = 1
    texSize = 1050
    
    instance = np.zeros(numberOfSwatches,dtype=[('model',np.float32,(4,4))])
    width = 2*max([(self.boundingBox[0][0]**2 + self.boundingBox[1][2]**2)**0.5,
                   (self.boundingBox[1][0]**2 + self.boundingBox[0][2]**2)**0.5,
                   (self.boundingBox[1][0]**2 + self.boundingBox[1][2]**2)**0.5,
                   (self.boundingBox[0][0]**2 + self.boundingBox[0][2]**2)**0.5])
    for i in xrange(numberOfSwatches):
      instance[i] = np.eye(4,dtype=np.float32)
      yrotate(instance['model'][i],i*360.0/numberOfSwatches)
      translate(instance['model'][i],i * width,0,0)
    renderIDs = []

    for data,indices,texture in self.meshes:
      renderIDs.append(makeBillboardShader.setData(data,indices,instance))

    framebuffer = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,framebuffer)

    self.billboardTexture = Texture.Texture(Texture.COLORMAP)
    self.billboardTexture.loadData(texSize*numberOfSwatches,texSize,np.ones((texSize*numberOfSwatches,texSize),dtype=[('',np.float32,4)]))
    self.billboardnormalTexture = Texture.Texture(Texture.BUMPMAP)
    self.billboardnormalTexture.loadData(texSize*numberOfSwatches,texSize,np.ones((texSize*numberOfSwatches,texSize),dtype=[('',np.float32,4)]))

    depthbuffer = gl.glGenRenderbuffers(1)
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER,depthbuffer)
    gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT,texSize*numberOfSwatches,texSize)
    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, depthbuffer)

    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0,self.billboardTexture.id,0);
    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT1,self.billboardnormalTexture.id,0);

    gl.glDrawBuffers(2,[gl.GL_COLOR_ATTACHMENT0,gl.GL_COLOR_ATTACHMENT1])
    gl.glViewport(0,0,texSize*numberOfSwatches,texSize)
    camera = Camera.Camera(np.array([0,0,40]))
    camera.render()
    camera.render('user')
    gl.glClear(gl.GL_DEPTH_BUFFER_BIT| gl.GL_COLOR_BUFFER_BIT)
    projection = ortho(-width/2,width/2 + (numberOfSwatches-1)*width,self.boundingBox[0][2],self.boundingBox[1][2], 0.1 ,100)
    Shaders.setUniform('projection',projection)

    for mesh,renderID in zip(self.meshes,renderIDs):
      mesh[2].load()
      makeBillboardShader['colormap'] = Texture.COLORMAP_NUM
      makeBillboardShader.draw(gl.GL_TRIANGLES,renderID,len(instance),0)
    self.billboardTexture.makeMipmap()
    self.billboardnormalTexture.makeMipmap()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)

    gl.glDeleteRenderbuffers(1,[depthbuffer])
    gl.glDeleteFramebuffers(1,[framebuffer])

  def makeBillboardMesh(self):
    width = 2*max([(self.boundingBox[0][0]**2 + self.boundingBox[1][2]**2)**0.5,
                   (self.boundingBox[1][0]**2 + self.boundingBox[0][2]**2)**0.5,
                   (self.boundingBox[1][0]**2 + self.boundingBox[1][2]**2)**0.5,
                   (self.boundingBox[0][0]**2 + self.boundingBox[0][2]**2)**0.5])
    data = np.zeros(4,
                      dtype=[("position" , np.float32,3),
                             ("normal"  , np.float32,3),
                             ("textcoord"  , np.float32,2),
                             ("color"    , np.float32,4)])
    data["position"] = [(-width/2,self.boundingBox[0][2],0),
                        (-width/2,self.boundingBox[1][2],0),
                        (width/2,self.boundingBox[1][2],0),
                        (width/2,self.boundingBox[0][2],0)]
    data["normal"] = [(1,1,1)]*4
    data["textcoord"] = [[0,0],[0,1],[1,1],[1,0]]
    data["color"] = [(1,1,1,1)]*4
    indices = np.array([0,1,2,2,0,3],dtype=np.int32)
    self.billboardMesh = (data,indices)

  def display(self,pos,shadows=False):
    if not self.frozen:
      return
    # Render the billboards
    indexPos = (int((pos[2]+30000)*self.numSwatches/60000),
                int((pos[0]+30000)*self.numSwatches/60000))
    #for i in xrange(max(0,indexPos[1]-40),min(self.numSwatches-1,indexPos[1]+41)):
#    for i in xrange(self.numSwatches-1):
#      stj,enj  = max(0,indexPos[0]-20),min(self.numSwatches-1,indexPos[0]-3)
#      stindex = self.swatches[stj][i].startIndex
#      enindex = self.swatches[enj][i].endIndex
#      self.renderBillboards(stindex,enindex-stindex)
#      if (i<indexPos[1]-2 or i>=indexPos[1]+3):
#        stj,enj  = max(0,indexPos[0]-2),min(self.numSwatches-1,indexPos[0]+3)
#        stindex = self.swatches[stj][i].startIndex
#        enindex = self.swatches[enj][i].endIndex
#        self.renderBillboards(stindex,enindex-stindex)
#      stj,enj  = max(0,indexPos[0]+4),min(self.numSwatches-1,indexPos[0]+21)
#      stindex = self.swatches[stj][i].startIndex
#      enindex = self.swatches[enj][i].endIndex
#      self.renderBillboards(stindex,enindex-stindex)
    self.renderBillboards(0,self.swatches[-1][-1].endIndex)
    return

    # Render the full geometries
    indexPos = (int((pos[2]+30000)*self.numSwatches/60000),
                int((pos[0]+30000)*self.numSwatches/60000))
    shader.load()
    for i in xrange(max(0,indexPos[1]-2),min(self.numSwatches-1,indexPos[1]+3)):
      stj,enj  = max(0,indexPos[0]-2),min(self.numSwatches-1,indexPos[0]+3)
      stindex = self.swatches[stj][i].startIndex
      enindex = self.swatches[enj][i].endIndex
      self.render(stindex,enindex-stindex)
#    clptpos = (pos + 3000) / (8000/self.numSwatches)
#    for i in xrange(int(math.floor(clptpos[0])-1),int(math.floor(clptpos[0])+2)):
#      if i<0 or i>=self.numSwatches: continue
      #      pdb.set_trace()
#      startj = int(math.floor(((-pos+4000)/(8000/self.numSwatches))[2]))-1
#      startj = min(self.numSwatches-3,max(0,startj))
#      self.render(self.swatches[startj][i].startIndex,
#                  self.swatches[startj+2][i].endIndex-self.swatches[startj][i].startIndex)
  #self.renderBillboards(0)

  def addSwatch(self,position,startIndex,points):
    # World position of swatch
    pos = (60000/self.numSwatches*position[0] - 30000,
           60000/self.numSwatches*position[1] - 30000)
    self.swatches[position[1]][position[0]] = Swatch(self,pos[0],pos[1],startIndex,points)
    return self.swatches[position[1]][position[0]].endIndex

numSwatch = 80
class Swatch:
  def __init__(self,owner,posx,posy,startIndex,points):
    self.posx = posx
    self.posy = posy
    self.startIndex = startIndex
    self.endIndex = startIndex
    self.owner = owner
    self.addTree(points)

  def addTree(self,points):
    for point in points:
      b = np.eye(4,dtype=np.float32)
      translate(b,point[0],point[1],point[2])
      self.owner.addInstance(b)
      self.endIndex+=1
