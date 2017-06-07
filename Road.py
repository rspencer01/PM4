import numpy as np
import Shaders
import transforms
import OpenGL.GL as gl
import logging
import Terrain

pagingShader = Shaders.getShader('buildingPaging', forceReload=True)
data = np.zeros(4, dtype=[("position", np.float32, 3)])
data['position'] = [(-1, -1, 0.999999), (-1, 1, 0.999999), (1, -1, 0.999999), (1, 1, 0.999999)]
I = [0, 1, 2, 1, 2, 3]
indices = np.array(I, dtype=np.int32)
pagingRenderID = pagingShader.setData(data, indices)

def generateControls(start, end):
    curr = np.array(start, dtype=np.float32)
    end = np.array(end, dtype=np.float32)
    ans = []
    dr = (end - start) / np.linalg.norm(end-start)
    while (np.linalg.norm(end-curr) > 1000):
        ans.append(curr.copy())
        curr += dr*1000
    return ans

class Road(object):
    def __init__(self, start, end):
        self.controls = generateControls(start, end)
        Terrain.registerCallback(self.renderHeightmap)

    def renderHeightmap(self, x, y, width, height):
        for i in xrange(len(self.controls)-1):
            start, end = self.controls[i], self.controls[i+1]
            middle = (start+end)/2
            angle = np.arctan2(start[0] - end[0], start[1] - end[1])
            model = np.eye(4, dtype=np.float32)
            transforms.scale(model, 4, np.linalg.norm(end-start)/2, 1)
            transforms.zrotate(model, angle*180/3.1416)
            transforms.translate(model, x=middle[0], y=middle[1], z=0)

            transforms.translate(model, 30000 - y - height/2, x + width/2- 30000)
            transforms.scale(model, 1.6/width, -1.6/height, 1)

            pagingShader.load()
            pagingShader['model'] = model
            pagingShader['level'] = Terrain.getAt(middle[0], middle[1]) - 1000
            pagingShader.draw(gl.GL_TRIANGLES, pagingRenderID)
