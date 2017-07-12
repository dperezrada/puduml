# Pudu ML

A group of tools to make text analytics and machine learning.

## Requirements 

 * Python3

## Install

 * pip install -r requirements.txt

## Components

### Relevant words

Tries to identify all the relevant phrases from a input documents. The input format must be:

```
<id>	<classification>	<title>	<text>
```

The separation between the field must be tabs, and the values must not have any tab


#### Run

```
./relevant_words/find_all_relevants.sh data/samples/all_episte_docs_small_5000.tsv.gz  /tmp/puduml
```