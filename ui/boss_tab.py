from PyQt6.QtWidgets import *
import pandas as pd
import math

class BossTab(QWidget):

    def __init__(self):

        super().__init__()
        self.level_df = pd.read_csv(
            "data/diablo_2000_exp_table.csv"
        )
        self.df = pd.read_csv(
            "data/boss_run_data.csv",
            sep="\t"
        )
        # 첫 번째 행(EXP/돈 행) 제거
        self.df = self.df.iloc[1:].reset_index(drop=True)

        layout = QVBoxLayout()

        self.boss_combo = QComboBox()

        bosses = self.df["Boss"].unique()

        for boss in bosses:
            self.boss_combo.addItem(
                boss
            )
        self.current_level = QSpinBox()
        self.current_level.setRange(1, 2000)

        self.target_level = QSpinBox()
        self.target_level.setRange(1, 2000)
        self.target_level.setValue(2000)

        self.run_spin = QSpinBox()
        self.run_spin.setRange(1,13)

        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(
            1,1000000
        )

        form = QFormLayout()

        form.addRow(
            "Boss",
            self.boss_combo
        )

        form.addRow(
            "Run (max: 13)",
            self.run_spin
        )

        form.addRow(
            "횟수",
            self.repeat_spin
        )

        form.addRow(
            "현재 레벨",
            self.current_level
        )

        form.addRow(
            "목표 레벨",
            self.target_level
        )

        layout.addLayout(form)

        self.btn = QPushButton(
            "계산"
        )

        self.btn.clicked.connect(
            self.calculate
        )

        layout.addWidget(
            self.btn
        )

        self.output = QTextEdit()

        layout.addWidget(
            self.output
        )
        self.setLayout(layout)

    def calculate(self):

        boss = self.boss_combo.currentText()
        run = self.run_spin.value()
        cnt = self.repeat_spin.value()

        row = self.df[
            self.df["Boss"] == boss
        ].iloc[0]
        print(row)
        exp_col = (run * 2) - 1
        gold_col = run * 2

        exp = str(
            row.iloc[exp_col]
        ).replace(",", "")

        gold = str(
            row.iloc[gold_col]
        ).replace(",", "")

        exp = int(exp)
        gold = int(gold)
        cur_level = self.current_level.value()
        target_level = self.target_level.value()

        cur_exp = int(
            self.level_df[
                self.level_df["Level"] == cur_level
            ]["Cumulative_EXP"].iloc[0]
        )

        target_exp = int(
            self.level_df[
                self.level_df["Level"] == target_level
            ]["Cumulative_EXP"].iloc[0]
        )

        remain_exp = target_exp - cur_exp
        total_exp = exp * cnt
        total_gold = gold * cnt
        need_count = math.ceil(
            remain_exp / exp
        )
        self.output.setText(
f"""
보스 : {boss}

런 : {run}

횟수 : {cnt:,}

현재 레벨
{cur_level}

목표 레벨
{target_level}

필요 경험치
{remain_exp:,}

필요 보스런
{need_count:,} 회

1회 경험치
{exp:,}

1회 골드
{gold:,}

총 경험치
{total_exp:,}

총 골드
{total_gold:,}
"""
    )