import dent.Object as Object
import dent.InstancedObject as InstancedObject
import Terrain
import numpy as np
import dent.transforms as transforms
import Buildings
import random
from dent.configuration import config

numberNPCs = config.npc_count

class Character(object):
  def __init__(self, index):
    self.index = index
    self.destination_town = random.choice(Buildings.clumpSpecs)
    self.position = np.array(random.choice([i.position for i in self.destination_town.buildings]))
    self.destination = self.position.copy()

  def update(self):
    while np.linalg.norm(self.destination - self.position) < 4:
      self.destination = random.choice([i.position for i in self.destination_town.buildings])
    self.position += (self.destination - self.position) / np.linalg.norm(self.destination - self.position)*0.1
    self.position[1] = Terrain.getAt(self.position[0],self.position[2])+2

npcs_object = \
  InstancedObject.InstancedObject(
    'assets/paladin/paladin_prop_j_nordstrom.fbx',
    'Knight',
    scale=0.01,
    position=(-183, 0,-2938),
    offset=(0, 2, 0))

instances = np.zeros(numberNPCs, dtype=[("model", np.float32, (4,4))])
npcs_object.addInstances(instances)

npcs = [Character(i) for i in xrange(numberNPCs)]

character = \
  Object.Object(
    'assets/paladin/paladin_prop_j_nordstrom.fbx',
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
  character.direction = character.direction / character.direction.dot(character.direction)**0.5
  character.bidirection = np.cross((0.,1.,0.),character.direction)

move(0)

npcs_object.freeze()

def update():
  for i in xrange(numberNPCs):
    npcs[i].update()

  for i in xrange(numberNPCs):
    npcs_object.instances['model'][i] = np.eye(4)
    transforms.translate(npcs_object.instances["model"][i], *npcs[i].position)
  npcs_object.refreeze()


def display(camera):
  character.display()
  npcs_object.display()
