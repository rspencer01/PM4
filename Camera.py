import numpy as np
from transforms import *
from Shaders import *
class Camera:
  def __init__(self,pos):
    self.pos = -pos
    self.theta = 0
    self.phi = 0 
    self.update()
    self.direction = np.array([0.,0.,1.])

  def move(self,d):
    self.pos += d*self.direction
    self.update()

  def rotUpDown(self,d):
    self.theta += d
    self.update()

  def rotLeftRight(self,d):
    self.phi += d
    self.update()

  def update(self):
    self.view = np.eye(4,dtype=np.float32)
    self.view[2,2] = -1
    translate(self.view,self.pos[0],self.pos[1],self.pos[2])
    rotate(self.view,self.phi*180/3.1415,0,1,0)
    rotate(self.view,self.theta*180/3.1415,1,0,0)
    self.direction = np.array([0.,0.,1.])
    ch = np.eye(4,dtype=np.float32)
    rotate(ch,self.phi*180/3.1415,0,1,0)
    rotate(ch,self.theta*180/3.1415,1,0,0)
    self.direction = ch[:3,:3].dot(self.direction)

  def render(self,name=''):
    setUniform(name+'View',self.view)
    setUniform(name+'CameraDirection',self.direction*np.array((-1,-1,1)))
    setUniform(name+'CameraPosition',self.pos*np.array((-1,-1,1)))



