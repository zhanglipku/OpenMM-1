#!/usr/bin/env python

""" This is module for performing different multimodal fusion experiments """
import pandas
import numpy as np
from collections import Counter
from sklearn import svm
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import Imputer
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample

def early_fusion(multimodal_files):
    """
    This function fuses unimodal data files into one multimodal csv file
    :param multimodal_files: a list of unimodal csv files
    :param write2file: file name to write data to
    :return: mm_names, mm_feats
        WHERE
        list mm_names is the feature names
        list mm_feats is a list of feature lists
    """
    # Statistics we will use to combine features at the frame/sentence level to the participant level
    # stats_names = ['max', 'min', 'mean', 'median', 'std']
    stats_names = ['mean']
    mm_feats = []
    mm_names = []
    # Process each unimodal data file
    print('Processing unimodal files...\n')
    for feat_file in multimodal_files:
        df = pandas.read_csv(feat_file, header='infer')
        feature_names = df.columns.values
        for feat in feature_names:
            # Feature vector
            vals = df[feat].values
            # Run statistics
            maximum = np.nanmax(vals)
            minimum = np.nanmin(vals)
            mean = np.nanmean(vals)
            median = np.nanmedian(vals)
            std = np.nanstd(vals)
            names = [feat.strip() + "_" + stat for stat in stats_names]
            # feats = [maximum, minimum, mean, median, std]
            feats = [mean]
            for n in names:
                mm_names.append(n)
            for f in feats:
                mm_feats.append(f)
    print('Done combining modalities!\n')
    return mm_names, mm_feats


def handle_nans(data):
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(data)
    return imp.transform(data)


def add_pca(n, train_features, test_features):
    """
    :param features: matrix like list where each item in list is a list of features
    :return: pca_features
        WHERE
        list pca_features is a matrix like list where each item is a reduced list of features
    """
    train = handle_nans(train_features)
    test = handle_nans(test_features)
    pca = PCA(n_components=n)
    train_pca_features = pca.fit_transform(train)
    test_pca_features = pca.transform(test)
    return train_pca_features, test_pca_features


def predict_regression(train_data, test_data, train_labels, test_labels):
    """
    This function predicts depression score using an SVM regression algorithm (SVR - http://scikit-learn.org/stable/modules/svm.html#regression)

    :param train_data: list of feature lists for training data
    :param train_labels: list of depression score labels for training data
    :param test_data: list of feature lists for test data
    :param test_labels: list of depression score labels for test data
    :return: MAE, RMSE
        WHERE
        float MAE is mean absolute error
        float RMSE is root mean square error
    """
    # Handle missing data in train
    # missing_values is the value of your placeholder, strategy is if you'd like mean, median or mode, and axis=0 means it calculates the imputation based on the other feature values for that sample
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(train_data)
    train_imp = imp.transform(train_data)

    # Handle missing data in dev
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(test_data)
    test_imp = imp.transform(test_data)

    clf = svm.SVR()
    clf.fit(train_imp, train_labels)
    predictions = clf.predict(test_imp)
    MAE = mean_absolute_error(predictions, test_labels)
    RMSE = mean_squared_error(predictions, test_labels) ** 0.5
    return MAE, RMSE


def predict_class(train_data, test_data, train_labels, test_labels):
    """
    This function predicts depression class (depressed/not depressed) using an SVM classification algorithm (SVC - http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC )

    :param train_data: list of feature lists for training data
    :param train_labels: list of depression (binary) class labels for training data
    :param test_data: list of feature lists for test data
    :param test_labels: list of depression (binary) class labels for test data
    :return: accuracy
        WHERE
        float accuracy is the percentage of correct predictions
    """
    # Handle missing data in train
    # missing_values is the value of your placeholder, strategy is if you'd like mean, median or mode, and axis=0 means it calculates the imputation based on the other feature values for that sample
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(train_data)
    train_imp = imp.transform(train_data)

    # Handle missing data in dev
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(test_data)
    test_imp = imp.transform(test_data)

    clf = svm.SVC(class_weight="balanced")
    clf.fit(train_imp, train_labels)
    predictions = clf.predict(test_imp)
    accuracy = accuracy_score(test_labels, predictions)
    print(classification_report(test_labels, predictions))
    print(confusion_matrix(test_labels, predictions))
    tn, fp, fn, tp = confusion_matrix(test_labels, predictions).ravel()
    print('True negative', tn, "False positive", fp, "False negative", fn, "True positive", tp)
    return accuracy


def predict_class_forest(train_data, test_data, train_labels, test_labels):
    """
    This function predicts depression class (depressed/not depressed) using an SVM classification algorithm (SVC - http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC )

    :param train_data: list of feature lists for training data
    :param train_labels: list of depression (binary) class labels for training data
    :param test_data: list of feature lists for test data
    :param test_labels: list of depression (binary) class labels for test data
    :return: accuracy
        WHERE
        float accuracy is the percentage of correct predictions
    """
    # Handle missing data in train
    # missing_values is the value of your placeholder, strategy is if you'd like mean, median or mode, and axis=0 means it calculates the imputation based on the other feature values for that sample
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(train_data)
    train_imp = imp.transform(train_data)

    # Handle missing data in dev
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(test_data)
    test_imp = imp.transform(test_data)

    clf = RandomForestClassifier(max_depth=2, random_state=0)
    clf.fit(train_imp, train_labels)
    predictions = clf.predict(test_imp)
    accuracy = accuracy_score(test_labels, predictions)
    print(classification_report(test_labels, predictions))
    print(confusion_matrix(test_labels, predictions))
    tn, fp, fn, tp = confusion_matrix(test_labels, predictions).ravel()
    print('True negative', tn, "False positive", fp, "False negative", fn, "True positive", tp)
    return accuracy


