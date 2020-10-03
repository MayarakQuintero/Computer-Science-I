'''
Linear regression

YOUR NAME HERE

Main file for linear regression and model selection.
'''

import numpy as np
from sklearn.model_selection import train_test_split
import util


class DataSet(object):
    '''
    Class for representing a data set.
    '''

    def __init__(self, dir_path):
        '''
        Constructor
        Inputs:
            dir_path: (string) path to the directory that contains the
              file
        '''

        self.dir_path = dir_path
        self.labels, self.data = util.load_numpy_array(dir_path, "data.csv")
        parameters = util.load_json_file(dir_path, "parameters.json")
        self.dependent_var = parameters["dependent_var"]
        self.name = parameters["name"]
        self.predictor_vars = parameters["predictor_vars"]
        self.seed = parameters["seed"]
        self.training_fraction = parameters["training_fraction"]
        self.train_data, self.test_data = train_test_split(self.data, 
            train_size=self.training_fraction, test_size=None, random_state=self.seed)

class Model(object):
    '''
    Class for representing a model.
    '''

    def __init__(self, dataset, pred_vars):
        '''
        Construct a data structure to hold the model.
        Inputs:
            dataset: an dataset instance
            pred_vars: a list of the indices for the columns (of the
              original data array) used in the model.
        '''
        self.dataset = dataset
        self.pred_vars = pred_vars
        self.dep_var = dataset.dependent_var
        y_obs = dataset.train_data[:, self.dep_var]
        x_predictors = dataset.train_data[:, self.pred_vars]
        x_predictors_1 = util.prepend_ones_column(x_predictors)
        self.y_obs_t = dataset.test_data[:, self.dep_var]
        self.x_predictors_t = dataset.test_data[:, self.pred_vars]
        self.x_predictors_1_t = util.prepend_ones_column(self.x_predictors_t)
        self.beta = util.linear_regression(x_predictors_1, y_obs)
        self.R2 = self.get_R2(x_predictors_1, y_obs)
        self.adj_R2 = self.R2 - (1 - self.R2) * (len(self.pred_vars) / 
            (dataset.train_data.shape[0] - len(self.pred_vars) - 1))
    
    def get_R2(self, X, y):
        '''
        Computes R2

        Inputs: 
            X: Predictor variable matriz
            y: Dependent variable array

        Returns: 
            R2 value of a given model.
        '''
        
        y_pred = util.apply_beta(self.beta, X)
        calc_R2 = 1 - sum((y - y_pred)**2) / sum((y - y.mean())**2)

        return calc_R2


    def __repr__(self):
        '''
        Format model as a string.
        '''

        # Replace this return statement with one that returns a more
        # helpful string representation
        return "!!! You haven't implemented the Model __repr__ method yet !!!"

def compute_single_var_models(dataset):
    '''
    Computes all the single-variable models for a dataset

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        List of Model objects, each representing a single-variable model
    '''
    list_models = []
    for predictor_var in dataset.predictor_vars:
        list_models.append(Model(dataset, [predictor_var]))

    return list_models


def compute_all_vars_model(dataset):
    '''
    Computes a model that uses all the predictor variables in the dataset

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A Model object that uses all the predictor variables
    '''

    # Replace None with a model object
    return Model(dataset, dataset.predictor_vars)


def compute_best_pair(dataset):
    '''
    Find the bivar'iate model with the best R2 value

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A Model object for the best bivariate model
    '''
    model_max = None
    R2_max = 0
    for i in range(len(dataset.predictor_vars)):
        for j in range(i+1, len(dataset.predictor_vars)):
            model_temp = Model(dataset, [i,j])
            if model_temp.R2 > R2_max:
                R2_max = model_temp.R2
                model_max = model_temp
    return model_max


def backward_elimination(dataset):
    '''
    Given a dataset with P predictor variables, uses backward elimination to
    select models for every value of K between 1 and P.

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A list (of length P) of Model objects. The first element is the
        model where K=1, the second element is the model where K=2, and so on.
    '''
        # Replace [] with the list of models
    model_list = [Model(dataset, dataset.predictor_vars)]
    R2_max = 0
    index_max = 0
    model_max = None
    temp_predictor_vars = dataset.predictor_vars

    while len(temp_predictor_vars) > 1:
        for index in range(len(temp_predictor_vars)):
            model_temp = Model(dataset, 
                drop_pred_var(temp_predictor_vars, index))
            if model_temp.R2 > R2_max:
                R2_max = model_temp.R2
                model_max = model_temp
                index_max = index 
        temp_predictor_vars = drop_pred_var(temp_predictor_vars, index_max)
        model_list.append(model_max) 
        R2_max = 0
        index_max = 0
        model_max = None
   
    return model_list[::-1]

def drop_pred_var(predictor_vars, i):
    '''
    Generate a list of predictor variables based on the index
    '''
    return predictor_vars[0:i] + predictor_vars[i+1:len(predictor_vars)+1]


def choose_best_model(dataset):
    '''
    Given a dataset, choose the best model produced
    by backwards elimination (i.e., the model with the highest
    adjusted R2)

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A Model object
    '''
    best_model = None
    max_adj_R2 = 0
    for model in backward_elimination(dataset):
        if model.adj_R2 > max_adj_R2:
            best_model = model
            max_adj_R2 = model.adj_R2

    return best_model


def validate_model(dataset, model):
    '''
    Given a dataset and a model trained on the training data,
    compute the R2 of applying that model to the testing data.

    Inputs:
        dataset: (DataSet object) a dataset
        model: (Model object) A model that must have been trained
           on the dataset's training data.

    Returns:
        (float) An R2 value
    '''

    R2_test = model.get_R2(model.x_predictors_1_t, model.y_obs_t)

    return R2_test
