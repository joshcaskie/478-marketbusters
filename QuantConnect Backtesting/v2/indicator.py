#region imports
from AlgorithmImports import *
#endregion
from collections import deque

# Custom Corrma Indicator
class CustomCorrelationMovingAverage(PythonIndicator):
    import pandas as pd

    def __init__(self, name, period):
        self.Name = name 
        # self.WarmUpPeriod = period * 2             # How long to initialize
        # This WarmUpPeriod pumps in data from BEFORE the start of the algorithm... Am I worried about that?
        self.Time = datetime.min                # Initial value
        self.Value = 0.0                        # Initial value
        self.ind_queue = deque(maxlen=period)   # I think this sets the max # of data rows the indicator can store
        self.dep_queue = deque(maxlen=period)

        self.myupdate = False

    def __repr__(self):
        return f"{self.Name} -> IsReady: {self.IsReady}. Time: {self.Time}. Value: {self.Value}. Ind Queue (Len vs. Max): ({len(self.ind_queue)}, {self.ind_queue.maxlen}). Dep Queue (Len vs. Max): ({len(self.dep_queue)}, {self.dep_queue.maxlen})"

    @property
    def IsReady(self) -> bool:
        return len(self.ind_queue) == self.ind_queue.maxlen and len(self.dep_queue) == self.dep_queue.maxlen

    def Update(self, input: BaseData, ind_bar: bool) -> bool:
        if input == None:
            return True

        if ind_bar:
            self.ind_queue.append(input.Value)
        else:
            self.dep_queue.append(input.Value)

        self.Time = input.Time 

        if self.IsReady:
            self.Value = pd.DataFrame({'col1': self.ind_queue, 'col2': self.dep_queue}).corr().iloc[0].iloc[1]

        # Supposed to "Show when indicator IsReady", but I think it's broken.
        # return len(self.ind_queue) == self.ind_queue.maxlen and len(self.dep_queue) == self.dep_queue.maxlen

        # Trying
        return self.IsReady
