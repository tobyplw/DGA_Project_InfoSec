from collections import Counter
import pandas as pd
import features
import pickle


class predictor:
    def __init__(self, file_name = None):
        self.ngrams_counter = features.get_eng_ngrams()

        if file_name:
            self.model = self.load_model(file_name)

    def load_model(self, model_file_name):
        return pickle.load(open(model_file_name, "rb"))

    def predict_isDga(self, domain):
        feature_df = features.extract_features(domain = domain, ngrams_counter = self.ngrams_counter)

        result = self.model.predict(feature_df)
        data = result[0]
        if data == 0:
            return False
        elif data == 1:
            return True
        else:
            return None


pred = predictor("DGA_model.pickle")

list = ["increaseinside.net","rememberbright.net","riddenready.net","belongdaughter.net",]

for x in list:
    print(pred.predict_isDga(x))