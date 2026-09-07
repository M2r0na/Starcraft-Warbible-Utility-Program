from PyQt6.QtWidgets import *
import pandas as pd
from data.monsters import MONSTERS
from core.calculator import exp_per_hour
import math
from core.config import *


class LevelTab(QWidget):

    def __init__(self):

        super().__init__()

        self.df = pd.read_csv(
            "data/diablo_2000_exp_table.csv"
        )
        self.boss_df = pd.read_csv(
            "data/boss_run_data.csv",
            sep="\t"
        )

        self.boss_df = self.boss_df.iloc[1:].reset_index(drop=True)
        layout = QVBoxLayout()

        self.current_level = QSpinBox()
        self.current_level.setRange(
            1,
            2000
        )

        self.target_level = QSpinBox()
        self.target_level.setRange(
            1,
            2000
        )

        self.target_level.setValue(
            2000
        )

        self.mode = QComboBox()

        self.mode.addItems([
            "사냥",
            "보스"
        ])
        self.boss_combo = QComboBox()

        for boss in self.boss_df["Boss"]:
            self.boss_combo.addItem(
                boss
            )
        self.run_spin = QSpinBox()

        self.run_spin.setRange(
            1,
            13
        )
        self.monster_combo = QComboBox()

        for m in MONSTERS:
            self.monster_combo.addItem(
                m["name"]
            )
        form = QFormLayout()

        form.addRow(
            "현재 레벨",
            self.current_level
        )

        form.addRow(
            "목표 레벨",
            self.target_level
        )

        form.addRow(
            "계산 방식",
            self.mode
        )

        form.addRow(
            "기준 몬스터",
            self.monster_combo
        )
        form.addRow(
            "보스",
            self.boss_combo
        )

        form.addRow(
            "런",
            self.run_spin
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

        cur = self.current_level.value()
        tar = self.target_level.value()

        mode = self.mode.currentText()
        remain_level = tar - cur

        cur_exp = int(
            self.df[
                self.df["Level"] == cur
            ]["Cumulative_EXP"].iloc[0]
        )

        tar_exp = int(
            self.df[
                self.df["Level"] == tar
            ]["Cumulative_EXP"].iloc[0]
        )

        remain = tar_exp - cur_exp

        # -----------------------
        # 사냥 모드
        # -----------------------

        if mode == "사냥":

            monster_name = (
                self.monster_combo.currentText()
            )

            monster = next(
                m for m in MONSTERS
                if m["name"] == monster_name
            )

            exp_hour = exp_per_hour(
                monster
            )

            hours = remain / exp_hour
            days = hours / 24

            self.output.setText(
    f"""
    사냥 계산

    현재 레벨
    {cur}

    목표 레벨
    {tar}

    현재 누적 경험치
    {cur_exp:,}

    목표 누적 경험치
    {tar_exp:,}

    필요 경험치
    {remain:,}

    기준 몬스터
    {monster_name}

    경험치/시간
    {exp_hour:,.0f}

    남은 레벨
    {remain_level}

    예상 사냥시간
    {hours:,.1f} 시간

    예상 일수
    {days:,.1f} 일
    """
            )

        # -----------------------
        # 보스 모드
        # -----------------------

        else:

            boss = self.boss_combo.currentText()
        
            run = self.run_spin.value()

            row = self.boss_df[
                self.boss_df["Boss"] == boss
            ].iloc[0]

            exp_col = (run * 2) - 1

            boss_exp = int(
                str(
                    row.iloc[exp_col]
                ).replace(",", "")
            )

            need_count = math.ceil(
                remain / boss_exp
            )

            self.output.setText(
f"""
보스런 계산

현재 레벨
{cur}

목표 레벨
{tar}

현재 누적 경험치
{cur_exp:,}

목표 누적 경험치
{tar_exp:,}

필요 경험치
{remain:,}

보스
{boss}

런
{run}

1회 경험치
{boss_exp:,}

필요 보스런 횟수
{need_count:,.0f} 회
"""
            )