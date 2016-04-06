import numpy as np
from transforms import *
from Shaders import *

class Camera:
  def __init__(self,pos):
    self.pos = pos
    # Spherical coordinates are used to show the direction we
    # are looking in
    self.theta = 0
    self.phi = 0 
    # The "global" variables are the frame in which we rotate.
    # This allows, for example, for us to go around the earth
    # and still have "up" being away from the surface
    self.globalUp = np.array([0.0,1.0,0.0])
    self.globalRight = np.array([1.0,0.0,0.0])

    self.direction = np.array([0.,0.,1.])
    self.update()

  def move(self,d):
    self.update()
    self.pos -= d*self.direction

  def rotUpDown(self,d):
    self.theta += d
#    self.update()

  def rotLeftRight(self,d):
    self.phi += d
#    self.update()

  def update(self):
    self.view = np.eye(4,dtype=np.float32)
    self.view[0:3,0] = self.globalRight[:]
    self.view[0:3,1] = self.globalUp[:]
    self.view[0:3,2] = np.cross(self.globalUp,self.globalRight)
    translate(self.view,-self.pos[0],-self.pos[1],-self.pos[2])
    rotate(self.view,self.phi*180/3.1415,0,1,0)
    rotate(self.view,self.theta*180/3.1415,1,0,0)

    self.direction = np.array([0,0,1])
    ch = np.eye(4,dtype=np.float32)
    ch[0:3,0] = self.globalRight[:]
    ch[0:3,1] = self.globalUp[:]
    ch[0:3,2] = np.cross(self.globalUp,self.globalRight)
    rotate(ch,self.phi*180/3.1415,0,1,0)
    rotate(ch,self.theta*180/3.1415,1,0,0)
    self.direction = ch[:3,:3].dot(self.direction)

  def render(self,name=''):
    self.update()
    setUniform(name+'View',self.view)
    setUniform(name+'CameraDirection',self.direction)
    setUniform(name+'CameraPosition',self.pos)
