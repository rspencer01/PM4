import Object
import Terrain
import numpy as np

character = \
  Object.Object(
    'assets/knight/models/knight.fbx',
    'Knight',
    scale=0.01,
    position=(-183, 0,-2938),
    offset=(0, 2, 0))

def move(amount):
  character.position[0] += amount * character.direction[0]
  character.position[2] += amount * character.direction[2]
  character.position[1] = Terrain.getAt(character.position[0],character.position[2])+2

def setCharacterDirection(d):
  character.direction[0] = d[0]
  character.direction[1] = 0.
  character.direction[2] = d[2]
  print character.direction
  character.direction = character.direction / character.direction.dot(character.direction)**0.5
  character.bidirection = np.cross((0.,1.,0.),character.direction)

move(0)

def display(camera):
  character.display()
