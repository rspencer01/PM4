import numpy as np
from transforms import *
from Shaders import *

class Camera:
  def __init__(self, pos, lockObject=None, lockDistance=10):
    self.pos = pos
    self.lockObject = lockObject
    self.lockDistance = lockDistance
    # Spherical coordinates are used to show the direction we
    # are looking in
    self.theta = 0
    self.phi = 0

    # There is a closest point we may get to the origin.  This
    # is a quick hack to prevent us going to the Earth
    self.minRadius = 0
    self.radiusCentre = np.array([0,0,0])
    # The "global" variables are the frame in which we rotate.
    # This allows, for example, for us to go around the earth
    # and still have "up" being away from the surface
    self.globalUp = np.array([0.0,1.0,0.0])
    self.globalRight = np.array([0.0,0.0,1.0])

    self.direction = np.array([0.,0.,1.])
    self.update()

  def move(self,d):
    self.update()
    if np.linalg.norm(self.pos-self.radiusCentre-d*self.direction) >= self.minRadius:
      self.pos += d * self.direction
      self.update()

  def rotUpDown(self,d):
    self.theta += d
    self.update()

  def rotLeftRight(self,d):
    self.phi += d
    self.update()

  def update(self):
    """Updates the internal representation of the camera, such as the view
    matrix and direction vector."""
    self.view = np.eye(4,dtype=np.float32)
    view2 = np.eye(4,dtype=np.float32)
    translate(self.view,-self.pos[0],-self.pos[1],-self.pos[2])
    view2[0:3,0] = np.cross(self.globalUp,self.globalRight)
    view2[0:3,1] = self.globalUp[:]
    view2[0:3,2] = self.globalRight[:]
    self.view = self.view.dot(view2)
    rotate(self.view,self.phi*180/3.1415,0,1,0)
    rotate(self.view,self.theta*180/3.1415,1,0,0)

    self.direction = np.array([0,0,-1])
    self.direction = self.view[:3,:3].dot(self.direction)

    if self.lockObject is not None:
      self.pos = self.lockObject.pos + self.lockDistance * self.direction * np.array((1,-1,-1))


  def render(self, name=''):
    """Set the uniforms in all the shaders.  Uniform names are `{name}View`,
    `{name}CameraDirection` and `{name}CameraPosition` for a given name.  This
    allows for multiple cameras to be "rendered" simultaniously."""
    self.update()
    setUniform(name+'View',self.view.T)
    setUniform(name+'CameraDirection',self.direction)
    setUniform(name+'CameraPosition',self.pos)
