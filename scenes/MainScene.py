from Scene import Scene
import OpenGL.GL as gl
import Shaders
import transforms
import numpy as np
from RenderPipeline import RenderPipeline
from RenderStage import RenderStage
import messaging
import spells
import lighting
Re = 6.360e6

class MainScene(Scene):
  def __init__(self):
    super(MainScene, self).__init__()
    import Terrain
    self.Terrain = Terrain
    self.camera.position = np.array([ 0., 1356.92767998,-1000])
    self.camera.move_hook=lambda x:np.array((x[0],
            max(self.Terrain.getAt(x[0],x[2])+0.6,x[1]),x[2]))
    self.camera.radiusCentre = np.array([0,-Re,0])
    self.camera.minRadius = Re

    import Sky
    self.Sky = Sky

    import Map
    self.Map = Map

    import Shadows
    self.Shadows = Shadows
    self.Shadows.shadowCamera.lockObject = self.camera

    import grass
    self.grass = grass

    import Forest
    self.Forest = Forest

    import Characters
    self.Characters = Characters

    import Buildings
    self.Buildings = Buildings

    import particles
    self.particles = particles

    import postrender
    self.postrender = postrender

    self.fastMode = False
    self.enableAtmosphere = True
    self.line = False
    self.flycam = None

    self.renderStages = [RenderStage(render_func=self.main_display)      ,
                         RenderStage(render_func=self.lighting_display   , clear_depth=False) ,
                         RenderStage(render_func=self.sky_display        , clear_depth=False) ,
                         RenderStage(render_func=self.postrender_display , clear_depth=False  , final_stage=True)
                         ]

    self.renderPipeline = RenderPipeline(self.renderStages)

    messaging.add_handler('horse', self.horse_handler)
    messaging.add_handler('accio', self.accio_handler)
    messaging.add_handler('add_light', self.add_light_handler)
    messaging.add_handler('spell', self.spell_handler)

  def main_display(self, width, height, **kwargs):
    if self.line:
      gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_LINE)
    gl.glEnable(gl.GL_CULL_FACE)
    self.camera.render()
    projection = transforms.perspective( 60.0, width/float(height), 0.3, 1e7 )
    Shaders.updateUniversalUniform('projectionNear', 0.3)
    Shaders.updateUniversalUniform('projectionFar', 1e7)
    Shaders.setUniform('projection', projection)
    Shaders.setUniform('aspectRatio', width/float(height))
    Shaders.setUniform('windowWidth', float(width))

    self.camera.render()
    self.camera.render('user')

    self.Terrain.display(self.camera)
    self.grass.display(self.camera)
    self.Forest.display(self.camera.position)
    self.Characters.display(self.camera)
    self.Buildings.display(self.camera)

    self.particles.render_all()
    gl.glDisable(gl.GL_CULL_FACE)
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_FILL);


  def lighting_display(self, previous_stage, **kwargs):
    self.postrender.lighting(previous_stage)


  def sky_display(self, previous_stage, **kwargs):
    self.Sky.display(previous_stage)


  def postrender_display(self, width, height, previous_stage, **kwargs):
    self.postrender.display(previous_stage, width, height)
    self.Map.display()


  def render(self, windowWidth, windowHeight):
    self.renderStages[2].enabled = self.enableAtmosphere

    self.camera.render('user')
    self.Shadows.render(self)

    super(MainScene, self).render(windowWidth, windowHeight)

  def timer(self, fps):
    self.Map.update(1.0/fps)
    self.Forest.update(self.camera.position)
    self.Characters.update()

    if self.flycam:
      self.flycam.update(self.camera)

    p = self.camera.position + np.array([0,Re,0])
    if self.fastMode:
      self.cameraSpeed = max((p.dot(p)**0.5-Re-1000)*3+90,0)
    else:
      self.cameraSpeed = max((p.dot(p)**0.5-Re-1000)*.1+90,0)
    f = np.clip((p.dot(p)**0.5 - Re*1.03) /(Re*0.3),0,1)
    globUp = np.array([np.array([1.0,0.0,0.0]),
                       p/p.dot(p)**0.5])
    self.camera.globalUp = (globUp[0]*f + globUp[1]*(1-f))
    self.camera.globalUp /= self.camera.globalUp.dot(self.camera.globalUp)**0.5
    t = np.cross(self.camera.globalUp,self.camera.globalRight)
    self.camera.globalRight = np.cross(t,self.camera.globalUp)
    self.camera.globalRight /= self.camera.globalRight.dot(self.camera.globalRight)**0.5

    self.Terrain.updatePageTable(self.camera)

    self.particles.update(self.Shadows.gameTime)

    self.Shadows.gameTime += 3e-4

  def key(self, key):
    if key=='o':
      self.enableAtmosphere = not self.enableAtmosphere
    if key=='f':
      self.fastMode = not self.fastMode
    if key=='n':
      self.postrender.showNormals = (self.postrender.showNormals + 1) % 3
    if key=='m':
      self.Map.targetFullScreenAmount = 1-self.Map.targetFullScreenAmount
    if key=='p':
      self.line = not self.line
    if key=='l':
      if self.camera.lockObject:
        self.camera.lockObject = None
      else:
        self.camera.lockObject = self.Characters.character
    if key=='0':
      messaging.add_message(messaging.Message('add_light',()))
    if key=='z':
      messaging.add_message(messaging.Message('spell',('idea',)))
    if key=='Z':
      messaging.add_message(messaging.Message('spell',('fountain',)))
    if key=='y':
      if self.flycam:
        flycam = None
      else:
        import flyCam
        self.flycam = flyCam

  def horse(self, i=0):
    messaging.add_message(messaging.Message('horse',(i,)))

  def accio(self):
    messaging.add_message(messaging.Message('accio',()))

  def accio_handler(self):
    self.Characters.character.position = self.camera.position.copy()

  def horse_handler(self, i):
    self.camera.position = self.Buildings.clumpSpecs[i].position
    self.camera.update()
    self.accio()
    self.Characters.move(0)

  def add_light_handler(self):
    lighting.addLight(self.Characters.character.position,
        [random.random()*0.5+0.5, random.random()*0.5+0.5, random.random()*0.5+0.5])

  def spell_handler(self, type):
    if type == 'idea':
      self.particles.add_system(spells.IdeaSpellParticles(self.Characters.character.position[:]))
    elif type == 'fountain':
      self.particles.add_system(spells.FountainSpellParticles(self.Characters.character.position[:]))
    else:
      logging.warn('Unknown spell "{}"'.format(type))
