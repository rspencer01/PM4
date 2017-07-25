import Terrain 
import random
import numpy as np

prevpos = np.array([0.,0.,-1000.])
nextpos = np.array([100.,0.,-1000.])
nextpos[1] = max(nextpos[1], Terrain.getAt(nextpos[0], nextpos[2])+1)
prevpos[1] = max(prevpos[1], Terrain.getAt(prevpos[0], prevpos[2])+1)
speed = 10
height = 0

def update(camera):
  global nextpos, prevpos, speed, height
  d = (nextpos - camera.position)/np.linalg.norm(nextpos - camera.position)
  camheight = camera.position[1] - Terrain.getAt(camera.position[0], camera.position[2])
  p = camera.position + d * (speed + camheight / 100)
  camera.position = p.copy()
  camera.position[1] = max(camera.position[1], Terrain.getAt(camera.position[0], camera.position[2])+1)

  if np.linalg.norm(nextpos - camera.position) < 10 or np.linalg.norm(nextpos - camera.position) > 2e3:
    prevpos = nextpos
    a,b = (random.random()*0.5+0.5),(random.random()*0.5+0.5)
    nextpos = camera.position.copy() + np.array([
      a*a*a*2000,
      0,
      b*b*b*2000
      ])
    height += (random.random()-0.5) * 1000
    height = max(0, height)
    nextpos[1] = Terrain.getAt(nextpos[0], nextpos[2])+height
    dist = np.linalg.norm(nextpos - prevpos)
    speed = dist / 800
