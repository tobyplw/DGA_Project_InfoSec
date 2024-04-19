import pandas as pd
import numpy as np
from sklearn import tree, model_selection, metrics
import pickle
import features_isDGA
import time

# A portion of this code was written by following worksheets found at https://github.com/yevheniyc/Projects in the DGA Detection using Machine Learning Series
# Part 2 - Machine Learning: https://notebook.community/yevheniyc/Python/1m_ML_Security/notebooks/day_3/Worksheet%206%20-%20DGA%20Detection%20ML%20Classification

#read in data files
data_frame = pd.read_csv("./data/dga_data_full.csv")
data_frame.drop(['host', 'subclass'], axis=1, inplace=True)
print("\n______________________________________________________________\n")

print("Data Frame shape: " + str(data_frame.shape))

print("Data Frame Sample: ")
print(data_frame.sample(n=5).head())


#extract features from the data
data_frame = features_isDGA.extract_features(data_frame=data_frame)


data_frame.isDGA = data_frame.isDGA.replace(to_replace = 'dga', value = 1)
data_frame.isDGA = data_frame.isDGA.replace(to_replace='legit', value = 0)

print("\n______________________________________________________________\n")
print("Data Frame with Features Sample: ")
print(data_frame.sample(n=5).head())



data_frame_final = data_frame
file_name = './data/dga_features_final_datafile.csv'
print("\n______________________________________________________________\n")
print("Saving Features to: " + file_name)
data_frame_final.to_csv(file_name, index=False)
data_frame_final.head()



target = data_frame_final['isDGA']
feature_matrix = data_frame_final.drop(['isDGA'], axis=1)

#split training, testing data 75% to 25%
feature_matrix_train, feature_matrix_test, target_train, target_test = model_selection.train_test_split(feature_matrix, target, test_size = 0.25, random_state = 33)

print("\n______________________________________________________________\n")
print("\n Feature Training Counts: " + str(feature_matrix_train.count()))
print("\n Feature Test Counts: " +str(feature_matrix_test.count()))

print("\n______________________________________________________________\n")
print("\n Sample of Feature Training Set: ")
print(feature_matrix_train.sample(n=5).head())


print("\n______________________________________________________________\n")
print("Training Model...")
#create DecisionTree Classifier
classifier = tree.DecisionTreeClassifier()
start = time.time()
classifier = classifier.fit(feature_matrix_train, target_train)
end = time.time()
print("Training Completed...")
print('Training time: ' + str(end-start) + " sec")



print("\n______________________________________________________________\n")
#predict domains 
target_prediction = classifier.predict(feature_matrix_test)

#get accuracy score
print("Model Accuracy: " + str(metrics.accuracy_score(target_test, target_prediction)) + "%")
print('\nConfusion Matrix\n', metrics.confusion_matrix(target_test, target_prediction))
print("\n______________________________________________________________\n")
print("Classification Report: \n")
print(metrics.classification_report(target_test, target_prediction, target_names=['legit', 'dga']))


#load model into pickle file 
model_file_name = "DGA_model.pickle"
print("\n______________________________________________________________\n")
print("Dumping model into: " + model_file_name)
pickle.dump(classifier, open(model_file_name, "wb"))




