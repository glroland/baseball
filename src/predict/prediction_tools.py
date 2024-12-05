""" Utility methods for use by prediction services. """
import os
import copy
import logging
import joblib
import pandas as pd
from pandas.api.typing import NAType
import numpy as np
import psycopg
import tqdm
import torch
from torch import optim
from torch import nn
import onnx
#import onnxruntime
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

SCALER_SUFFIX = "_scaler.gz"

# pylint: disable=too-few-public-methods
class PredictionConstants:
    """ Constants used by the prediction tools. """
    VALUE_TRUE = 1
    VALUE_FALSE = 0

    NUM_EPOCHS = 300
    BATCH_SIZE = 10
    LOSS_RATE = 0.0001

def fail(msg : str):
    """ Fail with the message provided.
    
        msg - error message
    """
    logger.error(msg)
    raise ValueError(msg)

def get_config_value(key : str, default_value : str):
    """ Gets the specified config key from an environment variable and if not set,
        return the default.
        
        key - env var name
        default_value - default value
    """
    if key is None or len(key) == 0:
        fail("get_config_value() no key provided")

    if key in os.environ:
        return os.environ[key]

    return default_value

def acquire_data(connection_str : str, sql : str, limit : int = None) -> pd.DataFrame:
    """ Populates a data frame based on the provided baseball query
    
        connection_str - connection string
        sql - sql to execute
        limit - optional row limit
    """
    # validate arguments
    if connection_str is None or len(connection_str) == 0:
        fail("acquire_data() - connection string is empty!")
    if sql is None or len(sql) == 0:
        fail("acquire_data() - sql query is empty!")

    logger.info("Using DB Connection String: %s", connection_str)

    # apply limit (optional)
    if limit is not None:
        sql += "limit " + str(limit)

    # pylint: disable=not-context-manager
    with psycopg.connect(connection_str) as sql_connection:
        with sql_connection.cursor() as sql_cursor:
            sql_cursor.execute(sql) #, [])

            results = sql_cursor.fetchall()
            return pd.DataFrame(results, columns=[desc[0] for desc in sql_cursor.description])

def model_train(model, train_x, train_y, val_x, val_y):
    """ Train the provided model on the provided training and test data sets.
    
        model - pytorch model
        train_x, train_y - training data
        val_X, val_y - validation data set
    """
    # loss function and optimizer
    loss_fn = nn.BCELoss()      # binary cross entropy
    optimizer = optim.Adam(model.parameters(), lr=PredictionConstants.LOSS_RATE)

    batch_start = torch.arange(0, len(train_x), PredictionConstants.BATCH_SIZE)

    # Hold the best model
    best_acc = - np.inf   # init to negative infinity
    best_weights = None

    for epoch in range(PredictionConstants.NUM_EPOCHS):
        # train model
        model.train()
        with tqdm.tqdm(batch_start, unit="batch", mininterval=0, disable=True) as tqdm_bar:
            tqdm_bar.set_description(f"Epoch {epoch}")
            for start in tqdm_bar:
                # take a batch
                batch_x = train_x[start:start+PredictionConstants.BATCH_SIZE]
                batch_y = train_y[start:start+PredictionConstants.BATCH_SIZE]

                # forward pass
                y_pred = model(batch_x)
                loss = loss_fn(y_pred, batch_y)

                # backward pass
                optimizer.zero_grad()
                loss.backward()

                # update weights
                optimizer.step()

                # print progress
                acc = (y_pred.round() == batch_y).float().mean()
                tqdm_bar.set_postfix(
                    loss=float(loss),
                    acc=float(acc)
                )

        # evaluate accuracy at end of each epoch
        model.eval()
        y_pred = model(val_x)
        acc = (y_pred.round() == val_y).float().mean()
        acc = float(acc)
        if acc > best_acc:
            best_acc = acc
            best_weights = copy.deepcopy(model.state_dict())

    # restore model and return best accuracy
    model.load_state_dict(best_weights)
    return best_acc

