# Databricks notebook source
# default_exp queryTranslator
from nbdev import *

# COMMAND ----------

# MAGIC %md # Query Translation Tools  
# MAGIC 
# MAGIC > A library permits translation of complex boolean AND/OR queries between online APIs. 

# COMMAND ----------

#export
# USE PYEDA TO PROCESS AND REPURPOSE QUERIES AS LOGICAL EXPRESSIONS FOR SEARCHING.
import re
import pprint
from pyeda.inter import *
from pyeda.boolalg.expr import Literal,AndOp,OrOp
from enum import Enum
import unicodedata
from tqdm import tqdm

class QueryType(Enum):
  """
  An enumeration that permits conversion of complex boolean queries to different formats
  """
  open = 1
  closed = 2
  solr = 3
  epmc = 4
  epmc_sections = 5
  pubmed = 6
  andPlusOrPipe = 7
  pubmed_no_types = 8
  snowflake = 9

class QueryTranslator(): 
  def __init__(self, df, id_col, query_col):
    """This class allows a user to define a set of logical boolean queries in a Pandas dataframe and then convert them to a variety of formats for use on various online API systems.<BR>
    Functionality includes:
      * Specify queries as a table using '|' and '&' symbols
      * generate search strings to be used in API calls for PMID, SOLR, and European PMC

    Attributes:
      * df: The dataframe of queries to be processed (note: this dataframe must have a numerical ID column specified)
      * query_col: the column in the data frame where the query is specified
    """
    pp = pprint.PrettyPrinter(indent=4)
    def fix_errors(expr_string):
      q = re.sub('\s+(AND)\s+',' & ',expr_string)
      q = re.sub('\s+(OR)\s+',' | ',q)
      q = re.sub('\s+(NOT)\s+',' ~',q)
      q = re.sub('[\n]','',q)
      q = re.sub('\"','QQQ',q)
      q = re.sub('\[(ti|ab|ft|tiab|mesh|dp)\]',r'_\g<1>', q).strip()
      return q

    self.id2terms = {}
    self.terms2id = {}
    for tt in df[query_col]:
      redq = fix_errors(str(tt).strip())
      for t in re.split('[\&\|\(\)]', redq):
        t = re.sub('[\(\)]','', t).strip()
        #t = re.sub('\[(ti|ab|ft|tiab)\]',r'\g<1>', t).strip()
        if len(t)==0:
          continue
        if self.terms2id.get(t) is None:
          id = 't'+str(len(self.terms2id))
          self.id2terms[id] = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('ascii') # convert to ascii for searches via API 
          self.terms2id[t] = id

    ordered_names = sorted(self.terms2id.keys(), key=len, reverse=True)
    self.redq_list = []
    for row in tqdm(df.iterrows(),total=len(df)):
      tt = row[1][query_col]
      row_id = row[1][id_col]
      redq = fix_errors(str(tt).strip())
      for t in ordered_names:
        id = self.terms2id[t]
        if '"' in t:
          redq = re.sub(t, id, redq)
        else:
          redq = re.sub('\\b'+t+'\\b', id, redq)        
      self.redq_list.append((row_id, redq))

  def generate_queries(self, query_type:QueryType, skipErrors=True, **kwargs):
    """
    Use this command to covert the queries to the different forms specified by the QueryType enumeration
    """
    queries = []
    IDs = []
    for ID, t in tqdm(self.redq_list):
      try:
        if t:
          ex = expr(t)
          queries.append(self._expand_expr(ex, query_type, **kwargs))
        else: 
          queries.append('')
        IDs.append(ID)
      except:
        print('Error with '+str(ID)+': '+t)
        queries.append('')
        IDs.append(ID)
        if skipErrors is False:
          raise
    return (IDs, queries)
    
  def _expand_expr(self, ex, query_type:QueryType, **kwargs):
    if query_type == QueryType.open:
      return self._simple(ex)
    elif query_type == QueryType.closed:
      return self._closed_quote(ex)
    elif query_type == QueryType.solr:
      return self._solr(ex)
    elif query_type == QueryType.epmc:
      return self._epmc(ex)
    elif query_type == QueryType.epmc_sections:
      return self._epmc_sections(ex, sections=kwargs.get('sections',[]))
    elif query_type == QueryType.pubmed:
      return self._pubmed(ex)
    elif query_type == QueryType.andPlusOrPipe:
      return self._plusPipe(ex)
    elif query_type == QueryType.pubmed_no_types:
      return self._pubmed_no_types(ex)
    elif query_type == QueryType.snowflake:
      return self._snowflake(ex)

  # expand the query as is with AND/OR linkagage, no extension. 
  # drop search fields
  def _simple(self, ex):
    if isinstance(ex, Literal):
      term = re.sub('_(ti|ab|ft|tiab)', '', self.id2terms[ex.name])
      term = re.sub('QQQ', '"', term)
      return term
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._simple(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._simple(x) for x in ex.xs])+')'

  def _closed_quote(self, ex):
    if isinstance(ex, Literal):
      term = re.sub('_(ti|ab|ft|tiab)', '', self.id2terms[ex.name])
      term = re.sub('QQQ', '', term)
      return '"'+term+'"'
    elif isinstance(ex, AndOp):
      return '('+' NOT '.join([self._closed_quote(x) for x in ex.xs])+')'
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._closed_quote(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._closed_quote(x) for x in ex.xs])+')'
  
  def _solr(self, ex):
    if isinstance(ex, Literal):
      p = re.compile('^(.*)_(ti|ab|ft|tiab)')
      m = p.match( self.id2terms[ex.name] )
      if m:
        t = m.group(1)
        t = re.sub('QQQ', '"', t)
        f = m.group(2)
        if f == 'ti':
          return '(paper_title:"%s")'%(t)
        elif f == 'ab':
          return '(paper_abstract:"%s")'%(t)
        elif f == 'tiab':
          return '(paper_title:"%s" OR paper_abstract:"%s")'%(t,t)
        elif f == 'ft':
          return '(paper_title:"%s" OR paper_abstract:"%s")'%(t,t)
        else :
          raise Exception("Incorrect field specification, must be 'ti', 'ab', 'tiab', or 'ft': " + self.id2terms[ex.name] )
      else:              
        t = self.id2terms[ex.name]
        t = re.sub('QQQ', '"', t)
        return '(paper_title:"%s" OR paper_abstract:"%s")'%(t,t)
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._solr(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._solr(x) for x in ex.xs])+')'

  def _epmc(self, ex):
    if isinstance(ex, Literal):
      p = re.compile('^(.*)_(ti|ab|ft|tiab)')
      m = p.match( self.id2terms[ex.name] )
      if m:
        t = m.group(1)
        t = re.sub('QQQ', '"', t)
        f = m.group(2)
        if f == 'ti':
          return '(TITLE:"%s")'%(t)
        elif f == 'ab':
          return '(ABSTRACT:"%s")'%(t)
        elif f == 'tiab':
          return '(TITLE:"%s" OR ABSTRACT:"%s")'%(t,t)
        elif f == 'ft':
          return '"%s"'%(t)
        else:
          raise Exception("Incorrect field specification, must be 'ti', 'ab', 'tiab', or 'ft': " + self.id2terms[ex.name] )
      else:              
        t = self.id2terms[ex.name]
        t = re.sub('QQQ', '"', t)
        return '(paper_title:"%s" OR ABSTRACT:"%s")'%(t,t)
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._epmc(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._epmc(x) for x in ex.xs])+')'

  def _epmc_sections(self, ex, sections):
    if isinstance(ex, Literal):
      t = self.id2terms[ex.name]
      t = re.sub('QQQ', '', t)
      query = '('+' OR '.join(['%s:"%s"'%(s,t) for s in sections])+')'
      return query
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._epmc_sections(x, sections) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._epmc_sections(x, sections) for x in ex.xs])+')'
    
  def _pubmed(self, ex):
    if isinstance(ex, Literal):
      p = re.compile('^(.*)_(ti|ab|ft|tiab|mesh|dp)$')
      m = p.match( self.id2terms[ex.name] )
      #print(m)
      if m:
        t = m.group(1)
        f = m.group(2)
        t = re.sub('QQQ', '"', t)
        if f == 'ti':
          return '%s[ti]'%(t)
        elif f == 'ab':
          return '%s[ab]'%(t)
        elif f == 'tiab':
          return '%s[tiab]'%(t)
        elif f == 'mesh':
          return '%s[mesh]'%(t)
        elif f == 'dp':
          return '%s[dp]'%(t)
        elif f == 'ft':
          raise Exception("Can't run full text query on pubmed currently: " + self.id2terms[ex.name] )
        else:
          raise Exception("Incorrect field specification, must be 'ti', 'ab', 'tiab', or 'ft': " + self.id2terms[ex.name] )
      else:              
        t = self.id2terms[ex.name]
        t = re.sub('QQQ', '"', t)
        return '%s'%(t)
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._pubmed(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._pubmed(x) for x in ex.xs])+')'
    
  def _plusPipe(self, ex):
    if isinstance(ex, Literal):
      t = re.sub('QQQ', '', self.id2terms[ex.name])
      return '"%s"'%(t) 
    elif isinstance(ex, AndOp):
      return '('+'+'.join([self._pubmed(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+'|'.join([self._pubmed(x) for x in ex.xs])+')'
    
  def _snowflake(self, ex):
    if isinstance(ex, Literal):
      t = self.id2terms[ex.name]
      t = re.sub('QQQ', '', t)
      t = re.sub("'", "''", t)
      t = re.sub('"', '', t)
      s = "(lower(p.TITLE) LIKE '*%s*' OR lower(p.ABSTRACT) LIKE '*%s*')"%(t.lower(),t.lower())
      s = re.sub('\*', '%', s)
      return s
    elif isinstance(ex, AndOp):
      return '('+' AND '.join([self._snowflake(x) for x in ex.xs])+')'
    elif isinstance(ex, OrOp):
      return '('+' OR '.join([self._snowflake(x) for x in ex.xs])+')'

# COMMAND ----------

show_doc(QueryTranslator.__init__)

# COMMAND ----------

show_doc(QueryTranslator.generate_queries)
