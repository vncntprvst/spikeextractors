import unittest
import numpy as np
import spikeextractors as se



class TestNpzSortingExtractors(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    def test_write_then_read(self):
        
        
        recording, sorting_gt = se.example_datasets.toy_example(num_channels=4, duration=10)
        print(sorting_gt)
        
        se.NpzSortingExtractor.write_sorting(sorting_gt, 'test_NpzSortingExtractors.npz')
        
        npz = np.load('test_NpzSortingExtractors.npz')
        units_ids = npz['unit_ids']
        self.assertEqual(list(units_ids), list(sorting_gt.get_unit_ids()))
        
        
        
        

if __name__ == '__main__':
    unittest.main()


        