# Databricks notebook source
# MAGIC %pip install git+https://github.com/GullyBurns/czLandscapingTk.git

# COMMAND ----------

# MAGIC %run /Users/gully.burns@chanzuckerberg.com/datasci_databricks_notebooks/global_variables

# COMMAND ----------

# default_exp curatedDataUtils
from nbdev import *

# COMMAND ----------

# MAGIC %md # Curated Dataframe Utilities
# MAGIC 
# MAGIC > Library to provide functions to compute statistics and summary information on a dataframe that has been curated by multiple people. This library provides tools for computing Krippendorf Alpha stats and computing merged dataframes across multiple curators. 

# COMMAND ----------

#export
import pandas as pd
import json
from urllib.parse import quote
from tqdm import tqdm
import requests
import nltk
from nltk.metrics import agreement
from nltk.metrics.agreement import AnnotationTask
from nltk.metrics import masi_distance, binary_distance

class CuratedDataUtils:
  """This class permits generation of curation statistics and merged, consensus dataframes
  
  Attributes:
    * df: The dataframe being processed
    * doc_id_column: column in df that denotes document IDs
    * category_column: column in df that denotes curated category
    * curator_column: column in df that denotes curator
    * docs: the document set being curated
    * curators: the curators performing the curation work
    * categories: the set of categories being used to annotate the documents 
    * doc_task: a low-level `nltk` task object
  """
  
  def __init__(self, df, doc_id_column, category_column, curator_column, distance_function=masi_distance):
    self.df = df
    self.doc_id_column = doc_id_column
    self.category_column = category_column
    self.curator_column = curator_column
    document_task_data = []
    curators = {}
    docs = {}
    categories = {}

    for i, row in df.iterrows():
      category_array = str(row[category_column]).split(',')
      item = str(row[doc_id_column])
      td_row = (row[curator_column], item, frozenset(category_array))
      document_task_data.append(td_row)
      if docs.get(item) is None:
        docs[item] = 1
      else:
        docs[item] = docs[item] + 1

      if curators.get(row[curator_column]) is None:
        curators[row[curator_column]] = 1
      else:
        curators[row[curator_column]] = curators[row[curator_column]] + 1
      for c in str(row[category_column]).split(','):
        if categories.get(c) is None:
          categories[c] = 1
        else:
          categories[c] = categories[c] + 1

    doc_task = AnnotationTask(distance = distance_function)
    doc_task.load_array(document_task_data)
    self.docs = docs
    self.curators = sorted(curators.keys())
    self.categories = categories
    self.task = doc_task
  
  def get_avg_doc_agr(self, item):
    temp_list = [] 
    sum = 0.0
    cnt = 0.0
    for i in range(len(self.curators)):
      for j in range(i):
        try:
          sum += self.task.agr(self.curators[i], self.curators[j], str(item))
          cnt += 1.0
        except StopIteration:
          # No need to do anything - we get this error if attempting to compute agreement 
          # between curators where one of them never entered a score. 
          print('', end = '')
    if cnt > 0.0:
      avg = sum/cnt
    else: 
      avg = 0.0;
    return avg

  def get_consensus(self, item):
    """ 
    """
    result = []
    best = 0.0 
    for i in range(len(self.curators)):
      for j in range(i):
        try:
          agr = self.task.agr(self.curators[i], self.curators[j], str(item))
          if agr == 1.0:
            l = [x for x in self.task.data if x['coder']==self.curators[i] and x['item']==item]
            return list(l[0]['labels'])[0]
        except StopIteration:
          # No need to do anything - we get this error if attempting to compute agreement 
          # between curators where one of them never entered a score. 
          print('', end = '')
    return None

  def get_consensus_per_doc(self):
    """
    Generates DataFrame with new columns for 'AVG_AGREEMENT' and 'CONSENSUS' for each document
    """
    cat_list = sorted(list({c:0 for cc in df[self.category_column] for c in str(cc).split(',')}.keys()))
    curators = self.df[self.curator_column].unique()

    unused_columns = [c for c in df.columns if c != self.doc_id_column]
    sdf = df.drop([c for c in df.columns if c != self.doc_id_column], axis=1).drop_duplicates()
    sdf = sdf.reset_index(drop=True)

    #cat_count_dict = {cc: {c: 0 for c in cat_list} for cc in df.ID_PAPER}
    #for row in df.itertuples():
    #  for t in row.CATEGORIES.split(','):
    #    cat_count_dict[row.ID_PAPER][t] = cat_count_dict.get(row.ID_PAPER).get(t) + 1
    #cat_counts = [[cat_count_dict[row.ID_PAPER][c] for c in cat_list ] for row in sdf.itertuples()]
    #sdf['CATEGORY_COUNTS'] = cat_counts

    sdf['AVG_AGREEMENT'] = [self.get_avg_doc_agr(str(sdf.iloc[i][self.doc_id_column])) for i in range(len(sdf))]
    sdf['CONSENSUS'] = [self.get_consensus(str(sdf.iloc[i][self.doc_id_column])) for i in range(len(sdf))]

    return sdf

  def get_cross_curator_comparison(self):
    """
    Generates table with 1 row per doc + extra columns for each curator
    """
    unused_columns = [c for c in self.df.columns if c != self.doc_id_column]
    sdf = df.drop(unused_columns, axis=1).drop_duplicates()
    sdf = sdf.reset_index(drop=True)
    for c in self.curators:
      sdf_temp = self.df.query(self.curator_column+'==\''+c+'\'')
      sdf_temp[c] = sdf_temp[self.category_column]
      sdf_temp = sdf_temp.reset_index(drop=True)
      sdf_temp = sdf_temp.drop(unused_columns, axis=1)
      sdf = sdf.join(sdf_temp.set_index(self.doc_id_column), 
                     lsuffix='_1', rsuffix='_2', on=self.doc_id_column, how='outer') 
    return sdf
  

# COMMAND ----------

show_doc(CuratedDataUtils.__init__)

# COMMAND ----------

show_doc(CuratedDataUtils.get_cross_curator_comparison)

# COMMAND ----------

show_doc(CuratedDataUtils.get_consensus_per_doc)
