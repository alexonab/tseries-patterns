#
# MIT License
#
# Copyright (c) 2020 Jonathan Shore
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class FeatureSelectByRandomForest:

    def __init__(
        self,
        topk = 25,
        filter = lambda ith,corr: ith < 5 or corr < 0.9,
        maxdepth=15,
        iterations = 10,
        ntrees = 1000):
        """
        Select features using random forest

        :param topk: number of features to return
        :param filter: feature filter based on index and max correlation with prior features
        :param maxdepth: maximum tree depth
        :param iterations: iterations of RF to run
        :param ntrees: number of trees to use
        """
        self.filter = filter
        self.topk = topk
        self.maxdepth = maxdepth
        self.iterations = iterations
        self.ntrees = ntrees


    def evaluate(self, df: pd.DataFrame, labels: pd.Series):
        """
        Determine most relevant features given feature set and labels

        :param df: feature data frame
        :param labels: class labels, 1 for each row
        """
        scores = np.zeros(df.shape[1])
        names = df.columns.values

        for i in range(0, self.iterations):
            print("importance round: %d" % i)
            clf = RandomForestClassifier(n_estimators=self.ntrees, random_state=i * 100 + 1, max_depth=self.maxdepth, n_jobs=-1)
            clf.fit(df, labels)
            scores += clf.feature_importances_

        indices = np.argsort(scores)[::-1]
        features = names[indices]
        importance = scores[indices]

        selected_features = [features[0]]
        selected_importance = [importance[0]]
        for i in range(1, names.shape[0]):
            feature = features[i]
            ith = len(selected_features) + 1
            v = df[feature]
            maxcorr = df[[feature] + selected_features].corr().iloc[1:,0].max()

            if self.filter (ith, maxcorr):
                selected_features.append (feature)
                selected_importance.append (importance[i])

            if len(selected_features) == self.topk:
                break

        self.selected = pd.DataFrame({
            "order": np.arange(len(selected_features)),
            "feature": selected_features,
            "importance": selected_importance }).reset_index(drop=True)

        return self.selected

