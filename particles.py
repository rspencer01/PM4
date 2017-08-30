import Shaders
import numpy as np
import OpenGL.GL as gl
import dent.Texture as Texture
import lighting

shader = Shaders.getShader('general', instance=True)
shader['colormap'] = Texture.COLORMAP_NUM

data = np.zeros(24, dtype=[("position" , np.float32,3),
                            ("normal"  , np.float32,3),
                            ("uv"  , np.float32,2)])
I = []
for i in range(8):
  I += [i*3, i*3+1, i*3+2]
h = 2 ** 0.5
data['position'] = [(-1, 0, -1), (0, h, 0), (-1, 0, 1),
                    (-1, 0, 1), (0, h, 0), (1, 0, 1),
                    (1, 0, 1), (0, h, 0), (1, 0, -1),
                    (1, 0, -1), (0, h, 0), (-1, 0, -1),
                    (-1, 0, -1), (0, -h, 0), (-1, 0, 1),
                    (-1, 0, 1), (0, -h, 0), (1, 0, 1),
                    (1, 0, 1), (0, -h, 0), (1, 0, -1),
                    (1, 0, -1), (0, -h, 0), (-1, 0, -1)]
data['normal']   = [(-1, 1, 0)] * 3 +\
                   [(0, 1, 1)] * 3 + \
                   [(1, 1, 0)] * 3 + \
                   [(0, 1, -1)] * 3 + \
                   [(-1, -1, 0)] * 3 + \
                   [(0, -1, 1)] * 3 + \
                   [(1, -1, 0)] * 3 + \
                   [(0, -1, -1)] * 3
data['uv'] = [0,0]
indices = np.array(I, dtype=np.int32)

class ParticleSystem(object):
  def __init__(self, position):
    self.position = position
    self.instances = np.zeros(0, dtype=[("model", np.float32, (4,4)),
                                        ("color", np.float32, (4,))])
    self.instbo = gl.glGenBuffers(1)
    self.renderID = shader.setData(data, indices, self.instances[:0], self.instbo)
    self.lightIDs = []
    self.particleCount = 10
    self.t0 = None
    self.alive = True
    self.lifetime = 1
    self.isLight = False
    self.lightIntensity = 1


  def isAlive(self, t):
    """Checks whether this particle system still has any alive particles left."""
    return t - self.t0 < self.lifetime


  def update(self, t):
    if self.t0 is None:
      self.t0 = t
    t -= self.t0

    self.instances = self.getCPUPositions(t)
    self.particleCount = len(self.instances)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.instbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, self.instances.nbytes, self.instances, gl.GL_STREAM_DRAW)

    if self.isLight:
      self.clearLights()
      for i in xrange(self.particleCount):
        particlePosition = np.dot(self.instances[i]['model'].T, np.array([0,0,0,1]))[:3]
        self.lightIDs.append(lighting.addLight(particlePosition, [self.lightIntensity,self.lightIntensity,self.lightIntensity]))


  def clearLights(self):
    """Removes all the lights from the lighting control."""
    for lightID in self.lightIDs:
      lighting.removeLight(lightID)
    self.lightIDs = []


  def display(self):
    """Displays all the particles."""
    Texture.getWhiteTexture().load()
    shader.draw(gl.GL_TRIANGLES, self.renderID, self.particleCount)


  def __del__(self):
    shader.deleteData(self.renderID)
    if self.isLight:
      self.clearLights()

systems = set()

def render_all():
  for i in systems:
    i.display()

def update(t):
  for i in systems:
    i.update(t)
  for i in list(systems):
    if not i.isAlive(t):
      systems.remove(i)

def add_system(system):
  systems.add(system)