def save_model(model, num_features, filename):
    """ Save the model to disk in onnx format.
    
        model - pytorch model
        num_features - number of features
        filename - output filename
    """
    if model is None:
        fail("save_model() - no model provided")
    if num_features < 1:
        fail(f"save_model() - insufficient features provided.  {num_features}")
    if filename is None or len(filename) == 0:
        fail("save_model() - output filename is empty")

    # save the model
    torch_input = torch.randn(1, 1, num_features, num_features)
    onnx_program = torch.onnx.export(model, torch_input, filename, dynamo=False)
#    onnx_program.save(filename)

def load_model(filename):
    """ Load a persisted onnx model from disk.
    
        filename - model filename 
    """
    # load the onnx file
    onnx_model = onnx.load(filename)
    onnx.checker.check_model(onnx_model)
    return onnx_model

def one_for_true(row, label):
    """ Simple utility function that returns 1 or 0 for a given cell, depending on whether
        its populated or not.
    
        row - dataframe row
        label - column name
    """
    v = row[label]
    if v:
        return PredictionConstants.VALUE_TRUE
    return PredictionConstants.VALUE_FALSE

def get_tf_num_for_value(x):
    """ Gets the true/false numeric value for a given variable, based on whether it 
        has been populated with something.
        
        x - value to test
    """
    if not isinstance(x, NAType) and len(x) > 0:
        return PredictionConstants.VALUE_TRUE
    return PredictionConstants.VALUE_FALSE

def replace_populated_values_with_tf_num(df, old_column, new_column, drop_column_flag=False):
    """ For a dataframe, replace column value with a 1 or 0, depending on whether or not
        it is populated.
        
        df - dataframe
        old_column - existing column name
        new_column - name of column to receive the new values
        drop_column_flag - whether to drop the old column after processing
    """
    df[new_column] = df[old_column].apply(lambda x: get_tf_num_for_value(x))

    if drop_column_flag:
        df.drop(old_column, axis=1, inplace=True)

def get_tf_num_for_bool(x):
    """ Gets the true/false numeric value for a given boolean.
        
        x - value to test
    """
    if x:
        return PredictionConstants.VALUE_TRUE
    return PredictionConstants.VALUE_FALSE

def replace_boolean_values_with_tf_num(df, old_column, new_column, drop_column_flag=False):
    """ For a dataframe, replace a boolean value with a 1 or 0, depending on whether true or false.
        
        df - dataframe
        old_column - existing column name
        new_column - name of column to receive the new values
        drop_column_flag - whether to drop the old column after processing
    """
    df[new_column] = df.apply(lambda x: one_for_true(x, old_column), axis=1)

    if drop_column_flag:
        df.drop(old_column, axis=1, inplace=True)

def extract_categorical_columns(df, categorical_cols):
    """ For a dataframe with a column that contains a limited number of values, create dummy columns
        per column value.
        
        df - dataframe
        drop_column_flag - whether to drop the old column after processing
    """
    return pd.get_dummies(df, columns=categorical_cols, prefix=categorical_cols)

def scale_int_values(df, old_column, new_column, drop_column_flag=False, save_scaler_file=None):
    """ For a dataframe, create a column with a scaled numerical range between 1 and 0.  Uses
        StandardScaler.
        
        df - dataframe
        old_column - existing column name
        new_column - name of column to receive the new values
        drop_column_flag - whether to drop the old column after processing
        save_scaler_file - where to save the scaler file (optional)
    """
    scaler = StandardScaler()
    scaler.fit(df.iloc[:, df.columns.get_loc(old_column) : df.columns.get_loc(old_column) + 1])
    df[new_column] = scaler.transform(
            df.iloc[:, df.columns.get_loc(old_column) : df.columns.get_loc(old_column) + 1])

    if drop_column_flag:
        df.drop(old_column, axis=1, inplace=True)

    save_scaler(scaler, save_scaler_file)

def scale_single_value(scaler, value):
    """ Scales a single value
    
        scaler - scaler
        value - value
    """
    npa = scaler.transform(np.array([value]).reshape(-1, 1))
    return npa.tolist()[0][0]

