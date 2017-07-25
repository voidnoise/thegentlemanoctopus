import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import os
import sys

import psutil
import time
import csv
import argparse
import threading

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

import core.tests.integrationTestData as integrationTestData
from core.tests.integrationTestData import IntegrationTestData

# matplotlib may not work on the odroid
try:
    import matplotlib.pyplot as plt
    import core.tests.utils as utils
    plotting = True

except Exception as e:
    plotting = False

Testopus = "./core/tests/test_octopus.json" 
Test_File = "./core/tests/test_data.csv"

class IntegrationTest:
    def __init__(self, 
        framerate=20, 
        patterns = None,
        host="127.0.0.1",
        port=7890
    ):

        self.pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus), 
            framerate=framerate,
            enable_status_monitor=False,
            patterns = patterns,
            opc_host=host, 
            opc_port=port,
        )

        # Start the cpu meter
        self.cpu_percent = 0
        self.lock = threading.Lock()
        thread = threading.Thread(target=self.cpu_fun)
        thread.daemon = True
        thread.start()

    def run(self, run_time=10):        
        run_start = time.time()
        process = psutil.Process(os.getpid())
        test_file = open(Test_File, "w")

        test_succesful = True

        # Run the Pattern for a bit and log data
        try: 
            while time.time() - run_start < run_time:
                status_string = (
                    "Testing ", self.pattern_generator.current_pattern.__class__.__name__, ": ", 
                    int(time.time() - run_start), "s",
                    " of ", 
                    str(run_time), "s"
                )
                status_string = "".join([str(x) for x in status_string])
                print '\r', status_string,
                sys.stdout.flush()

                #Update the pattern generator
                loop_start = time.time()


                self.pattern_generator.update()

                rate = 1/(time.time() - loop_start)
                t = loop_start - run_start
                mem = process.memory_percent()
                cpu = self.get_cpu()

                status = self.pattern_generator.current_pattern.status()

                IntegrationTestData(t, rate, cpu, mem, status).save(test_file)

            print "\n"


        except Exception as err:
            test_succesful = False 
            raise err

        finally:
            test_file.close()

            if test_succesful:
                print "Test completed.."
            else:
                print "TEST FAILED"

    # TODO: Methods to stop cpu meter
    def cpu_fun(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=0.3)

            with self.lock:
                self.cpu_percent = cpu_percent

    def get_cpu(self):
        with self.lock:
            cpu_percent = self.cpu_percent

        return cpu_percent

def print_results(filename):
    results = integrationTestData.load_csv(filename)

    t = [result.t for result in results]
    framerate = [result.framerate for result in results]
    mem = [result.mem for result in results]
    cpu = [result.cpu for result in results]

    print "Min Framerate", np.min(framerate)
    print "Max mem", np.max(mem)
    print "Max CPU", np.max(cpu)

# TODO: Put this in utils?
def plot_dashes(x_locations):
    for x in x_locations:
        plt.axvline(x, color='k', linestyle='dashed', linewidth=1)

def plot_results(filename):
    results = integrationTestData.load_csv(filename)

    t = [result.t for result in results]
    framerate = [result.framerate for result in results]
    mem = [result.mem for result in results]
    cpu = [result.cpu for result in results]
    names = [result.pattern_name for result in results]

    dashes=[]
    for i, name in enumerate(names[:-1]):
        if name != names[i-1]:
            dashes.append(t[i])

    unique_names = np.unique(names).tolist()

    num_plots = 4
    plt.subplot(num_plots, 1, 1)
    plot_dashes(dashes)
    plt.plot(t, framerate)
    plt.title('Framerate')
    plt.xlabel('Time (s)')
    plt.ylabel('Framerate')


    plt.subplot(num_plots, 1, 2)
    plot_dashes(dashes)
    plt.plot(t, mem)
    plt.title('Memory Usage')
    plt.xlabel('Time (s)')
    plt.ylabel('Memory (Mb)')

    plt.subplot(num_plots, 1, 3)
    plot_dashes(dashes)
    plt.plot(t, cpu)
    plt.title('CPU Usage')
    plt.xlabel('Time (s)')
    plt.ylabel('CPU %')
    plt.ylim([0, 100])

    plt.subplot(num_plots, 1, 4)
    
    
    pos = [unique_names.index(name) for name in names]
    plot_dashes(dashes)
    plt.scatter(t, pos, c=pos, s=100)
    plt.title('Selected Pattern')
    plt.xlabel('Time (s)')
    plt.ylabel('Pattern')
    plt.gca().yaxis.grid(True)
    plt.yticks(range(len(unique_names)), unique_names)

    print_results(filename)

    plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Test the octopus!"
    )

    #TODO: Print Results
    parser.add_argument('mode', choices=['test', 'plot', 'print'], help=
        'test: Test the octopus\n'
        'plot: plot test data csv\n'
        'print: print test metrics'
    )

    parser.add_argument('-t', type=int, help="Time to test for in seconds", default=5)

    parser.add_argument('-i', help="Time to test for in seconds", default="127.0.0.1")
    parser.add_argument('-p', type=int, help="Time to test for in seconds", default=7890)

    
    args = parser.parse_args()

    if args.mode == "test":
        integration_test = IntegrationTest(patterns=[ShambalaPattern()], host=args.i, port=args.p)
        integration_test.run(run_time=args.t)

    elif args.mode == "plot":
        if not plotting:
            print "Cannot import Matplotlib on this device"
        plot_results(Test_File)

    elif args.mode =="print":
        print_results(Test_File)

    else:
        print parser.print_help()


