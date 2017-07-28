import Camera
import numpy as np

class Scene(object):
  def __init__(self):
    self.camera = Camera.Camera()

  def render(self):
    pass


class MainScene(Scene):
  def __init__(self):
    Re = 6.360e6
    super(MainScene, self).__init__()
    import Terrain
    self.Terrain = Terrain
    self.camera.position = np.array([ 0., 1356.92767998,-1000])
    self.camera.move_hook=lambda x:np.array((x[0],
            max(self.Terrain.getAt(x[0],x[2])+0.6,x[1]),x[2]))
    self.camera.radiusCentre = np.array([0,-Re,0])
    self.camera.minRadius = Re

    import grass
    self.grass = grass

    import Forest
    self.Forest = Forest

    import Characters
    self.Characters = Characters

    import Buildings
    self.Buildings = Buildings

  def render(self):
    self.camera.render()
    self.camera.render('user')

    self.Terrain.display(self.camera)
    self.grass.display(self.camera)
    self.Forest.display(self.camera.position)
    self.Characters.display(self.camera)
    self.Buildings.display(self.camera)

  def timer(self, fps):
    self.Forest.update(self.camera.position)
    self.Characters.update()

