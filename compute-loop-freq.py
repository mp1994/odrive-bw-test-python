#!/usr/bin/env python3

import numpy as np
import pandas as pd
import os

csv_files = list(filter(lambda f: f.endswith('.csv'), os.listdir(".") ))

for f in csv_files:
    df = pd.read_csv(f, header=0, comment='/')
    t = df['time'].to_numpy()

    f = np.diff(t)
    dt = f.mean()
    fa = 1/dt

    print("Average dt = {:.6f} s | Average frequency: {:4.4f} Hz".format(dt, fa))