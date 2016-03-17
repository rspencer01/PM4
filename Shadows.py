import Camera
import numpy as np
import OpenGL.GL as gl
#import Road
import Terrain
import Texture
#import Marker
import Forest 
import Shaders
import transforms

print "Initialising Shadows"

shadowSize = 2048

sunDeclination = 22/180.0*3.141592
latitude = 3.1415/4
sunTheta = 5*3.1415/16
sunPhi = 0

shadowCamera = Camera.Camera(np.array([0.,300,0]))
shadowCamera.rotUpDown(sunTheta)
shadowCamera.rotLeftRight(sunPhi)
shadowCamera.update()

sunDirection = shadowCamera.direction
#sunDirection[0],sunDirection[2] = sunDirection[2],sunDirection[0]
Shaders.setUniform('sunDirection',sunDirection*np.array((1,1,-1)))

shadowTexture1 = Texture.Texture(Texture.SHADOWS1)
shadowTexture2 = Texture.Texture(Texture.SHADOWS2)
shadowTexture3 = Texture.Texture(Texture.SHADOWS3) 
frameBuffers = [-1]*4

textures = [shadowTexture1,shadowTexture2,shadowTexture3]

for i in range(1,4):
  frameBuffers[i] = gl.glGenFramebuffers(1)
  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,frameBuffers[i] );

  textures[i-1].load()
  gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
  gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
  gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
  gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)    
  gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_FUNC,gl.GL_LEQUAL)
  gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_MODE,gl.GL_NONE)

  gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, shadowSize, shadowSize, 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)
  gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, textures[i-1].id, 0)
  gl.glDrawBuffer(gl.GL_NONE)
  if(gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE):
    raise "Error!"
  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0);
    

lockCam = None

count = 0

def render():
  global count,sunTheta
  # Get this right some day
  sunTheta = np.cos(count/200.0)*0.1
  sunTheta = -count/500.0+2.005
  shadowTexture1.load()
  shadowCamera.direction = np.array([0.,0.,1.])
  shadowCamera.theta = 0
  shadowCamera.phi = 0
  shadowCamera.rotUpDown(sunTheta)
  shadowCamera.rotLeftRight(sunPhi)
  sunDirection = shadowCamera.direction
  shadowCamera.pos = lockCam.pos - 4000*sunDirection*np.array((-1,1,1))
  Shaders.setUniform('sunDirection',sunDirection*np.array((1,1,-1)))
  shadowCamera.update()
  shadowCamera.render()
  shadowTexture1.load()
  shadowTexture2.load()
  shadowTexture3.load()
  gl.glViewport(0,0,shadowSize,shadowSize)

  for i in range(3):
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,frameBuffers[i+1] );
    gl.glClear(gl.GL_COLOR_BUFFER_BIT|gl.GL_DEPTH_BUFFER_BIT);
    width = 10 * 20**i
    projection = transforms.ortho(-width,width,-width,width, 4000. - 2*width, 4000. + 2*width)
    Shaders.setUniform('projection',projection)
    Shaders.setUniform('shadowProjection'+str(i+1),projection)
    Shaders.setUniform('shadowLevel',i)
    shadowCamera.render('shadow'+str(i+1))
  
    Terrain.display()
    #Marker.display()
    Forest.display(lockCam.pos,shadows=True)

    textures[i].makeMipmap()
  Shaders.setUniform('shadowLevel',-1)
    
  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0);
  
  
  Shaders.setUniform('shadowTexture1',Texture.SHADOWS1_NUM)
  Shaders.setUniform('shadowTexture2',Texture.SHADOWS2_NUM)
  Shaders.setUniform('shadowTexture3',Texture.SHADOWS3_NUM)

  count+=1
  
def cleanup():
  gl.glDeleteFramebuffers(frameBuffers[1:])
  for i in textures:
    del i
