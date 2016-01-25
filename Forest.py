import numpy as np
import random
import Image
import Camera 
import noiseG
from pyassimp import *

print "Loading trees"

#import Marker
import Terrain
import Texture 
from transforms import *
from Shaders import *

shader          = getShader('general',instance=True)
billboardShader = getShader('billboard',instance=True)
makeBillboardShader = getShader('makeBillboard',instance=True)

class Tree:
  def __init__(self):
    self.meshes = []
    self.renderIDs = []
    self.textures = []
    self.billboardMesh = None
    self.billboardRenderID = None
    self.billboardTexture = None
    self.instances = np.zeros(0,dtype=[('model',np.float32,(4,4))])
    self.scale = 50

  def loadFromScene(self,scene):
    self.boundingBox = (helper.get_bounding_box(scene))
    for i in xrange(3):
      self.boundingBox[0][i] *= self.scale
      self.boundingBox[1][i] *= self.scale
    def addNode(node,trans):
      newtrans = trans.dot(node.transformation)
      for msh in node.meshes:
        self.addMesh(msh,newtrans)
      for nod in node.children:
        addNode(nod,newtrans)
    addNode(scene.rootnode,np.eye(4))

  def addMesh(self,mesh,trans):
    data = np.zeros(len(mesh.vertices),
                      dtype=[("position" , np.float32,3),
                             ("normal"  , np.float32,3),
                             ("textcoord"  , np.float32,2),
                             ("color"    , np.float32,4)])
    vertPos = mesh.vertices
    add = np.zeros((vertPos.shape[0],1),dtype=np.float32)+1
    vertPos = np.append(vertPos,add,axis=1)
    vertNorm = mesh.normals
    add = np.zeros((vertNorm.shape[0],1),dtype=np.float32)
    vertNorm = np.append(vertNorm,add,axis=1)
    for i in xrange(len(vertPos)):
      vertPos[i] = trans.dot(vertPos[i])
      vertNorm[i] = trans.dot(vertNorm[i])
    vertPos = vertPos[:,0:3]
    vertNorm = vertNorm[:,0:3]

    data["position"] = vertPos*self.scale
    data["normal"] = vertNorm
    data["textcoord"] = mesh.texturecoords[0][:,[0,1]]
    data["color"] = [(1,1,1,1)]*len(mesh.vertices)
    indices = mesh.faces
    texture = Texture.Texture(Texture.COLORMAP)
    teximag = Image.open('assets/tree1/'+dict(mesh.material.properties.items())['file'])
    texdata = np.array(teximag.getdata()).astype(np.float32)
    if (texdata.shape[1]!=4):
      add = np.zeros((texdata.shape[0],1),dtype=np.float32)+256
      texdata = np.append(texdata,add,axis=1)
    texdata = texdata.reshape(teximag.size[0], teximag.size[1], 4)
    texture.loadData(texdata.shape[0],texdata.shape[1],texdata/256)
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

  def render(self,offset,num=None):
    if num==None: num = len(self.instances)
    for mesh,renderID in zip(self.meshes,self.renderIDs):
      # Load texture
      shader['colormap'] = Texture.COLORMAP_NUM
      mesh[2].load()
      shader.draw(gl.GL_TRIANGLES,renderID,num,offset)

  def renderBillboards(self,offset,num=None):
    if num==None: num = len(self.instances)
    # Load texture
    billboardShader['colormap'] = Texture.COLORMAP_NUM
    billboardShader['bumpmap'] = Texture.BUMPMAP_NUM
    self.billboardTexture.load()
    self.billboardnormalTexture.load()
    billboardShader.draw(gl.GL_TRIANGLES,self.billboardRenderID,num,offset)


  def makeBillboard(self):
    numberOfSwatches = 10
    texSize = 200
    
    instance = np.zeros(numberOfSwatches,dtype=[('model',np.float32,(4,4))])
    width = self.boundingBox[1][0]-self.boundingBox[0][0]
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
    projection = ortho(self.boundingBox[0][0],self.boundingBox[1][0]+(numberOfSwatches-1)*width,self.boundingBox[0][2],self.boundingBox[1][2], 0.1 ,100)
    setUniform('projection',projection)

    for mesh,renderID in zip(self.meshes,renderIDs):
      mesh[2].load()
      makeBillboardShader['colormap'] = Texture.COLORMAP_NUM
      makeBillboardShader.draw(gl.GL_TRIANGLES,renderID,len(instance),0)
    self.billboardTexture.makeMipmap()
    self.billboardnormalTexture.makeMipmap()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)

    self.makeBillboardMesh() 
  def makeBillboardMesh(self):
    data = np.zeros(4,
                      dtype=[("position" , np.float32,3),
                             ("normal"  , np.float32,3),
                             ("textcoord"  , np.float32,2),
                             ("color"    , np.float32,4)])
    data["position"] = [(self.boundingBox[0][0],self.boundingBox[0][2],0),
                        (self.boundingBox[0][0],self.boundingBox[1][2],0),
                        (self.boundingBox[1][0],self.boundingBox[1][2],0),
                        (self.boundingBox[1][0],self.boundingBox[0][2],0)]
    data["normal"] = [(1,1,1)]*4
    data["textcoord"] = [[0,0],[0,1],[1,1],[1,0]]
    data["color"] = [(1,1,1,1)]*4
    indices = np.array([0,1,2,2,0,3],dtype=np.int32)
    self.billboardMesh = (data,indices)


tree1 = Tree()
scene = load('assets/tree1/Tree N110314.3DS')
tree1.loadFromScene(scene)
tree1.makeBillboard()

numSwatch = 80
class Swatch:
  def __init__(self,posx,posy,startIndex):
    self.posx = posx
    self.posy = posy
    self.startIndex = startIndex
    self.endIndex = startIndex
    self.addTree()
  def addTree(self):
    for i in xrange(5):
      for j in xrange(5):
        b = np.eye(4,dtype=np.float32)
        posx = self.posx+i*(8000/numSwatch)/5+random.random()*16-8
        posy = self.posy+j*(8000/numSwatch)/5+random.random()*16-8
        if sum(map(lambda x:x**2,Terrain.getGradAt(-posx,-posy)))>0.4:
          continue;
        if noiseG.get(posx/30000.0, posy/30000.0)[3]**2 < 0.01:
          continue
#        yrotate(b,random.random()*360)
        translate(b,-posx,Terrain.getAt(-posx,-posy)[3]+12,-posy)
        tree1.addInstance(b)
        self.endIndex+=1
    
swatches = [[None for i in xrange(numSwatch)] for j in xrange(numSwatch)]
startIndex = 0
for i in xrange(numSwatch):
  for j in xrange(numSwatch):
    b = np.eye(4,dtype=np.float32)
    ps = (8000/numSwatch*i-4000,8000/numSwatch*j-4000)
    swatches[j][i] = Swatch(ps[0],ps[1],startIndex)
    startIndex = swatches[j][i].endIndex

tree1.freeze()
def display(pos,shadows=False):
  shader.load()
  shader['colormap'] = Texture.COLORMAP_NUM
  for i in xrange(int(round(((pos+4000)/(8000/numSwatch))[0]))-1,int(round(((pos+4000)/(8000/numSwatch))[0]))+2):
    startj = int(round(((-pos+4000)/(8000/numSwatch))[2]))-1
    tree1.render(swatches[startj][i].startIndex,swatches[startj+2][i].endIndex-swatches[startj][i].startIndex)
  if not shadows:
    tree1.renderBillboards(0)
