import isodate
from datetime import timedelta
import numpy as np
import pandas as pd
from lib.models import *

def write_table_to_file(reviews, filename):
    df = pd.DataFrame(reviews)
    df = df[(df["reviewer"] != "coveralls")]
    df['duration_hours'] = df['duration'].apply(isodate.parse_duration).apply(lambda d: round(d / timedelta(hours=1), 2))
    del df['duration']
    table = df.pivot_table(values=['duration_hours'], index=['reviewer'], aggfunc=[p50, p90])
    table = table.sort_values(('p50','duration_hours'), ascending=False)
    f = open(filename, "w")
    f.write(table.to_markdown())
    f.close()

def p50(g):
    return np.percentile(g, 50)

def p90(g):
    return np.percentile(g, 90)
