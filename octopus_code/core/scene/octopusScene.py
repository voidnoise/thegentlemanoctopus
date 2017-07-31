#!/usr/bin/env python

from core.audioAnalysis.AudioProcessing import AudioProcessing
from core.fish.fish import Fish
from core.scene.controlInterface import ControlInterface
from core.octopus.gentlemanOctopus import GentlemanOctopus
import core.octopus.layouts.octopusLayout as octopusLayout
import core.octopus.patterns.patternList as patternList

''' standard imports '''
import numpy as np
import Queue
import argparse
import time
import sys
import ConfigParser



class OctopusScene():
    '''
    * GentlemanOctopus
    * EL-Ting
    * Control Input (RPC Server)
    * Audio processing (UDP Server)
    '''
    
    def __init__(self, cfg, layout, controlQueue):
        ''' config - dictionary '''
        self.conf = cfg

        self.process_config()

        self.layout_f = layout

        ''' init control queues '''
        self.ifQueue = controlQueue
        self.fish_ctrl = Queue.Queue(100)
        self.octopus_ctrl = Queue.Queue(100)
        self.audio_ctrl = Queue.Queue(100)

        ''' init queues '''
        self.ELQueue = Queue.Queue(100)
        self.fft_queues = [Queue.Queue(100),Queue.Queue(100)]

        ''' init devices '''
        self.init_audio_processing(self.conf_audio, self.fft_queues, self.audio_ctrl)
        print 'f1sh'
        self.init_fish(self.conf_fish,self.fish_ctrl,self.fft_queues[0])
        print 'octopus'
        self.init_octopus(self.octopus_ctrl,self.fft_queues[1])
        
        # init control interface
        # run main loop in ControlInterface.py


        pass


    def main_loop(self,  run_time=10):
        ''' pole rpc queue for new commands and distrubute to scene 
        devices as needed '''
        run_start = time.time()
        while time.time() - run_start < run_time:
            status_string = (
                "Testing ", self.gentleman_octopus.current_pattern.__class__.__name__, ": ", 
                int(time.time() - run_start), "s",
                " of ", 
                str(run_time), "s"
            )
            status_string = "".join([str(x) for x in status_string])
            print '\r', status_string,
            sys.stdout.flush()
                
            loop_start = time.time()
            self.gentleman_octopus.update()
            rate = 1/(time.time() - loop_start)
            t = loop_start - run_start
        pass

    def process_config(self):

        ''' declare specific dictionaries '''
        self.conf_routing = self.conf['Routing']
        self.conf_fish = self.conf['Fish']
        self.conf_control = self.conf['Control']
        self.conf_audio = self.conf['Audio']   
        self.conf_pattern_gen = self.conf['PatternGenerator'] 
        self.conf_patterns = self.conf['Patterns']
        
    def print_config(self, conf):
        ''' 
        method to print the configuration file parameters
        '''
        print '\nConfiguration file loaded....\n'
        ''' sections '''
        for section in conf:
            print '\n____[', section, ']____'
            for item in conf[section]:
                print item, ':', conf[section][item]

    def init_audio_processing(self, conf, fft_q, ctrl_q):
        print 'Audio'
        self.audio = AudioProcessing(
            conf,
            fft_q, 
            ctrl_q
            )
        self.audio.start()
        pass


    def init_fish(self, conf, fft_q, ctrl_q):
        self.fish = Fish(
            conf, 
            control_queue=ctrl_q, 
            audio_stream_queue=fft_q
            )
        self.fish.start()


    def init_octopus(self, fft_q, ctrl_q):
        octopus_layout = octopusLayout.Import(self.layout_f)
        self.gentleman_octopus = GentlemanOctopus(
            octopus_layout, 
            control_queue=ctrl_q,
            audio_stream_queue=fft_q,
            opc_host=self.conf_routing['OPC_ip'], 
            opc_port=self.conf_routing['OPC_port'],
            patterns=patternList.patterns
        )
        self.gentleman_octopus.start()


    def init_control(self, fft_q, ctrl_q):
        print 'init control not implimented'


# Example
if __name__ == '__main__':

    
    scene = OctopusScene()





    