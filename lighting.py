import postrender
import numpy as np
import Pager

lightingShader = postrender.lightingShader

lightID = 0
lightPositions = np.zeros((100, 3), dtype=np.float32)
lightColours = np.zeros((100, 3), dtype=np.float32)

indices = Pager.Pager(100)

def addLight(position, colour):
  global lightID
  ID = lightID
  lightID += 1
  if ID not in indices:
    indices.add(ID)
  index = indices[ID]

  lightPositions[index] = position
  lightColours[index] = colour
  update()
  return ID

def removeLight(ID):
  if ID not in indices:
    return
  index = indices[ID]
  lightColours[index] = 0

def update():
  lightingShader['numLights'] = 100
  lightingShader['lightPositions'] = lightPositions
  lightingShader['lightColours'] = lightColours

update()
