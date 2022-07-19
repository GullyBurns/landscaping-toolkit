# Chan Zuckerberg Landscaping Toolkit
> This is a public-facing library of components designed to support and facilitate 'scientific knowledge landscaping' within the Chan Zuckerberg Initiative's Science Program. It consists of several utility libraries to help build and analyze corpora of scientific knowledge expressed as natural language and structured data. This system is built on the excellent <a href='https://nbdev.fast.ai/'>`nbdev`</a> package 


 ## Install

 `pip install git+https://github.com/GullyBurns/czLandscapingTk.git`

 ## How to use:

 This libray is built on [databricks_to_nbdev_template](https://github.com/GullyBurns/databricks_to_nbdev_template), which is modified version of [nbdev_template](https://github.com/fastai/nbdev_template) tailored to work with databricks notebooks.

The steps to using this are: 
1. Use the basic template to clone your repository and access it via databricks. 
2. Fill in your `settings.ini` file (especially with any `requirements` that would need to be built to run your code).
3. Place your scripts and utility notebooks in subdirectories of the `databricks` folder in the file hierarchy.
4. Any databricks notebooks that contain the text: `from nbdev import *` will be automatically converted to Jupyter notebooks that live at the root level of the repository.
5. When you push this repository to Github from Databricks, Jupyter notebooks will be built, added to the repo and then processed by nbdev to generate modules and documentation (refer to https://nbdev.fast.ai/ for full documentation on how to do this). Note that pushing code to Github will add and commit *more* code to github, requiring you to perform another `git pull` to load and refer to the latest changes in your code.  

 ## Instructions for how to use Toolkit Classes:

 ### AirtableUtils Class

  
Load the class and instantiate it with the API-KEY from Airtable:
```
from czLandscapingTk.airtableUtils import AirtableUtils
atu = AirtableUtils('keyXYZXYZXYZYXZY')
```

Read a complete table into a pandas dataframe: 
```
# atu.read_airtable(<notebook id>, <table id>)
atu.read_airtable('appXYZXYZXYZXYZ', 'tblXYZXYZXYZXYZ')
```

Write a dataframe to an Airtable (note, column names of Airtable must match the columns of the dataframe and must be instantiated manually ahead of time): 
```
# atu.send_df_to_airtable(<notebook id>, <table id>, df):
df = <YOUR DATA>
atu.send_df_to_airtable('appXYZXYZXYZXYZ', 'tblXYZXYZXYZXYZ', df)
```

 ### NetworkxS2AG Class

 

Instantiate the class using an api key you should obtain from the S2AG team to permit more than 100 request calls per 5 minutes. This script will burn through that limit immediately. Obtain API keys here: https://www.semanticscholar.org/product/api#Partner-Form

```
from czLandscapingTk.networkxS2AG import NetworkxS2AG
kolsGraph = NetworkxS2AG('<API-KEY-FROM-S2AG-TEAM>')
```

Maybe start by searching for a reseracher by name. e.g. [Daphne Koller](https://api.semanticscholar.org/graph/v1/author/search?query=Daphne+Koller) 

```
kolsGraph.search_for_disambiguated_author('Daphne Koller')
```

Generating the following output: 
<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;"><th></th>      <th>authorId</th>      <th>name</th>      <th>paperCount</th>      <th>hIndex</th>      <th>Top 10 Pubs</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>1736370</td>      <td>D. Koller</td>      <td>351</td>      <td>130</td>      <td>Probabilistic Graphical Models - Principles and Techniques     |     The Genotype-Tissue Expression (GTEx) project     |     FastSLAM: a factored solution to the simultaneous localization and mapping problem     |     Support Vector Machine Active Learning with Applications to Text Classification     |     Max-Margin Markov Networks     |     SCAPE: shape completion and animation of people     |     Self-Paced Learning for Latent Variable Models     |     The Genotype-Tissue Expression (GTEx) pilot analysis: Multitissue gene regulation in humans     |     Decomposing a scene into geometric and semantically consistent regions     |     Toward Optimal Feature Selection</td>    </tr>    <tr>      <th>1</th>      <td>2081968396</td>      <td>D. Koller</td>      <td>5</td>      <td>1</td>      <td>Systematic Analysis of Breast Cancer Morphology Uncovers Stromal Features Associated with Survival     |     [Relevance of health geographic research for dermatology].     |     Convolutional neural networks of H&amp;E-stained biopsy images accurately quantify histologic features of non-alcoholic steatohepatitis     |     IDENTIFYING GENETIC DRIVERS OF CANCER MORPHOLOGY     |     Features Associated with Survival Systematic Analysis of Breast Cancer Morphology Uncovers Stromal</td>    </tr>    <tr>      <th>2</th>      <td>50678963</td>      <td>D. Koller</td>      <td>1</td>      <td>0</td>      <td>½º Äääöòòòò Èöóóóóóðð×øø Êêððøøóòòð Åóð×</td>    </tr>    <tr>      <th>3</th>      <td>2049948919</td>      <td>Daphne Koller</td>      <td>1</td>      <td>1</td>      <td>Team-Maxmin Equilibria☆</td>    </tr>    <tr>      <th>4</th>      <td>2081968988</td>      <td>Daphne Koller</td>      <td>1</td>      <td>0</td>      <td>Í××òò Øùöö Àààööö Blockin× Ò Ý×××ò Aeaeøûóöö Äääöòòòò´´üøøòòòò ×øöö Blockinøµ</td>    </tr>    <tr>      <th>5</th>      <td>2081968959</td>      <td>Daphne Koller</td>      <td>3</td>      <td>1</td>      <td>Abstract 1883: Large scale viability screening with PRISM underscores non-inhibitory properties of small molecules     |     Strategic and Tactical Decision-Making Under Uncertainty     |     2 . 1 Pursuit / Evader in the UAV / UGV domain</td>    </tr>    <tr>      <th>6</th>      <td>1753668669</td>      <td>Daphne Koller</td>      <td>4</td>      <td>1</td>      <td>A Data-Driven Lens to Understand Human Biology: An Interview with Daphne Koller     |     Conservation and divergence in modules of the transcriptional programs of the human and mouse immune systems [preprint]     |     ImmGen at 15     |     Speaker-specific terms and resources</td>    </tr>    <tr>      <th>7</th>      <td>46193831</td>      <td>D. Stanford</td>      <td>3</td>      <td>0</td>      <td>Unmanned Aircraft Systems     |     Inference : Exploiting Local Structure     |     Learning : Parameter Estimation</td>    </tr>  </tbody></table>

Then generate an author+paper graph based on her ID:`1736370` 

```
kolsGraph.build_author_citation_graph(1736370)
kolsGraph.print_basic_stats()
```

This command performs the following steps: 

* Retrieve all her papers indexed in S2AG add those papers and all authors to the graph
* Iterate through those papers and add any papers that either she cites 'meaninfully' or that cite her 'meaningfully' (for a definition of what constitutes a 'meaningful' citation, see [Valenzuela et al 2015](https://ai2-website.s3.amazonaws.com/publications/ValenzuelaHaMeaningfulCitations.pdf)). 
* Add or link authors to these papers. 
* Iterate over all papers in this extended set and add all citations / references between them.
* Print out the results

 ### QueryTranslator class

 

This class processes a Pandas Dataframe where one of the columns describes a Boolean Query that could be issued on an online scientific database written as a string (e.g., this query searches for various terms denoting neurodegenerative diseases and then links them to the phrase "Machine Learning": `'("Neurodegeneration" | "Neurodegenerative disease" | "Alzheimers Disease" | "Parkinsons Disease") & "Machine Learning"'`. This dataframe must also contain a numerical ID column to identify each query. 

Load the class and instantiate it with dataframe:
```
from czLandscapingTk.queryTranslator import QueryType, QueryTranslator
df = pd.DataFrame({'ID':0, 'query':'("Neurodegeneration" | "Neurodegenerative disease" |
    "Alzheimers Disease" | "Parkinsons Disease") & "Machine Learning"'})
qt = QueryTranslator(df, 'query')
```

Generate a list of queries that work on Pubmed:
```
(corpus_ids, pubmed_queries) = qt.generate_queries(QueryType.pubmed)
```

Generate a list of queries that work on European PMC:
```
(corpus_ids, epmcs_queries) = qt.generate_queries(QueryType.epmc)
```

 ### ESearchQuery / EFetchQuery

 

These classes provides an interface for performing queries on NCBI Etuils. This is designed to work in conjunction with the `QueryTranslator` class. 

Load the class and instantiate it:
```
from czLandscapingTk.searchEngineUtils import ESearchQuery, EFetchQuery



df = pd.DataFrame({'ID':0, 'query':'("Neurodegeneration" | "Neurodegenerative disease" | "Alzheimers Disease" | "Parkinsons Disease") & "Machine Learning"'})
qt = QueryTranslator(df, 'query')
```

Generate a list of queries that work on Pubmed:
```
(corpus_ids, pubmed_queries) = qt.generate_queries(QueryType.pubmed)
```

Generate a list of queries that work on European PMC:
```
(corpus_ids, epmcs_queries) = qt.generate_queries(QueryType.epmc)
```

 ### EuroPMCQuery

```


```
