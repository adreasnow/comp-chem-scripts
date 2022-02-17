import numpy as np
from pymol.cgo import *
from pymol import cmd
import colorsys



class vecClass:
    def __init__(self, vec, origin, maxVec):
        x, y, z = vec
        hxy = np.hypot(x, y)
        size = np.hypot(hxy, z)

        hue = 130-(size*(130/maxVec))
        r, g, b = colorsys.hsv_to_rgb(hue/360, 1, 1)
        self.colour = [r, g, b]

        self.scalingFactor = 10
        self.coneRatio = 0.2
        self.coneWidthRatio = 0.2
        self.arrowRadiusRatio = 0.06
        
        self.origin = origin
        self.vec = np.multiply(vec, self.scalingFactor)

        # generate the field vector
        self.arrowStart = [0.0, 0.0, 0.0]
        az, el, self.arrowLength = self.cart2sph(*self.vec)
        self.coneRadius = self.arrowLength*self.coneWidthRatio
        self.arrowRadius = self.arrowLength*self.arrowRadiusRatio
        # self.coneRadius = 0.06
        # self.arrowRadius = 0.02
        self.coneStart = self.sph2cart(az, el, self.arrowLength-(self.arrowLength*self.coneRatio))
        
        # center the field vector
        centerOffset = self.sph2cart(az, el, -self.arrowLength/2)
        self.arrowStart = np.subtract(self.arrowStart, centerOffset)
        self.coneStart = np.subtract(self.coneStart, centerOffset)
        self.coneEnd = np.subtract(self.vec, centerOffset)

        # offset the field vector
        self.arrowStart = np.add(self.arrowStart, self.origin)
        self.coneStart = np.add(self.coneStart, self.origin)
        self.coneEnd = np.add(self.coneEnd, self.origin)

    @staticmethod
    def cart2sph(x, y, z):
        hxy = np.hypot(x, y)
        r = np.hypot(hxy, z)
        el = np.arctan2(z, hxy)
        az = np.arctan2(y, x)
        return(az, el, r)

    @staticmethod
    def sph2cart(az, el, r):
        rcos_theta = r * np.cos(el)
        x = rcos_theta * np.cos(az)
        y = rcos_theta * np.sin(az)
        z = r * np.sin(el)
        return(x, y, z)

    def arrow(self):
        cgoList = []
        # cgoList += [BEGIN, POINTS]
        cgoList += [CYLINDER]
        cgoList += list(self.arrowStart)
        cgoList += list(self.coneStart)
        cgoList += [self.arrowRadius] # cylinder radius
        cgoList += self.colour
        cgoList += self.colour
        cgoList += [CONE]
        cgoList += list(self.coneStart)
        cgoList += list(self.coneEnd)
        cgoList += [self.coneRadius, 0.0] # cone radius
        cgoList += self.colour
        cgoList += self.colour
        cgoList += [1.0, 0.0]
        # cgoList += [END]
        return(cgoList)

def plotEField(vecFile, pointFile, name='eField'):
    vecs = np.load(vecFile)
    points = np.load(pointFile)
    x, y, z = np.split(vecs, 3, 1)
    hxy = np.hypot(x, y)
    size = np.hypot(hxy, z)
    maxVec = np.max(size)

    cgoList = []
    for vec, origin in zip(vecs, points):
        cgoList +=  vecClass(vec, origin, maxVec).arrow()

    cmd.load_cgo(cgoList, name)
    cmd.reset()