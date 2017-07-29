import OpenGL.GL as gl
import OpenGL.GL.framebufferobjects as glfbo
import Texture


class RenderStage(object):
  def __init__(self, render_func=None, final_stage=False, depth_only=False, clear_depth=True):
    """Constructs a render stage.  If the state is 'final', then rendering to it
    will render to the default buffer of id 0."""
    self.final_stage = final_stage
    self.width = None
    self.height = None
    self.depth_only = depth_only
    self.render = render_func
    self.clear_depth = clear_depth
    self.enabled = True
    if not final_stage:
      self.create_fbos()

  def load(self, width, height, offsetx=0, offsety=0, clear=None):
    """Loads the render stage's buffers, clears them and sets the viewport.

    The depth buffer will always be cleared, but the color buffer is cleared
    only if the `clear` argument is true (default).

    If the stage is "final", the screen buffer will be loaded."""
    if not self.final_stage:
      gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.displayFBO)
    else:
      gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    if clear is None:
      clear = self.clear_depth
    if clear:
      gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
    else:
      gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

    self.width = width
    self.height = height
    gl.glViewport(offsetx, offsety, width, height)

  def reshape(self, width, height=None):
    if self.final_stage:
      return
    if height is None:
      height = width
    if not self.depth_only:
      self.displayColorTexture.loadData(None, width=width, height=height)
      self.displaySecondaryColorTexture.loadData(None, width=width, height=height)
      self.displayAuxColorTexture.loadData(None, width=width, height=height)
    self.displayDepthTexture.load()
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_DEPTH_COMPONENT32,
        width,
        height,
        0,
        gl.GL_DEPTH_COMPONENT,
        gl.GL_FLOAT,
        None)
    self.width = width
    self.height = height

  def create_fbos(self):
    self.displayFBO = gl.glGenFramebuffers(1)

    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.displayFBO)

    if not self.depth_only:
      self.displayColorTexture = Texture.Texture(Texture.COLORMAP)
      self.displayColorTexture.load()
      gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
      self.displayColorTexture.loadData(None, width=1, height=1)

      self.displaySecondaryColorTexture = Texture.Texture(Texture.COLORMAP2)
      self.displaySecondaryColorTexture.load()
      gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
      self.displaySecondaryColorTexture.loadData(None, width=1, height=1)

      self.displayAuxColorTexture = Texture.Texture(Texture.COLORMAP3)
      self.displayAuxColorTexture.load()
      gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
      self.displayAuxColorTexture.loadData(None, width=1, height=1)

    self.displayDepthTexture = Texture.Texture(Texture.DEPTHMAP)
    self.displayDepthTexture.load()
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_FUNC, gl.GL_LEQUAL)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_MODE, gl.GL_NONE)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_DEPTH_COMPONENT32, 1, 1, 0, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)

    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT,   self.displayDepthTexture.id, 0)
    if not self.depth_only:
      gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,  self.displayColorTexture.id, 0)
      gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT1,  self.displaySecondaryColorTexture.id, 0)
      gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT2,  self.displayAuxColorTexture.id, 0)
      gl.glDrawBuffers(3, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT1, gl.GL_COLOR_ATTACHMENT2])
    else:
      gl.glDrawBuffers(gl.GL_NONE)
    glfbo.checkFramebufferStatus()

  def __del__(self):
    """When the stage is deleted, we must get rid of any GPU resources we have
    requested."""
    gl.glDeleteFramebuffers([self.displayFBO])
