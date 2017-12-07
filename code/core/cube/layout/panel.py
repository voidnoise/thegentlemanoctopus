import numpy as np
import colorsys
import math



class Pixel:
    ''' Represents a chromatophore in octopusLayout space'''
    def __init__(self, location=(0,0,0), color=(0,0,0)):
        ''' location is the coordinate of the pixel'''
        self.location = location
        self.color = color

    def set_colour(self, color):
        self.color = color

    


class PixelStrip:
    ''' Represents a strip of addressable leds with nPixels  '''
    def __init__(self, origin=(0,0,0), colShift=(1.0,0.0,0.0), nPixels=1):
        
        self.origin = origin
        self.colShift = colShift
        self.nPixels = nPixels
        self.p_it=0
        self.pixels = []

        # print 'init_pixels origin', self.origin, 'colShift', self.colShift

        x = self.origin[0]
        y = self.origin[1]
        z = self.origin[2]

        for pixel in xrange(self.nPixels):
            self.pixels.append( Pixel(location=(x,y,z)) )
            x += self.colShift[0]
            y += self.colShift[1]
            z += self.colShift[2]

    def get_colours(self):
        colours = []
        for pixel in self.pixels:
            colours.append(pixel.color)
        return colours

    def clear_pixels(self):
        # print 'strip clear_pixels'
        for pixel in self.pixels:
            pixel.color = (0,0,0)

    def shift_pixel(self,col=(255,0,0),direction=1):
        self.pixels[self.p_it].color = col
        self.p_it = (self.p_it+1)%self.nPixels

    def set_colour(self,col=(255,0,0)):
        for pixel in self.pixels:
            pixel.color = col

    def draw_line(self, x0, x1, col):
        for x in xrange(x0,x1):
            self.pixels[x].color = col


