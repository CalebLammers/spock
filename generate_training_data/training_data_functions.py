import rebound
import numpy as np
import pandas as pd
import dask.dataframe as dd
import sys
sys.path.append('../spock')
sys.path.append('../../spock')
from simsetup import init_sim_parameters, get_sim

def training_data(row, csvfolder, runfunc, args):
    try:
        sim = get_sim(row, csvfolder)
        init_sim_parameters(sim)
        ret, stable = runfunc(sim, args)
    except:
        print('{0} failed'.format(row['runstring']))
        return None

    r = ret[0] # all runfuncs return list of features for all adjacent trios (to not rerun for each). For training assume it's always 3 planets so list of 1 trio
    return pd.Series(r, index=list(r.keys())) # convert OrderedDict to pandas Series

def gen_training_data(outputfolder, csvfolder, runfunc, args):
    # assumes runfunc returns a pandas Series of features, and whether it was stable in short integration. See features fucntion in spock/feature_functions.py for example
    df = pd.read_csv(csvfolder+"/runstrings.csv", index_col = 0).head(100)
    ddf = dd.from_pandas(df, npartitions=48)
    testres = training_data(df.loc[0], csvfolder, runfunc, args) # Choose formatting based on selected runfunc return type
    
    metadf = pd.DataFrame([testres]) # make single row dataframe to autodetect meta
    res = ddf.apply(training_data, axis=1, meta=metadf, args=(csvfolder, runfunc, args)).compute(scheduler='processes')
    res.to_csv(outputfolder+'/trainingdata.csv')

