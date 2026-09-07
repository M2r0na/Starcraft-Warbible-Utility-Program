import pandas as pd

class BossCalculator:

    def __init__(self):

        self.df = pd.read_csv(
            "data/boss_run_data.csv"
        )

    def calculate(
        self,
        boss_name,
        run_count,
        repeat
    ):

        row = self.df[
            self.df["Boss"] == boss_name
        ].iloc[0]

        exp = row[f"Run{run_count}_EXP"]
        gold = row[f"Run{run_count}_GOLD"]

        return {
            "exp": exp * repeat,
            "gold": gold * repeat
        }