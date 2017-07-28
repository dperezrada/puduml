import sys
import pandas as pd
from sklearn.externals import joblib


data_path = sys.argv[1]
model_path = sys.argv[2]

#Read CSV file (DISCOURAGED, please use pandas.read_csv() instead).
#df = pd.DataFrame.from_csv(data_path, compression='gzip', header=0, sep=',', index_col=0)
df = pd.read_csv(data_path, header=0, sep=',', index_col=0, compression='gzip')

features = df.columns[:len(df.columns) - 1]
clf = joblib.load(model_path)
base_model = model_path.split(".pkl")[0]
targets = [line.rstrip("\r\n").split("\t")[-1] for line in open(base_model + '.targets').readlines()]

prediction = clf.predict_proba(df[features])
i = 0
results = {}
total_pos = 0

print("\t".join(["id", ] + targets))
for key, row in df.iterrows():
    pred = [key, ] + list([round(pred_el, 4) for pred_el in prediction[i]])
    print("\t".join([str(el) for el in pred]))
    i += 1
