import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
import pandas as pd
import numpy as np
from sklearn.externals import joblib


# https://stackoverflow.com/questions/5125619/why-list-doesnt-have-safe-get-method-like-dictionary
def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

data_path = sys.argv[1]
model_output_path = sys.argv[2]
results_path = sys.argv[3]
N_PROCESS = int(safe_list_get(sys.argv, 4, 4))
TRAINING = float(safe_list_get(sys.argv, 5, '0.75'))
FEATURES_MAX_MULT = float(safe_list_get(sys.argv, 6, '100'))

N_ESTIMATORS = 128


df = pd.DataFrame.from_csv(data_path, header=0, sep=',', index_col=0)
df['is_train'] = np.random.uniform(0, 1, len(df)) <= TRAINING

train = df[df['is_train'] == True]
test = df[df['is_train'] == False]

features = df.columns[:len(df.columns) - 2]
clf = RandomForestClassifier(n_estimators=N_ESTIMATORS, n_jobs=N_PROCESS)
# clf = svm.LinearSVC(probability=True)
y, target_names = pd.factorize(train['puduml___result'], sort=True)
clf.fit(train[features], y)

results_file = open(results_path, 'w')

preds = target_names[clf.predict(test[features])]
results_file.write(str(pd.crosstab(test['puduml___result'], preds, rownames=['actual'], colnames=['preds'])) + "\n")
results_file.write("\ntarget_names: %s\n" % ",".join(target_names) + "\n")

predictions_with_prob = clf.predict_proba(test[features])


total = {}
results = {}
for index, predition_row in enumerate(predictions_with_prob):
    real_result = test['puduml___result'][index]
    total[real_result] = total.get(real_result, 0) + 1
    result_index = list(target_names).index(real_result)
    if not results.get(real_result):
        results[real_result] = {}
    result_value = round(predition_row[result_index], 1)
    if not results[real_result].get(result_value):
        results[real_result][result_value] = 0
    results[real_result][result_value] += 1

for result in results.keys():
    keys = sorted(results[result].keys(), reverse=True)
    current_sum = 0
    for result_value in keys:
        value = results[result][result_value]
        current_sum += value
        results_file.write("%s\t%s\t%s\t%s%%\n" % (result, result_value, value, round(1.0*current_sum/total[result], 2)))

joblib.dump(clf, model_output_path)

# Write used features
feature_importance = clf.feature_importances_
std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis=0)
indices = np.argsort(feature_importance)[::-1]

base_name = model_output_path.split(".pkl")[0]

with open(base_name + ".features", "w") as _file:
    for f in range(train[features].shape[1]):
        _file.write("%s\n" % features[indices[f]])


first_model_number = None
found_final = False
with open(base_name + ".recommended_features", "w") as _file:
    for f in range(train[features].shape[1]):
        if first_model_number is None:
            first_model_number = feature_importance[indices[f]]
        _file.write(features[indices[f]] + "\n")
        if not found_final and first_model_number / feature_importance[indices[f]] > FEATURES_MAX_MULT:
            found_final = True
            _file.write("\nRecommendation you can consider use %s features to train\n" % (f + 1))
            break
with open(base_name + ".targets", "w") as _file:
    for i, target in enumerate(target_names):
        _file.write("%s\t%s\n" % (i, target))
# import ipdb; ipdb.set_trace()
# results_file.write("hola")

results_file.close()
