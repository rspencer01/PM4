import numpy as np
import logging
import dent.Texture as Texture
import dent.Shaders as Shaders
import noise
import dent.args as args
import tqdm
import dent.assets as assets

logging.info("Loading noise texture")

noiseTexture = Texture.Texture(Texture.NOISE)
textHeight, textWidth = 1024, 1024

def generateNoise():
  logging.info("Recreating texture")
  d = np.zeros((textWidth, textHeight, 4), dtype=np.float32)
  # How many units?
  dx = 20
  dy = 20
  for i in tqdm.trange(textWidth, leave=False):
    for j in range(textHeight):
      s = float(i) / textWidth
      t = float(j) / textHeight
      x1 = 1
      y1 = 1
      nx = x1+np.cos(s*2*np.pi)*dx / (2*np.pi)
      ny = y1+np.cos(t*2*np.pi)*dy / (2*np.pi)
      nz = x1+np.sin(s*2*np.pi)*dx / (2*np.pi)
      nw = y1+np.sin(t*2*np.pi)*dy / (2*np.pi)

      t = noise.snoise4(nx, ny, nz, nw, octaves=10, persistence=0.5)
      d[i, j] = t
  d -= np.min(d)
  d /= np.max(d)-np.min(d)
  d *= 2
  d -= 1
  for i in tqdm.trange(textWidth, leave=False):
    for j in range(textHeight):
      v1 = np.array([float(i)/textWidth,   d[i, j][3],                float(j)/textWidth])
      v2 = np.array([float(i+1)/textWidth, d[(i+1)%textWidth, j][3],  float(j)/textWidth])
      v3 = np.array([float(i)/textWidth,   d[i, (j+1)%textHeight][3], float(j+1)/textWidth])
      d[i, j][:3] = np.cross(v3-v1, v2-v1)
      d[i, j][:3] /= np.linalg.norm(d[i, j][:3])
      d[i, j][0], d[i, j][2] = d[i, j][2], d[i, j][0]
  return d

d = assets.getAsset('noisedata', generateNoise, (), args.args.remake_noise)

logging.info("Uploading texture to GPU")
noiseTexture.loadData(d, keep_copy=True)
noiseTexture.load()

Shaders.updateUniversalUniform('noise', Texture.NOISE_NUM)
Shaders.updateUniversalUniform('noisemap', Texture.NOISE_NUM)

def get(x, y):
  return d[int(d.shape[0]*x)%d.shape[0]][int(d.shape[1]*y)%d.shape[1]]
