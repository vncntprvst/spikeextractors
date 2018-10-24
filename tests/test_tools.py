import numpy as np
import os, sys
import unittest
import tempfile, shutil
import spikeinterface as si

class TestTools(unittest.TestCase):
    def setUp(self):
        M=32
        N=10000
        samplerate=30000
        X=np.random.normal(0,1,(M,N))
        self._X=X
        self._samplerate=samplerate
        self.RX=si.NumpyRecordingExtractor(timeseries=X,samplerate=samplerate)
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_save_probes(self):
        si.loadProbeFile(self.RX, 'tests/probe_test.prb')
        assert 'location' in self.RX.getChannelPropertyNames()
        assert 'group' in self.RX.getChannelPropertyNames()
        positions = [self.RX.getChannelProperty(chan, 'location') for chan in range(self.RX.getNumChannels())]
        # save in csv
        si.saveProbeFile(self.RX, self.test_dir+'geom.csv')
        # load csv locations
        si.loadProbeFile(self.RX, self.test_dir+'geom.csv')
        position_loaded = [self.RX.getChannelProperty(chan, 'location') for chan in range(self.RX.getNumChannels())]
        self.assertTrue(np.allclose(positions[10], position_loaded[10]))

    def test_write_dat_file(self):
        si.writeBinaryDatFormat(self.RX, self.test_dir+'rec.dat')
        # load
        data = np.memmap(open(self.test_dir+'rec.dat'), dtype='float32', mode='r', shape=(self.RX.getNumFrames(),
                                                                                          self.RX.getNumChannels())).T
        assert np.allclose(data, self.RX.getTraces())
        si.writeBinaryDatFormat(self.RX, self.test_dir + 'rec.dat', transpose=True)
        # load
        data = np.memmap(open(self.test_dir + 'rec.dat'), dtype='float32', mode='r', shape=(self.RX.getNumChannels(),
                                                                                            self.RX.getNumFrames()))
        assert np.allclose(data, self.RX.getTraces())


if __name__ == '__main__':
    unittest.main()