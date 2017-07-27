# Pudu ML

A group of tools to make text analytics and machine learning.

## Requirements 

 * Python3

## Install

 * pip install -r requirements.txt
 * cd utils/python;python setup.py develop

## Components

### Relevant words

Tries to identify all the relevant phrases from a input documents. The input format must be:

```
<id>	<classification>	<title>	<text>
```

The separation between the field must be tabs, and the values must not have any tab


#### Run

```
./relevant_words/find_all_relevants.sh data/samples/all_episte_docs_small_5000.tsv.gz  /tmp/puduml/get_words
```

## Classify

Create a model to predict the classification of a certain document

### Run
Example with systematic_reviews
```
export PUDUML_CLASSIFICATION="systematic_review"
```

#### Prepare features

```
mkdir -p /tmp/puduml/models/${PUDUML_CLASSIFICATION}
cut -d$'\t' -f1 /tmp/puduml/get_words/classifications/${PUDUML_CLASSIFICATION}_positive.tsv | head -n 200 >  /tmp/puduml/models/${PUDUML_CLASSIFICATION}/features.txt
cut -d$'\t' -f1 /tmp/puduml/get_words/classifications/${PUDUML_CLASSIFICATION}_negative.tsv | head -n 200 >>  /tmp/puduml/models/${PUDUML_CLASSIFICATION}/features.txt
```

#### Train the model
```
./classification_model/create_model.sh data/samples/all_episte_docs_small_5000.tsv.gz systematic_review /tmp/puduml/models/${PUDUML_CLASSIFICATION}/features.txt /tmp/puduml/classifier
```

#### Predict
Input file has the same input but with no classification (empty) must have the empty space

```
./classification_model/predict.sh data/samples/all_episte_docs_small_5000.tsv.gz /tmp/puduml/classifier/model/systematic_review.pkl /tmp/puduml/classifier/model/systematic_review.features /tmp/puduml/classifier/tmp
```

