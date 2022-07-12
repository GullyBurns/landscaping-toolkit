# Databricks notebook source
#hide
from nbdev import *
#from your_lib.core import *

# COMMAND ----------

# MAGIC %md # czLandscapingTk (Chan Zuckerberg Landscaping Toolkit)
# MAGIC 
# MAGIC > This library is a public-facing implementation of a library of components designed to support and facilitate 'scientific knowledge landscaping' within the Chan Zuckerberg Initiative's Science Program. It consists of several utility libraries and some scripts to demonstrate how to use them. 

# COMMAND ----------

# MAGIC %md ## Install

# COMMAND ----------

# MAGIC %md `pip install git+https://github.com/GullyBurns/czLandscapingTk.git`

# COMMAND ----------

# MAGIC %md ## How to use

# COMMAND ----------

# MAGIC %md 
# MAGIC 
# MAGIC # NetworkxS2AG Class
# MAGIC 
# MAGIC # NetworkxS2AG Class
# MAGIC 
# MAGIC # NetworkxS2AG Class
# MAGIC Instantiate the class using an api key you should obtain from the S2AG team to permit more than 100 request calls per 5 minutes. This script will burn through that limit immediately. Obtain API keys here: https://www.semanticscholar.org/product/api#Partner-Form
# MAGIC 
# MAGIC ```
# MAGIC kolsGraph = NetworkxS2AG('<API-KEY-FROM-S2AG-TEAM>')
# MAGIC ```
# MAGIC 
# MAGIC Maybe start by searching for a reseracher by name. e.g. [Daphne Koller](https://api.semanticscholar.org/graph/v1/author/search?query=Daphne+Koller) 
# MAGIC 
# MAGIC ```
# MAGIC kolsGraph.search_for_disambiguated_author('Daphne Koller')
# MAGIC ```
# MAGIC 
# MAGIC Generating the following output: 
# MAGIC <table border="1" class="dataframe">  <thead>    <tr style="text-align: right;"><th></th>      <th>authorId</th>      <th>name</th>      <th>paperCount</th>      <th>hIndex</th>      <th>Top 10 Pubs</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>1736370</td>      <td>D. Koller</td>      <td>351</td>      <td>130</td>      <td>Probabilistic Graphical Models - Principles and Techniques     |     The Genotype-Tissue Expression (GTEx) project     |     FastSLAM: a factored solution to the simultaneous localization and mapping problem     |     Support Vector Machine Active Learning with Applications to Text Classification     |     Max-Margin Markov Networks     |     SCAPE: shape completion and animation of people     |     Self-Paced Learning for Latent Variable Models     |     The Genotype-Tissue Expression (GTEx) pilot analysis: Multitissue gene regulation in humans     |     Decomposing a scene into geometric and semantically consistent regions     |     Toward Optimal Feature Selection</td>    </tr>    <tr>      <th>1</th>      <td>2081968396</td>      <td>D. Koller</td>      <td>5</td>      <td>1</td>      <td>Systematic Analysis of Breast Cancer Morphology Uncovers Stromal Features Associated with Survival     |     [Relevance of health geographic research for dermatology].     |     Convolutional neural networks of H&amp;E-stained biopsy images accurately quantify histologic features of non-alcoholic steatohepatitis     |     IDENTIFYING GENETIC DRIVERS OF CANCER MORPHOLOGY     |     Features Associated with Survival Systematic Analysis of Breast Cancer Morphology Uncovers Stromal</td>    </tr>    <tr>      <th>2</th>      <td>50678963</td>      <td>D. Koller</td>      <td>1</td>      <td>0</td>      <td>½º Äääöòòòò Èöóóóóóðð×øø Êêððøøóòòð Åóð×</td>    </tr>    <tr>      <th>3</th>      <td>2049948919</td>      <td>Daphne Koller</td>      <td>1</td>      <td>1</td>      <td>Team-Maxmin Equilibria☆</td>    </tr>    <tr>      <th>4</th>      <td>2081968988</td>      <td>Daphne Koller</td>      <td>1</td>      <td>0</td>      <td>Í××òò Øùöö Àààööö Blockin× Ò Ý×××ò Aeaeøûóöö Äääöòòòò´´üøøòòòò ×øöö Blockinøµ</td>    </tr>    <tr>      <th>5</th>      <td>2081968959</td>      <td>Daphne Koller</td>      <td>3</td>      <td>1</td>      <td>Abstract 1883: Large scale viability screening with PRISM underscores non-inhibitory properties of small molecules     |     Strategic and Tactical Decision-Making Under Uncertainty     |     2 . 1 Pursuit / Evader in the UAV / UGV domain</td>    </tr>    <tr>      <th>6</th>      <td>1753668669</td>      <td>Daphne Koller</td>      <td>4</td>      <td>1</td>      <td>A Data-Driven Lens to Understand Human Biology: An Interview with Daphne Koller     |     Conservation and divergence in modules of the transcriptional programs of the human and mouse immune systems [preprint]     |     ImmGen at 15     |     Speaker-specific terms and resources</td>    </tr>    <tr>      <th>7</th>      <td>46193831</td>      <td>D. Stanford</td>      <td>3</td>      <td>0</td>      <td>Unmanned Aircraft Systems     |     Inference : Exploiting Local Structure     |     Learning : Parameter Estimation</td>    </tr>  </tbody></table>
# MAGIC 
# MAGIC Then generate an author+paper graph based on her ID:`1736370` 
# MAGIC 
# MAGIC ```
# MAGIC kolsGraph.build_author_citation_graph(1736370)
# MAGIC kolsGraph.print_basic_stats()
# MAGIC ```
# MAGIC 
# MAGIC This command performs the following steps: 
# MAGIC 
# MAGIC * Retrieve all her papers indexed in S2AG add those papers and all authors to the graph
# MAGIC * Iterate through those papers and add any papers that either she cites 'meaninfully' or that cite her 'meaningfully' (for a definition of what constitutes a 'meaningful' citation, see [Valenzuela et al 2015](https://ai2-website.s3.amazonaws.com/publications/ValenzuelaHaMeaningfulCitations.pdf)). 
# MAGIC * Add or link authors to these papers. 
# MAGIC * Iterate over all papers in this extended set and add all citations / references between them.
# MAGIC * Print out the results
