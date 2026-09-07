import pandas as pd

class LevelSystem:

    def __init__(self):
        self.df = pd.read_csv(
            "data/diablo_2000_exp_table.csv"
        )

    def level_from_exp(self, exp):

        row = self.df[
            self.df["Cumulative_EXP"] <= exp
        ]

        return int(
            row.iloc[-1]["Level"]
        )

    def target_exp(
        self,
        current_exp,
        target_level
    ):

        target = int(
            self.df[
                self.df["Level"] == target_level
            ]["Cumulative_EXP"].iloc[0]
        )

        return max(
            0,
            target - current_exp
        )