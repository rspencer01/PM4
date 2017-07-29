import Camera
import numpy as np
from RenderStage import RenderStage
import logging
import Texture
import Shaders
import transforms

logging.info("Initialising Shadows")

shadowSize = 1024

logging.info("3 shadow maps at {}x{} ~ {}Mb".format(shadowSize, shadowSize, 3*shadowSize**2*16/1024**2))

sunDeclination = 22/180.0*3.141592
latitude = 3.1415/4
sunTheta = 5*3.1415/16
sunPhi = 0.3
gameTime = 0

shadowCamera = Camera.Camera(np.array([0.,300,0]), lockObject=None, lockDistance=40000)
shadowCamera.globalUp, shadowCamera.globalRight = shadowCamera.globalRight, shadowCamera.globalUp
shadowCamera.rotUpDown(sunTheta)
shadowCamera.rotLeftRight(sunPhi)
shadowCamera.update()

sunDirection = shadowCamera.direction

renderStages = [RenderStage(depth_only=True) for _ in xrange(3)]
for i in renderStages:
  i.reshape(shadowSize, shadowSize)
renderStages[0].displayDepthTexture.loadAs(Texture.SHADOWS1)
renderStages[1].displayDepthTexture.loadAs(Texture.SHADOWS2)
renderStages[2].displayDepthTexture.loadAs(Texture.SHADOWS3)

projections = []
for i in range(3):
  width = 20 * 15**i
  projections.append(transforms.ortho(-width,width,-width,width, 40000. - 2*width, 40000. + 2*width))
  Shaders.setUniform('shadowProjection'+str(i+1),projections[i])

count = 0

Shaders.setUniform('shadowTexture1',Texture.SHADOWS1_NUM)
Shaders.setUniform('shadowTexture2',Texture.SHADOWS2_NUM)
Shaders.setUniform('shadowTexture3',Texture.SHADOWS3_NUM)

def render(scene):
  global count,sunTheta
  sunTheta = gameTime

  shadowCamera.theta = sunTheta
  shadowCamera.phi = sunPhi

  shadowCamera.update()
  shadowCamera.render()

  sunDirection = -shadowCamera.direction
  Shaders.setUniform('sunDirection',sunDirection)

  for i in range(3):
    if count % 20 ** i != 0:
      continue
    if np.sum(shadowCamera.lockObject.position*shadowCamera.lockObject.position) > 6e4**2 or shadowCamera.lockObject.position[1]>4e3:
      if i<2:
        continue
    renderStages[i].load(shadowSize, shadowSize)
    Shaders.setUniform('projection',projections[i])
    shadowCamera.render('shadow'+str(i+1))

    scene.Terrain.display(shadowCamera.lockObject)
    scene.Characters.display(shadowCamera.lockObject)
    scene.Buildings.display(shadowCamera.lockObject)
    scene.grass.display(shadowCamera.lockObject)
    scene.Forest.display(shadowCamera.lockObject.position,i)

  Shaders.setUniform('shadowLevel',-1)

  count+=1
