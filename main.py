from PyQt6.QtWidgets import *

from ui.ranking_tab import RankingTab
from ui.hunt_tab import HuntTab
from ui.boss_tab import BossTab
from ui.level_tab import LevelTab
from ui.ocr_tab import OCRTab
import sys
import os
import pandas as pd

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
app = QApplication(sys.argv)

window = QMainWindow()

window.setWindowTitle(
    "CR Helper"
)

window.resize(
    1400,
    900
)

tabs = QTabWidget()

tabs.addTab(
    RankingTab(),
    "순위표"
)

tabs.addTab(
    HuntTab(),
    "사냥 계산기"
)

tabs.addTab(
    BossTab(),
    "보스런 계산기"
)

tabs.addTab(
    LevelTab(),
    "레벨 계산기"
)

tabs.addTab(
    OCRTab(),
    "로드코드 OCR"
)

window.setCentralWidget(
    tabs
)

window.show()

sys.exit(
    app.exec()
)