import postrender
import numpy as np

lightingShader = postrender.lightingShader

numLights = 0
lightPositions = np.zeros((100, 3), dtype=np.float32)
lightColours = np.zeros((100, 3), dtype=np.float32)

def addLight(position, colour):
  global numLights
  print position, colour
  lightPositions[numLights] = position
  lightColours[numLights] = colour
  numLights += 1
  update()
  return numLights - 1

def update():
  lightingShader['numLights'] = numLights
  lightingShader['lightPositions'] = lightPositions
  lightingShader['lightColours'] = lightColours

update()
