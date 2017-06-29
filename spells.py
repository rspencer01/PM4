import numpy as np
import particles
import transforms

class IdeaSpellParticles(particles.ParticleSystem):
  def __init__(self, position):
    super(IdeaSpellParticles, self).__init__(position)
    self.lifetime = 0.05


  def getCPUPositions(self, t):
    """Called to get the number and positions of the particles at time `t`.
    Must return a numpy array of models."""
    N = 20
    particleCount = int((t/self.lifetime)*N)
    offset = -particleCount if particleCount < N/2 else -N/2
    particleCount = min(particleCount, N-particleCount)

    instances = np.zeros(particleCount, dtype=[("model", np.float32, (4,4)),
                                               ("color", np.float32, (4,))])
    for i in xrange(particleCount):
      instances[i] = np.eye(4, dtype=np.float32)
      instances['color'][i] = np.array([0.5,1.,0.5,1])
      transforms.scale(instances['model'][i], 0.1)
      transforms.translate(instances['model'][i], x=1, y=0, z=0)
      transforms.yrotate(instances['model'][i], 2*360/N*(i+offset)+5000*t)
      transforms.translate(instances['model'][i], x=0, y=(i+offset)/5.+5000*t/360*0.2*N, z=0)
      transforms.translate(instances['model'][i], *self.position)

    return instances


class FountainSpellParticles(particles.ParticleSystem):
  def __init__(self, position):
    super(FountainSpellParticles, self).__init__(position)
    self.lifetime = 0.05


  def getCPUPositions(self, t):
    """Called to get the number and positions of the particles at time `t`.
    Must return a numpy array of models."""
    N = 20
    instances = np.zeros(N, dtype=[("model", np.float32, (4,4)),
                                   ("color", np.float32, (4,))])
    for i in xrange(self.particleCount):
      instances['model'][i] = np.eye(4, dtype=np.float32)
      instances['color'][i] = np.array([1.,0.5,0.5,1])
      transforms.scale(instances['model'][i], 0.05)
      transforms.translate(instances['model'][i],
          x=0,
          y=-t * (t-self.lifetime) * 3000,
          z=t*100)
      transforms.yrotate(instances['model'][i], 360/N*i)
      transforms.translate(instances['model'][i], *self.position)

    return instances