def drop_column(df, column):
    """ Drop the column from the dataframe.
    
        df - data frame
        column - column name to remove
    """
    df.drop(column, axis=1, inplace=True)

def evaluate_model(model, test_x, test_y, roc_filename=None, label_descs=None):
    """ Evaluate the performance of the provided model.

        model - pytorch model
        test_x - test data set (input)
        test_y - test data set (expected output)
        roc_filename - if provided, save the roc curve to an image file
        label_descs - array of the label descriptions
    """
    model.eval()
    with torch.no_grad():
        # Test out inference with 5 samples
        for i in range(5):
            y_pred = model(test_x[i:i+1])
            print(f"{test_x[i].numpy()} -> {y_pred[0].numpy()} (expected {test_y[i].numpy()})")

        # Setup the graph
        plt.title("Receiver Operating Characteristics")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")

        # Plot the ROC curve
        size_y = y_pred.shape[1]
        y_pred = model(test_x)
        i = 0
        while i < size_y:
            # pylint: disable=unused-variable
            fpr, tpr, thresholds = roc_curve(test_y[:, i : i+1], y_pred[:, i : i+1])
            label = str(i)
            if label_descs is not None and len(label_descs) >= i:
                label = label_descs[i]
            plt.plot(fpr, tpr, label=label)        # ROC curve = TPR vs FPR
            i += 1
        if i > 0:
            plt.legend(loc=0)

        if roc_filename is not None:
            plt.savefig(roc_filename)

        # must be last - after show a new figure is created
        plt.show()

def save_scaler(scaler, filename):
    """ Saves the provided scaler for later use.

        scaler - scaler
        filename - filename
    """
    # validate parameters
    if scaler is None:
        fail("save_scaler() cannot persist a null scaler")
    if filename is None or len(filename) == 0:
        fail("save_scaler() No filename provided")

    # save a scaler
    joblib.dump(scaler, filename)

def load_scaler(filename):
    """ Loads a previously persisted scaler.

        filename - filename
    """
    # validate parameters
    if filename is None or len(filename) == 0:
        fail("load_scaler() No filename provided")

    # load the previously persisted scaler
    scaler = joblib.load(filename)
    if scaler is None:
        fail("load_scaler() Resulting scaler after load is null!")
    return scaler

#def onnx_infer(filename, torch_input):
#    onnx_input = onnx_program.adapt_torch_inputs_to_onnx(torch_input)
#    print(f"Input length: {len(onnx_input)}")
#    print(f"Sample input: {onnx_input}")
#
#    ort_session = onnxruntime.InferenceSession(filename, providers=['CPUExecutionProvider'])
#
#    def to_numpy(tensor):
#        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
#
#    onnxruntime_input = {k.name: to_numpy(v) for k, v in zip(ort_session.get_inputs(), onnx_input)}
#
#    onnxruntime_outputs = ort_session.run(None, onnxruntime_input)
#    return onnxruntime_outputs

#def onnx_infer2():
#    torch_outputs = model(torch_input)
#    torch_outputs = onnx_program.adapt_torch_outputs_to_onnx(torch_outputs)
#
#    assert len(torch_outputs) == len(onnxruntime_outputs)
#    for torch_output, onnxruntime_output in zip(torch_outputs, onnxruntime_outputs):
#        torch.testing.assert_close(torch_output, torch.tensor(onnxruntime_output))
#
#    print("PyTorch and ONNX Runtime output matched!")
#    print(f"Output length: {len(onnxruntime_outputs)}")
#    print(f"Sample output: {onnxruntime_outputs}")

## define 5-fold cross validation test harness
#kfold = StratifiedKFold(n_splits=5, shuffle=True)
#cv_scores = []
#for train, test in kfold.split(X_train, y_train):
#    model = PitchPredictionModel()
#    acc = model_train(model, X_train[train], y_train[train], X_train[test], y_train[test])
#    print("Accuracy (wide): %.2f" % acc)
#    cv_scores.append(acc)

# evaluate the model
#acc = np.mean(cv_scores)
#std = np.std(cv_scores)
#print("Cross Validation Scores: %.2f%% (+/- %.2f%%)" % (acc*100, std*100))