def predict_class_majorityvote(model1, model2, model3, train_labels, test_labels):
    """
    This function predicts depression class (depressed/not depressed) using an SVM classification algorithm (SVC - http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC )

    :param train_data: list of feature lists for training data
    :param train_labels: list of depression (binary) class labels for training data
    :param test_data: list of feature lists for test data
    :param test_labels: list of depression (binary) class labels for test data
    :return: accuracy
        WHERE
        float accuracy is the percentage of correct predictions
    """
    prediction_matrix = []
    for i, model in enumerate([model1, model2, model3]):
        i += 1
        train_data = model[0]
        test_data = model[1]
        # Handle nans
        train = handle_nans(train_data)
        test = handle_nans(test_data)
        # Create svm and fit model
        clf = svm.SVC(class_weight='balanced')
        clf.fit(train, train_labels)
        # Make predictions for each model
        preds = clf.predict(test)
        prediction_matrix.append(preds)
    matrix = pandas.DataFrame(prediction_matrix)
    vote_preds = []
    # For each instance find the majority class label
    for column in matrix:
        labels = matrix[column].values
        # Find majority
        count = Counter(labels)
        # Majority vote is the ultimate prediction
        majority_vote = count.most_common()[0][0]
        vote_preds.append(majority_vote)
    # Determine late fusion results
    accuracy = accuracy_score(test_labels, vote_preds)
    print(classification_report(test_labels, vote_preds))
    print(confusion_matrix(test_labels, vote_preds))
    tn, fp, fn, tp = confusion_matrix(test_labels, vote_preds).ravel()
    print('True negative', tn, "False positive", fp, "False negative", fn, "True positive", tp)
    print(accuracy)


def late_fusion_average(model1, model2, model3, train_labels, test_labels):
    """
    This function predicts depression score by using a late fusion approach of three different models
    :param model1: a tuple of model 1's feature lists for train and dev set, format: (train_features, test_features)
    :param model2: a tuple of model 2's feature lists for train and dev set, format: (train_features, test_features)
    :param model3: a tuple of model 3's feature lists for train and dev set, format: (train_features, test_features)
    :param train_labels: a list of labels
    :param test_labels: a list of labels
    :return: MAE, RMSE
        WHERE
        float MAE is mean absolute error
        float RMSE is root mean square error
    """
    # Handle missing data in train
    prediction_matrix = []
    for i, model in enumerate([model1, model2, model3]):
        i += 1
        train_data = model[0]
        test_data = model[1]
        imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
        imp.fit(train_data)
        train_imp = imp.transform(train_data)

        # Handle missing data in dev
        imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
        imp.fit(test_data)
        test_imp = imp.transform(test_data)

        clf = svm.SVR()
        clf.fit(train_imp, train_labels)
        predictions = clf.predict(test_imp)
        prediction_matrix.append(predictions)
    # TODO - average decisions?
    late_predictions = np.mean(prediction_matrix, axis=0)
    MAE = mean_absolute_error(late_predictions, test_labels)
    RMSE = mean_squared_error(late_predictions, test_labels) ** 0.5
    print MAE, RMSE


def upsample_data(train_data, train_labels, headers, test_data, test_labels):
    """Upsample training data to have balanced classes"""
    df = pandas.DataFrame(train_data, columns=headers)
    print(df.isnull().values.any())
    df.fillna(df.mean())
    print(df.isnull().values.any())
    df['label'] = train_labels

    # Separate majority and minority classes
    df_majority = df[df.label == 0]
    df_minority = df[df.label == 1]

    # Upsample minority class
    df_minority_upsampled = resample(df_minority,
                                     replace=True,  # sample with replacement
                                     n_samples= df_majority.shape[0],  # to match majority class
                                     random_state=123)  # reproducible results

    # Combine majority class with upsampled minority class
    df_upsampled = pandas.concat([df_majority, df_minority_upsampled])

    # Display new class counts
    # print df_upsampled.label.value_counts()
    # print df_upsampled.label.values

    # Separate input features (X) and target variable (y)
    y = df_upsampled.label
    X = df_upsampled.drop('label', axis=1)
    test = pandas.DataFrame(test_data, columns=headers)

    clf = svm.SVC()
    clf.fit(X, y)
    preds = clf.predict(test)
    print(accuracy_score(preds, test_labels))
    print(classification_report(preds, test_labels))
    print(confusion_matrix(preds, test_labels))
    # return X, y

def optimize_c(train_data, test_data, train_labels, test_labels):
    # Test out different C parameter values (10^-5 to 10^5)

    # Handle missing data in train
    train = handle_nans(train_data)
    test = handle_nans(test_data)

    results = []
    for x in range(-5, 5):
        print "----------------------------------------"
        C = 10 ** x
        print "C-paramter", C
        clf = svm.SVC(C=C, class_weight="balanced")
        clf.fit(train, train_labels)
        predictions = clf.predict(test)
        accuracy = accuracy_score(test_labels, predictions)
        print(classification_report(test_labels, predictions))
        print(confusion_matrix(test_labels, predictions))
        tn, fp, fn, tp = confusion_matrix(test_labels, predictions).ravel()
        print('True negative', tn, "False positive", fp, "False negative", fn, "True positive", tp)
        print accuracy
        print "----------------------------------------\n"

# def hybrid():
# def trees():
# TODO: create hybrid approach
# TODO: try CART decision tree algorithm
# TODO: try trees algorithm, which handles unbalanced data better
