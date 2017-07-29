import Camera
import numpy as np
import OpenGL.GL as gl
import RenderStage
import Shaders
import transforms
Re = 6.360e6

class Scene(object):
  def __init__(self):
    self.camera = Camera.Camera()
    self.renderStages = [RenderStage.RenderStage(final_stage=False)]

  def render(self, windowWidth, windowHeight):
    pass

  def timer(self, fps):
    pass


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

    self.renderStages = [RenderStage.RenderStage(),
                         RenderStage.RenderStage(),
                         RenderStage.RenderStage(),
                         RenderStage.RenderStage(final_stage=True)
                         ]


  def render(self, windowWidth, windowHeight):
    gl.glEnable(gl.GL_CULL_FACE)
    self.camera.render('user')
    self.Shadows.render(self)

    if self.line:
      gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_LINE)
    self.renderStages[0].load(windowWidth, windowHeight)

    self.camera.render()
    projection = transforms.perspective( 60.0, windowWidth/float(windowHeight), 0.3, 1e7 )
    Shaders.updateUniversalUniform('projectionNear', 0.3)
    Shaders.updateUniversalUniform('projectionFar', 1e7)
    Shaders.setUniform('projection', projection)
    Shaders.setUniform('aspectRatio', windowWidth/float(windowHeight))
    Shaders.setUniform('windowWidth', float(windowWidth))

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
    self.renderStages[1].load(windowWidth, windowHeight, clear=False)
    self.postrender.lighting(self.renderStages[0].displayColorTexture,self.renderStages[0].displaySecondaryColorTexture,self.renderStages[0].displayAuxColorTexture,self.renderStages[0].displayDepthTexture)
    lastRenderStage = self.renderStages[1]

    if self.enableAtmosphere:
      self.renderStages[2].load(windowWidth, windowHeight, clear=False)
      self.Sky.display(lastRenderStage)
      lastRenderStage = self.renderStages[2]

    self.renderStages[3].load(windowWidth, windowHeight, clear=False)
    self.postrender.display(lastRenderStage,windowWidth,windowHeight)
    self.Map.display()
    lastRenderStage = self.renderStages[3]

  def timer(self, fps):
    self.Map.update(1.0/fps)
    self.Forest.update(self.camera.position)
    self.Characters.update()

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


class SplashScene(Scene):
  pass
