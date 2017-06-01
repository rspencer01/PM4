import OpenGL.GL as gl
import os
import numpy as np
import pyassimp
import pyassimp.material
import Texture
import Image
import Shaders
import transforms
import logging
import taskQueue
import threading
import Terrain
from collections import namedtuple

MeshOptions = namedtuple("MeshOptions", ('has_bumpmap'))
MeshDatum = namedtuple("MeshDatum", ('data', 'indices', 'colormap', 'normalmap', 'options'))

def getOptionNumber(meshOptions):
  ans = 0
  for i,v in enumerate(meshOptions):
    if v:
      ans += 2 ** i
  return ans

def getTexturePath(path):
  """This is a stupid hack required for particular unity assets."""
  if path[:19] == '..\\..\\..\\..\\..\\tex\\':
    return 'textures/'+path[19:]
  return path

def getTextureFile(material, textureType):
  if ('file', textureType) in material.properties:
    return material.properties[('file', textureType)]
  return ''
shader             = Shaders.getShader('general-noninstanced', forceReload=True)
shader['colormap'] = Texture.COLORMAP_NUM

class Object:
  def __init__(
      self,
      filename,
      name=None,
      scale=1,
      position=np.zeros(3),
      offset=np.zeros(3)):

    if name == None:
      name = os.path.basename(filename)

    logging.info("Creating object {}".format(name))

    self.filename = filename
    self.directory = os.path.dirname(filename)
    self.name = name
    self.scene = None
    self.meshes = []
    self.renderIDs = []
    self.textures = []
    self.scale = scale
    self.position = np.array(position, dtype=np.float32)
    self.offset = np.array(offset, dtype=np.float32)
    self.direction = np.array((0,0,1), dtype=float)
    self.bidirection = np.array((1,0,0), dtype=float)

    thread = threading.Thread(target=self.loadFromFile)
    thread.setDaemon(True)
    thread.start()


  def __del__(self):
    logging.info("Releasing object {}".format(self.name))
    # Release the pyassimp, as we no longer need it
    pyassimp.release(self.scene)


  def loadFromFile(self):
    logging.info("Loading object {} from {}".format(self.name, self.filename))
    self.scene = pyassimp.load(self.filename)

    def addNode(node, trans):
      newtrans = trans.dot(node.transformation)
      for msh in node.meshes:
        self.addMesh(msh, newtrans)
      for nod in node.children:
        addNode(nod, newtrans)

    t = np.eye(4)
    t[:3] *= self.scale
    addNode(self.scene.rootnode, t)


  def addMesh(self, mesh, trans):
    logging.info("Loading mesh {}".format(mesh.__repr__()))
    options = MeshOptions(False)
    data = np.zeros(len(mesh.vertices),
                      dtype=[("position" , np.float32,3),
                             ("normal"   , np.float32,3),
                             ("textcoord", np.float32,2),
                             ("tangent"  , np.float32,3),
                             ("bitangent", np.float32,3)])
    # Get the vertex positions and add a w=1 component
    vertPos = mesh.vertices
    add = np.ones((vertPos.shape[0], 1),dtype=np.float32)
    vertPos = np.append(vertPos, add, axis=1)
    # Get the vertex normals and add a w=1 component
    vertNorm = mesh.normals
    add = np.zeros((vertNorm.shape[0],1),dtype=np.float32)
    vertNorm = np.append(vertNorm, add, axis=1)

    tinvtrans = np.linalg.inv(trans).transpose()
    # Transform all the vertex positions.
    for i in xrange(len(vertPos)):
      vertPos[i] = trans.dot(vertPos[i])
      vertNorm[i] = tinvtrans.dot(vertNorm[i]) * self.scale
    # Splice correctly, killing last components
    vertPos = vertPos[:,0:3] - self.offset
    vertNorm = vertNorm[:,0:3]

    vertUV = mesh.texturecoords[0][:, [0,1]]
    vertUV[:, 1] = 1 - vertUV[:, 1]

    for triangle in mesh.faces:
      edge1 = vertPos[triangle[1]] - vertPos[triangle[0]]
      edge2 = vertPos[triangle[2]] - vertPos[triangle[0]]
      deltaUV1 = vertUV[triangle[1]] - vertUV[triangle[0]]
      deltaUV2 = vertUV[triangle[2]] - vertUV[triangle[0]]
      f = 1. / (deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1])

      data['tangent'][triangle[0]][0] = f * (deltaUV2[1] * edge1[0] - deltaUV1[1] * edge2[0])
      data['tangent'][triangle[0]][1] = f * (deltaUV2[1] * edge1[1] - deltaUV1[1] * edge2[1])
      data['tangent'][triangle[0]][2] = f * (deltaUV2[1] * edge1[2] - deltaUV1[1] * edge2[2])
      data['tangent'][triangle[0]] /= data['tangent'][triangle[0]].dot(data['tangent'][triangle[0]])**0.5
      data['bitangent'][triangle[0]][0] = f * (-deltaUV2[0] * edge1[0] + deltaUV1[0] * edge2[0])
      data['bitangent'][triangle[0]][1] = f * (-deltaUV2[0] * edge1[1] + deltaUV1[0] * edge2[1])
      data['bitangent'][triangle[0]][2] = f * (-deltaUV2[0] * edge1[2] + deltaUV1[0] * edge2[2])
      data['bitangent'][triangle[0]] /= data['bitangent'][triangle[0]].dot(data['bitangent'][triangle[0]])**0.5

    # Set the data
    data["position"] = vertPos
    data["normal"] = vertNorm
    data["textcoord"] = vertUV

    # Get the indices
    indices = mesh.faces.reshape((-1,))

    # Load the texture
    texture = Texture.Texture(Texture.COLORMAP, nonblocking=True)
    if getTextureFile(mesh.material, pyassimp.material.aiTextureType_DIFFUSE):
      texture.loadFromImage(self.directory+'/'+getTexturePath(getTextureFile(mesh.material, pyassimp.material.aiTextureType_DIFFUSE)))

    if getTextureFile(mesh.material, pyassimp.material.aiTextureType_NORMALS):
      normalTexture = Texture.Texture(Texture.NORMALMAP, nonblocking=True)
      options = options._replace(has_bumpmap=True)
      normalTexture.loadFromImage(self.directory+'/'+getTexturePath(getTextureFile(mesh.material, pyassimp.material.aiTextureType_NORMALS)))
    else:
      normalTexture = None
      options = options._replace(has_bumpmap=False)

    # Add the textures and the mesh data
    self.textures.append(texture)
    self.meshes.append(MeshDatum(data, indices, texture, normalTexture, options))

    def uploadMesh():
      self.renderIDs.append(shader.setData(data, indices))
      logging.info("Loaded mesh {}".format(mesh.__repr__()))

    taskQueue.addToMainThreadQueue(uploadMesh)


  def display(self):
    shader.load()
    t = np.eye(4, dtype=np.float32)
    t[2,0:3] = self.direction
    t[0,0:3] = self.bidirection
    transforms.translate(t, self.position[0],self.position[1],self.position[2])
    shader['model'] = t
    shader['colormap'] = Texture.COLORMAP_NUM
    shader['normalmap'] = Texture.NORMALMAP_NUM

    for meshdatum,renderID in zip(self.meshes,self.renderIDs):
      # Set options
      shader['options'] = getOptionNumber(meshdatum.options)
      # Load textures
      meshdatum.colormap.load()
      if meshdatum.options.has_bumpmap:
        meshdatum.normalmap.load()
      shader.draw(gl.GL_TRIANGLES, renderID)


  def __repr__(self):
    return "<pmObject \"{}\">".format(self.name)
