
import sys
import time
from multiprocessing import Queue

from core.audioAnalysis.fft import Fft
from core.cube.layout.panel import Panel

from core.master.device import Device
# import core.master.animation as animation
import core.cube.animations.cube_animations as animation
import core.opc.opc as opc



''' TODO NOTES:
 - could audio / fft data be a udp multicast instead of a queue?
 - current animation control is in device but it should be in an 
   animation class.
'''

def map_range(value, OldMin, OldMax, NewMin,NewMax):
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((value - OldMin) * NewRange) / OldRange) + NewMin
    return max(min(255,NewValue),0)

class Cube(Device):

    def __init__(self, origin=(0.0,0.0,0.0),width=5,height=5,gap=0.1,step=0.3, frame_period=1000):
        Device.__init__(self,frame_period=frame_period)

        xP = Panel(origin=(origin[0]+(width-1)*step, origin[1]-gap, origin[2]), colShift=(-step,0.0,0.0), rowShift=(0.0,0.0,-step), nPixelsWide=width, nPixelsHigh=height)
        yP = Panel(origin=(origin[0]+-gap, origin[1], origin[2]-(width-1)*step), colShift=(0.0,0.0,step), rowShift=(0.0,step,0.0), nPixelsWide=width, nPixelsHigh=height)
        zP = Panel(origin=(origin[0]+0.0, origin[1]+(width-1)*step, origin[2]+gap), colShift=(0.0,-step,0.0), rowShift=(step,0.0,0.0), nPixelsWide=width, nPixelsHigh=height)
        
        self.Panels = [xP,yP,zP]

        self.pixels = []
        self.colors = []
        self.val = 0.2

        

        for panel in self.Panels:
            for strip in panel.rows:
                for pixel in strip.pixels:
                    self.pixels.append(pixel.location)
                    self.colors.append(pixel.color)

        self.nPixels = len(self.pixels)

        self.d_animations = {}
        self.d_animations['Vu'] = animation.Vu_to_rows(self.Panels)
        self.d_animations['Shift'] = animation.Shift(self.Panels)
        self.d_animations['Ring'] = animation.Vu_to_ring(self.Panels)
        self.d_animations['Spiral'] = animation.Vu_to_spiral_out(self.Panels)
        
        

        self.current_animation = self.d_animations['Vu']

        # self.current_animation = animation.Vu_to_rows(self.Panels)
        # return self.pixels

    def get_pixels(self):
        return self.pixels


    def get_colours(self):
    	colours = []
        for panel in self.Panels:
            colours.extend(panel.get_colours())
        return colours


 


if __name__ == '__main__':
    ''' to run
    - ensure an opc server is running 
        $ bin/gl_server -l layouts/cubeLayout.json 127.0.0.1:7890

    - then 
        $ cube.py -f DaftPunk.wav 
        or
        $ python -m core.cube.cube -f resources/DaftPunk.wav 

    '''

    #-------------------------------------------------------------------------------
    # handle command line

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip_host", type=str, help="ip:port defauls to 127.0.0.1:7890.")
    parser.add_argument("-f", "--file", type=str, help="file path and name of wav file.")
    parser.add_argument("-d", "--debug", type=str, help="set true to print to terminal.")
    parser.add_argument("-s", "--datasize", type=int, help="data size/window, default 2048.")
    parser.add_argument("-m", "--mic", type=str, help="set true to print to use microphone input.")
    args = parser.parse_args()

    if args.ip_host != None: IP_PORT = args.ip_host
    else: IP_PORT = '127.0.0.1:7890'

    if args.datasize != None: data_size = args.datasize
    else: data_size = 2048

    if args.file != None: fname = args.file
    else: fname = "../sounds/test.wav"
    frate = 44100.0

    if args.debug != None: debug = True
    else: debug = False

    if args.mic != None:
        mic=True
    else: mic = None


    ''' cube config '''
    audio_queue = Queue()
    cube = Cube(origin=(0,0,0), frame_period=100)
    cube.daemon = True
    control_queue = cube.control_queue
    pixel_queue = cube.pixel_queue
    cube.start()

    ''' FFT config '''
    mic = False
    fft = Fft(datasize=data_size,mic=mic,debug=debug,fname=fname,frate=44100.0, output=True, dataqueue=cube.audio_queue)
    fft.daemon = True
    fft.start()


    time.sleep(1)

    client = opc.Client(IP_PORT)
    if client.can_connect():
        print('    connected to %s' % IP_PORT)
    else:
        # can't connect, but keep running in case the server appears later
        print('    WARNING: could not connect to %s' % IP_PORT)
    print('')





    while True:

        control_queue.put('get_colours')
        while pixel_queue.empty():
            time.sleep(.10)
        client.put_pixels( pixel_queue.get(), channel=0)
        
