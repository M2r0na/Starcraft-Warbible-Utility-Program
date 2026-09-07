from PyQt6.QtWidgets import *
from data.weapons import WEAPONS
from data.monsters import MONSTERS
from core.calculator import *
from core.config import *

class HuntTab(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        form = QFormLayout()

        self.weapon_combo = QComboBox()
        self.weapon_combo.addItems(
            WEAPONS.keys()
        )

        self.upgrade_spin = QSpinBox()
        self.upgrade_spin.setRange(0, 255)

        self.monster_combo = QComboBox()

        for m in MONSTERS:
            self.monster_combo.addItem(
                m["name"]
            )

        self.stim_check = QCheckBox(
            "스팀팩 사용"
        )

        form.addRow(
            "무기",
            self.weapon_combo
        )

        form.addRow(
            "업글",
            self.upgrade_spin
        )

        form.addRow(
            "몬스터",
            self.monster_combo
        )

        form.addRow(
            "",
            self.stim_check
        )

        layout.addLayout(form)

        self.calc_btn = QPushButton(
            "계산"
        )

        self.calc_btn.clicked.connect(
            self.calculate
        )

        layout.addWidget(
            self.calc_btn
        )

        self.result = QTextEdit()
        self.result.setReadOnly(True)

        layout.addWidget(
            self.result
        )

        self.setLayout(layout)

    def calculate(self):

        weapon_name = (
            self.weapon_combo.currentText()
        )

        up = self.upgrade_spin.value()

        monster_name = (
            self.monster_combo.currentText()
        )

        stim = self.stim_check.isChecked()

        base, bonus = WEAPONS[
            weapon_name
        ]

        dmg = damage(
            base,
            bonus,
            up
        )

        monster = next(
            m
            for m in MONSTERS
            if m["name"] == monster_name
        )

        hit_count = hits(
            monster["hp"],
            dmg
        )

        kt = kill_time(
            monster["hp"],
            dmg,
            stim
        )

        exp_h = exp_per_hour(
            monster
        )

        gold_h = gold_per_hour(
            monster
        )
        self.result.setText(
f"""
무기 : {weapon_name}
업글 : +{up}

공격력 : {dmg}

필요 타수 : {hit_count}

처치시간 : {kt:.2f}초

시간당 경험치
{exp_h:,.0f}

시간당 골드
{gold_h:,.0f}
"""
        )