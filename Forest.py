import numpy as np
from dent.configuration import config
import logging
import dent.MultiObject as MultiObject
import dent.Shaders as Shaders
import OpenGL.GL as gl

logging.info("Loading trees")

tree = MultiObject.MultiObject('assets/tree5/Conifers tree 1 N1006162.3DS', scale=15)

logging.info("Generating trees")

shaderObj = Shaders.TransformFeedbackShader('testTransform')
shaderObj.addProgram(gl.GL_VERTEX_SHADER, Shaders.ShaderFile('shaders/forestFeedback/vertex.shd', gl.GL_VERTEX_SHADER))
shaderObj.addProgram(gl.GL_GEOMETRY_SHADER, Shaders.ShaderFile('shaders/forestFeedback/geometry.shd',gl.GL_GEOMETRY_SHADER))
shaderObj.addOutput('outValue')
Shaders.setUniversalUniforms(shaderObj)

shaderObj.build()
shaderObj.load()

N = int(config.forest_tree_count ** 0.5)
shaderObj['scan'] = N
shaderObj['range'] = N * 12.
shaderObj['center'] = np.zeros(0, dtype=np.float32)
ips = np.zeros(N*N, dtype=[('id', np.int32, 1)])
ips['id'] = np.arange(N*N)

idd = shaderObj.setData(ips)
# On average one out of four trees is placed.
tbo = shaderObj.getOutputBufferObject(idd, 16*N*N*4)

count = shaderObj.draw(gl.GL_POINTS, idd, tbo, N*N)
logging.info("Generated {}K/{}K trees".format(count/1000, N**2/1000))

# Sample for the output format
r_data = np.zeros(1, dtype=[('model', np.float32, (4, 4))])

tree.instances = r_data
tree.numInstances = count

tree.freeze(instanceBuffer=tbo)
del ips

lastPosition = None

def update(position):
  global lastPosition
  ps = position[np.array((0,2))]
  k = (N*3) - ((N*3)%12)
  ps = ((ps/k).astype(int)*k).astype(np.float32)
  if (np.array_equal(ps, lastPosition)): return
  lastPosition = ps.copy()

  shaderObj['center'] = ps
  count = shaderObj.draw(gl.GL_POINTS, idd, tbo, N*N)
  logging.info("Generated {}K/{}K trees".format(count/1000, N**2/1000))
  tree.numInstances = count

def display(pos, shadows=False):
  tree.display(pos, shadows)