class Panel:
    ''' Represents a strip of addressable leds with nPixels  '''
    def __init__(self, origin=(0,0,0), colShift=(1.0,0.0,0.0), rowShift=(0.0,-1.0,0.0), nPixelsWide=1, nPixelsHigh=1):
        
        self.origin = origin
        self.nPixels = nPixelsWide * nPixelsHigh
        self.height = nPixelsHigh
        self.width = nPixelsWide

        self.width_odd = (self.width)%2
        self.height_odd = (self.height)%2

        self.width_centre = self.width/2.0
        self.height_centre = self.width/2.0

        self.rowShift = rowShift
        self.row_it = 0
        self.hue = 1.
        self.val = 0.9
        self.colour = [int(i*255) for i in colorsys.hsv_to_rgb(self.hue, 1., self.val)]
        self.rows = []
        x = self.origin[0]
        y = self.origin[1]
        z = self.origin[2]
        # print 'xyz', x,y,z
        for strip in xrange(nPixelsHigh):
            self.rows.append( PixelStrip(origin=(x,y,z),colShift=colShift,nPixels=nPixelsWide) )
            x += self.rowShift[0]
            y += self.rowShift[1]
            z += self.rowShift[2]
            # print '--xyz', x,y,z
    
    def get_colours(self):
        colours = []
        for row in self.rows:
            colours.extend(row.get_colours())
        return colours

    def set_val(self, val=1.0):
        self.val = val
        self.colour = [int(i*255) for i in colorsys.hsv_to_rgb(self.hue, 1., self.val)]
        
    def shift_hue(self, step=0.1):
        self.hue = (self.hue+step) %1.0
        self.colour = [int(i*255) for i in colorsys.hsv_to_rgb(self.hue, 1., self.val)]
        
    def clear_pixels(self):
        # print 'panel clear_pixels'
        for row in self.rows:
            row.clear_pixels()

    def set_pixel(self,x,y):
        self.rows[y].pixels[x].set_colour(self.colour)

    def set_colour(self,col=(0,0,0)):
        self.colour = col
        for row in self.rows:
            row.set_colour(col=self.colour)

    def shift_pixel(self):
        for row in self.rows:
            row.shift_pixel(self.colour)

    def shift_row(self,direction=1):
        self.rows[self.row_it].set_colour(self.colour)
        self.row_it = (self.row_it+1)%self.height

    def vu_to_rows(self,freq_chs,hues):
        i = 0
        for row in self.rows:
            for p in xrange(freq_chs[i]):
                # colorsys.hsv_to_rgb(self.hue, 1., self.val)
                c = tuple([int(255*x) for x in colorsys.hsv_to_rgb(hues[i], 1., self.val)])   
                row.pixels[p].set_colour(c)
            i+=1
    
    def set_ring(self,level):
        ''' will set a ring expanding outward '''
        # print 'set_ring', level
        # start at centre
        # centre - level
        x1 = int(math.floor(self.width_centre) - level)
        x2 = int(math.ceil(self.width_centre) + level)
        y1 = int(math.floor(self.height_centre) - level)
        y2 = int(math.ceil(self.height_centre) + level)

        # print x1,x2,y1,y2
        # self.draw_rect_fill(x1,y1,x2,y2,col=self.colour)
        self.draw_rect(x1,y1,x2,y2,col=self.colour)

        pass

    def set_rect(self,level):
        ''' will set a ring expanding outward '''
        # print 'set_ring', level
        # start at centre
        # centre - level
        x1 = int(math.floor(self.width_centre) - level)
        x2 = int(math.ceil(self.width_centre) + level)
        y1 = int(math.floor(self.height_centre) - level)
        y2 = int(math.ceil(self.height_centre) + level)

        # print x1,x2,y1,y2
        self.draw_rect_fill(x1,y1,x2,y2,col=self.colour)

        pass

    def draw_rect_fill(self, x1,y1,x2,y2,col=(0,0,0)):

        for x in xrange(y1,y2):
            self.rows[x].draw_line(x1,x2,col)

    def draw_rect(self, x1,y1,x2,y2,col=(0,0,0)):
        print x1, y1, x2, y2
        self.rows[y1].draw_line(x1,x2,col)

        if y1 < y2:
            for i in xrange(y1+1,y2):
                self.rows[i].pixels[x1].set_colour(col)
                self.rows[i].pixels[x2-1].set_colour(col)

        self.rows[y2-1].draw_line(x1,x2,col)

    def draw_spiral_out(self,level):

        target_pixel = int(level * self.nPixels)
        # target_pixel = 12
        # print level, target_pixel
        # starting position
        x = int(math.floor(self.width_centre))
        y = int(math.floor(self.height_centre))     
        self.set_pixel(x,y)
        # itteration_map = [(1,0),(0,-1),(-1,0),(0,1)]
        itteration_map = [(1,0),(0,1),(-1,0),(0,-1)]
        count1 = 0
        step = 1
        it = 0
        target = target_pixel-1

        while(count1 < target):
            ''' for x '''
            for i in xrange(step):
                # print x,y
                x+=itteration_map[it][0]
                y+=itteration_map[it][1]
                # print '[X]',count1,':', x,y,it,itteration_map[it]
                self.set_pixel(x,y)
                count1+=1
                if(count1 >= target):
                    break
            if(count1 >= target):
                break
            it=(it+1)%4

            ''' for y '''
            for i in xrange(step):
                # print x,y
                x+=itteration_map[it][0]
                y+=itteration_map[it][1]
                # print '[Y]',count1,':', x,y,it, itteration_map[it]
                self.set_pixel(x,y)
                count1+=1
                if(count1 >= target):
                    break
            if(count1 >= target):
                break
            it=(it+1)%4

            step+=1



def printPixels(panel):

    for strips in panel.rows:
        for leds in strips.pixels:
            print leds.location



if __name__ == '__main__':

    ''' x panel '''
    xP = Panel(origin=(0.1,0,0.1), colShift=(1.0,0.0,0.0), rowShift=(0.0,-1.0,0.0), nPixelsWide=5, nPixelsHigh=5, hSpacing=1, vSpacing=1)
    zP = Panel(origin=(-0.1,0,-5.1), colShift=(0.0,0.0,1.0), rowShift=(0.0,-1.0,0.0), nPixelsWide=5, nPixelsHigh=5, hSpacing=1, vSpacing=1)
    yP = Panel(origin=(0.0,0.1,-5.0), colShift=(1.0,0.0,0.0), rowShift=(0.0,0.0,1.0), nPixelsWide=5, nPixelsHigh=5, hSpacing=1, vSpacing=1)
    printPixels(xP)
    printPixels(zP)
    printPixels(yP)


