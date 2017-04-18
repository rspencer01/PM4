import OpenGL.GL as gl
import OpenGL.GL.framebufferobjects as glfbo
import Texture

class RenderStage(object):
  def __init__(self, final_stage=False):
    self.final_stage = final_stage
    if not final_stage:
      self.create_fbos()

  def load(self, width, height):
    if not self.final_stage:
      gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.displayFBO)
    else:
      gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
    gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
    gl.glViewport(0, 0, width, height)

  def reshape(self, width, height):
    if self.final_stage: return
    self.displayColorTexture.loadData(width, height, None)
    self.displaySecondaryColorTexture.loadData(width, height, None)
    self.displayAuxColorTexture.loadData(width, height, None)
    self.displayDepthTexture.load()
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, width, height, 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)

  def create_fbos(self):
    self.displayFBO = gl.glGenFramebuffers(1)

    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.displayFBO)

    self.displayColorTexture = Texture.Texture(Texture.COLORMAP)
    self.displayColorTexture.load()
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    self.displayColorTexture.loadData(1,1,None)

    self.displaySecondaryColorTexture = Texture.Texture(Texture.COLORMAP2)
    self.displaySecondaryColorTexture.load()
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST_MIPMAP_NEAREST)
    self.displaySecondaryColorTexture.loadData(1,1,None)

    self.displayAuxColorTexture = Texture.Texture(Texture.COLORMAP3)
    self.displayAuxColorTexture.load()
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST_MIPMAP_NEAREST)
    self.displayAuxColorTexture.loadData(1,1,None)

    self.displayDepthTexture = Texture.Texture(Texture.DEPTHMAP)
    self.displayDepthTexture.load()
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_FUNC,gl.GL_LEQUAL)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_MODE,gl.GL_NONE)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, 1, 1, 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)

    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT,   self.displayDepthTexture.id, 0)
    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,  self.displayColorTexture.id, 0);
    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT1,  self.displaySecondaryColorTexture.id, 0);
    gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT2,  self.displayAuxColorTexture.id, 0);
    gl.glDrawBuffers(3, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT1, gl.GL_COLOR_ATTACHMENT2])
    glfbo.checkFramebufferStatus()