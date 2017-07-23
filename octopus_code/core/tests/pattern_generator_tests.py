import unittest
import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import time

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

# Standard library imports...
from mock import patch, MagicMock

Testopus = "./core/tests/test_octopus.json" 

class TestPatternGeneratorMethods(unittest.TestCase):

    # Mock OPC connectionc
    def setUp(self):
        patcher = patch('core.octopus.opc.Client')
        opc_mock = patcher.start()
        opc_mock.can_connect = MagicMock(return_value=True)
        opc_mock.put_pixels = MagicMock()

        self.pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus), enable_status_monitor=False)

        print "\n", "Testing:", self._testMethodName

    def test_contains_default_pattern(self):
        self.assertTrue(len(self.pattern_generator.patterns) > 0)

    def test_timeout(self, timeout=0.1):
        start_time = time.time()
        self.pattern_generator.run(timeout=timeout)
        self.assertTrue(time.time() - start_time + timeout*0.01 > timeout)

    def test_continues_on_pattern_exception(self):
        self.pattern_generator.patterns = [RpcTestPattern]
        with patch('core.octopus.patterns.rpcTestPattern.RpcTestPattern.next_frame') as mock:
            mock.side_effect = Exception("PURPOSELY BROKEN TEST PATTERN")

            self.pattern_generator.run(timeout=0.1)



if __name__ == '__main__':
    unittest.main()