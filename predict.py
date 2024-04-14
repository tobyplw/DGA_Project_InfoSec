import pandas as pd
import features_isDGA
import features_isDictDGA
import pickle

class predictor:
    def __init__(self):
        self.ngrams_counter = features_isDGA.get_eng_ngrams()
        self.dgaModel, self.dictModel = self.load_models()

    def load_models(self):
        dga_file_name = "DGA_model.pickle"
        dict_file_name = "Dict_DGA_model.pickle"
        return pickle.load(open(dga_file_name, "rb")), pickle.load(open(dict_file_name, "rb"))

    def predict_isDga(self, domain):
        feature_df = features_isDGA.extract_features(domain = domain, ngrams_counter = self.ngrams_counter)

        result = self.dgaModel.predict(feature_df)
        data = result[0]
        if data == 0:
            return False
        elif data == 1:
            return True
        else:
            return None
    
    def predict_isDictDga(self, domain):
        feature_df = features_isDictDGA.extract_features(domain = domain)

        result = self.dictModel.predict(feature_df)
        data = result[0]
        if data == 0:
            return False
        elif data == 1:
            return True
        else:
            return None
