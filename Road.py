import numpy as np
import heapq
import args
import assets
import random
import os
import Shaders
import transforms
import hashlib
import pickle
import OpenGL.GL as gl
import logging
import Terrain

pagingShader = Shaders.getShader('roadPaging')
data = np.zeros(4, dtype=[("position", np.float32, 3)])
data['position'] = [(-1, -1, 0.999999), (-1, 1, 0.999999), (1, -1, 0.999999), (1, 1, 0.999999)]
I = [0, 1, 2, 1, 2, 3]
indices = np.array(I, dtype=np.int32)
pagingRenderID = pagingShader.setData(data, indices)

def generateControls(start, end):
    """Sigh.  Don't try debug this too hard.  Its an A* counting the gradient as
    a weight."""
    start = np.array(start, dtype=np.float32)
    end = np.array(end, dtype=np.float32)

    logging.info("Generating road from {} to {}".format(start, end))

    curr = start.copy()

    ans = []
    def estimate(x):
      return np.linalg.norm(x - end)

    heap = [(estimate(start), 0, curr, None, 400, -1)]
    bst = {}
    endpoint = None

    for _ in xrange(300000):
      d, ln, curr, pth, lst, ang = heapq.heappop(heap)
      positionTuple = (int(curr[0]), int(curr[1]))
      if positionTuple not in bst:
        bst[positionTuple] = (ln,pth)

      if ln > bst[positionTuple][0]:
        continue
      bst[positionTuple] = ln, pth

      # Exit condition
      if estimate(curr) < 1000:
        endpoint = curr
        break

      for __ in xrange(10):
        if ang == -1:
          a = 2*3.4*random.random()
        else:
          a = ang + random.random() - 0.5

        n1 = curr + 400*np.array((np.cos(a), np.sin(a)))
        # Round to blocks
        n1 = 100.*np.floor(n1/100)
        # Avoid slipping off the world
        if abs(n1[0])>29000 or abs(n1[1])>29000:
          continue
        cost = np.linalg.norm(n1-curr)
        grd = abs(Terrain.heightmap.read((30000.+n1[0])/Terrain.planetSize,
                                         (30000.+n1[1])/Terrain.planetSize)[3] -
                  Terrain.heightmap.read((30000.+curr[0])/Terrain.planetSize, 
                                         (30000.+curr[1])/Terrain.planetSize)[3])
        cost += grd * 5
        # We need to avoid checking `>` on the positions as numpy complains
        # on equality checks that `heapq` implements.  This small random
        # offset should make each point unique.
        cost += random.random() / 10
        heapq.heappush(heap, (
          1.30*estimate(n1)+ln+cost,
          ln+cost,
          n1,
          curr,
          cost,
          a))
    if endpoint is None:
      ans = [end]
    else:
      while np.linalg.norm(endpoint - start) > 100:
        ans.append(endpoint)
        endpoint = bst[(int(endpoint[0]), int(endpoint[1]))][1]
      ans = ans[::-1]
      ans.append(end.copy())

    return ans

allControlPoints = []
def setRoadUniforms():
    Shaders.updateUniversalUniform('roadcontrols',
        np.insert(np.array(allControlPoints[::2]), 1, 0, axis=1)[:800])
    Shaders.updateUniversalUniform('roadcontrolscount',
        min(800, len(allControlPoints) / 2))


class Road(object):
    def __init__(self, start, end):
        global allControlPoints
        self.controls = assets.getAsset(
            'Road from {} to {}'.format(start,end),
            generateControls,
            (start, end),
            args.args.remake_roads)
        allControlPoints += self.controls
        setRoadUniforms()
        self.center = sum(self.controls)/len(self.controls)
        self.radius = max(
                [np.linalg.norm(i-self.center) for i in self.controls]
                )+1000
        Terrain.registerCallback(self.renderHeightmap)

    def renderHeightmap(self, x, y, width, height):
      #TODO This seems broken...
      #  if (y-30000-self.center[0])**2 + (x-30000-self.center[1])**2 > self.radius**2:
      #    return
        for i in xrange(len(self.controls)-1):
            start, end = self.controls[i], self.controls[i+1]
            middle = (start+end)/2
            angle = np.arctan2(start[0] - end[0], start[1] - end[1])
            model = np.eye(4, dtype=np.float32)
            transforms.scale(model, 16, np.linalg.norm(end-start)/2, 1)
            transforms.zrotate(model, angle*180/3.1416)
            transforms.translate(model, x=middle[0], y=middle[1], z=0)

            view = np.eye(4, dtype=np.float32)
            transforms.translate(view, 30000 - y - height/2, x + width/2- 30000)
            transforms.scale(view, 1.6/width, -1.6/height, 1)

            pagingShader.load()
            pagingShader['model'] = model
            pagingShader['view'] = view
            pagingShader['width'] = 4.
            pagingShader.draw(gl.GL_TRIANGLES, pagingRenderID)
