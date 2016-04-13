import threading
import queue
import re
import multiprocessing as mp
import numpy as np
import pandas as pd
import arrow
from sqlalchemy import create_engine
import tushare as ts
import nath
from ts_util import *

def run(consectives=3,min_raise=0.05):
    for i in range(600000,604000):
        sec_num=
    df=ts.get_hist_data()



