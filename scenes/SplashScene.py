from dent.Scene import Scene
from dent.RenderStage import RenderStage
import OpenGL.GL as gl
import dent.messaging as messaging
import dent.RectangleObjects as RectangleObjects
import noiseG

class SplashScene(Scene):
  def __init__(self):
    super(SplashScene, self).__init__()

    self.renderPipeline.stages.append(
        RenderStage(render_func=self.display, final_stage=True))

    self.pictureObject = RectangleObjects.ImageObject('assets/title.png')
    self.background = RectangleObjects.RectangleObject('splashscreen')

    self.time = 0.

    messaging.add_handler('timer', self.timer)

  def display(self, width, height, **kwargs):
    self.pictureObject.width = 952./width
    self.pictureObject.height = 123./height

    self.background.shader['time'] = self.time
    self.background.shader['aspectRatio'] = float(width)/height

    gl.glDisable(gl.GL_DEPTH_TEST)
    self.background.display()
    self.pictureObject.display()
    gl.glEnable(gl.GL_DEPTH_TEST)

  def timer(self, fps):
    self.time += 1./fps
