# Databricks notebook source
# default_exp bioLinkUtils
from nbdev import *

# COMMAND ----------

# MAGIC %md # BioLink Query Tools 
# MAGIC 
# MAGIC > Tools to query and analyze data from the Monarch Initiative's BioLink interface. This provides a live queryable interface for disease-based knowledge derived from Monarch's KG. Access to the service is through https://api.monarchinitiative.org/api/. More detailed information about the Biolink model is available from their [GitHub page](https://github.com/biolink/biolink-model). 

# COMMAND ----------

#export

import json
import requests
import pandas as pd
from tqdm import tqdm

class BioLinkUtils: 
  descendents_lookup = {}
  '''
  Interactions with the BioLink KG developed by the Monarch initiaive. 
  Currently, this system can query for MONDO disease Ids and compute similar diseases based on phenotype overlap. 
  '''
  def __init__(self, descendents_df = None):
    if descendents_df is not None:
      self.descendents_lookup = {}
      for row in descendents_df.itertuples():
        d = row.descendent_id[-13:].replace('_', ':')
        m = row.mondo_id[-13:].replace('_', ':')
        if self.descendents_lookup.get(m) is None:
          self.descendents_lookup[m] = [d]
        else:
          self.descendents_lookup.get(m).append(d)
    
  def query_diseases(self, disease_ids):
    BIOLINK_STEM = "https://api.monarchinitiative.org/api/bioentity/"
    recs = []
    for id in disease_ids:
      url = BIOLINK_STEM + 'disease/'+id 
      print(url)
      r = requests.get(url)
      d = r.content.decode('utf-8')
      recs.append(json.loads(d))
    return recs

  def compute_disease_similarity_across_disease_list(self, disease_ids, disease_names, metric='phenodigm', taxon=9606, limit=50, threshold=0.7):
    '''
    Iterates over a set of MONDO URIs to identify similar diseases based on phenotypic overlap.  
    '''
    df = pd.DataFrame()
    for (d_id, d_name) in zip(disease_ids, disease_names):
      m = re.match("^(MONDO\:\d{7})", d_id)
      if m is not None:
        df = df.append(self.compute_disease_similarity(m.group(1), d_name, metric=metric, taxon=taxon, limit=limit, threshold=threshold))
      else:
        print(d_id)
    return df  
  
  def compute_disease_similarity(self, disease_id, disease_name, metric='phenodigm', taxon=9606, limit=50, threshold=0.7):
    '''
    Computes similar diesases (with scores) for a single MONDO URI based on a phenotypic overlap metric (e.g., phenodigm). 
    Analysis is performed remotely. 
    Currently not ideal - needs to be able to remove 'descendents' from the list of returned similar diseases.  
    '''
    BIOLINK_STEM = "https://api.monarchinitiative.org/api/sim/search?is_feature_set=false&"
    url = BIOLINK_STEM + 'metric='+metric+'&id='+disease_id+'&limit=100&taxon='+str(taxon)
    r = requests.get(url)
    d = r.content.decode('utf-8')
    sim_data = json.loads(d)
    l = []
    print(disease_name + ': ' + str(len(sim_data.get('matches'))))
    for match in sim_data.get('matches'):
      t_id = match.get('id')
      #if self.descendents_lookup.get(disease_id) is not None and t_id in self.descendents_lookup.get(disease_id):
      #  continue
      if t_id != disease_id and \
          match.get('score') > threshold and \
          len(l)<limit:
        pl = [(pm.get('reference').get('IC'), pm.get('reference').get('id'), pm.get('reference').get('label')) for pm in match.get('pairwise_match')]
        l.append((disease_id, disease_name, match.get('type'), match.get('rank'), match.get('score'), match.get('label'), match.get('id'), pl))
    df = pd.DataFrame(l, columns=['source_disease_id','source_disease_name','type','rank','score','label','target_id', 'match'])
    return df
