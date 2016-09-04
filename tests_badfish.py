import unittest
import pandas as pd
import numpy as np
import math
import badfish as bf
 
class BadFish(unittest.TestCase):
 
    def setUp(self):
        self.basic_df = pd.util.testing.makeMissingDataframe(random_state=3)

        self.enc_df = self.basic_df.copy()
        self.enc_df.iloc[0,0] = "MISSING" #Adding Missing to column A
        self.enc_df.iloc[0,1] = "MISSING" #Adding Missing to column B
        self.enc_df.iloc[0,2] = -1 #Adding Missing to column C
        self.enc_df.iloc[0,3] = "N/A" #Adding Missing to column D
        self.enc_df.iloc[1,3] = "N/A" #Adding Missing to column D


    
    def test_basic_counts(self):
        mf = bf.MissFrame(self.basic_df)
        counts = mf.counts()
        self.assertEqual(0, counts['D']) 
        self.assertEqual(5, counts['C']) 
        self.assertEqual(5, counts['B']) 
        self.assertEqual(2, counts['A']) 

    def test_missing_codes_init(self):
        mf = bf.MissFrame(self.enc_df, missing_codes = ["N/A", "MISSING", -1])
        counts = mf.counts()
        self.assertEqual(2, counts['D']) 
        self.assertEqual(6, counts['C']) 
        self.assertEqual(6, counts['B']) 
        self.assertEqual(3, counts['A']) 

if __name__ == '__main__':
    unittest.main()
