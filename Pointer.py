import Terrain
import numpy as np
from dent.configuration import config

class Pointer(object):
  def __init__(self):
    self.position = np.array([0.,0.,0.])

  def update(self, camera_position, camera_direction):
    lo = 0
    hi = 1e2
    for _ in xrange(8):
      mi = (lo+hi)/2.
      test = camera_position + camera_direction * mi
      if Terrain.getAt(test[0],test[2]) > test[1]:
        hi = mi
      else:
        lo = mi

    self.position = camera_position + camera_direction*lo
