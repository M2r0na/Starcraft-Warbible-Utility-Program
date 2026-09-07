from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from core.ranking_scraper import get_rankings
import requests
from bs4 import BeautifulSoup

class RankingTab(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()
        self.search = QLineEdit()
        self.detail = QTextEdit()
        self.table = QTableWidget()
        self.detail.setReadOnly(True)
        self.search.returnPressed.connect(
            self.search_player
        )
        layout.addWidget(self.detail)
        self.search.setPlaceholderText(
            "플레이어 검색..."
        )

        self.search.textChanged.connect(
            self.filter_table
        )

        layout.addWidget(
            self.search
        )
        self.table = QTableWidget()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "순위",
            "플레이어",
            "레벨",
            "범죄",
            "직업",
            "무기",
            "강화"
        ])
        self.table.cellClicked.connect(
            self.show_player_info
        )
        layout.addWidget(
            self.table
        )

        self.setLayout(layout)

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.refresh
        )

        self.timer.start(
            300000
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.refresh()

    def refresh(self):

        rankings = get_rankings()

        self.table.setRowCount(
            len(rankings)
        )

        for row, player in enumerate(rankings):

            self.table.setItem(
                row,0,
                QTableWidgetItem(player["rank"])
            )

            self.table.setItem(
                row,1,
                QTableWidgetItem(player["player"])
            )

            self.table.setItem(
                row,2,
                QTableWidgetItem(player["level"])
            )

            self.table.setItem(
                row,3,
                QTableWidgetItem(player["crime"])
            )

            self.table.setItem(
                row,4,
                QTableWidgetItem(player["job"])
            )

            self.table.setItem(
                row,5,
                QTableWidgetItem(player["weapon"])
            )

            self.table.setItem(
                row,6,
                QTableWidgetItem(player["upgrade"])
            )

    def filter_table(self):

        text = self.search.text().lower()

        for row in range(
            self.table.rowCount()
        ):

            player_item = self.table.item(
                row,
                1
            )

            if player_item is None:
                continue

            player_name = (
                player_item.text()
                .lower()
            )

            visible = (
                text in player_name
            )

            self.table.setRowHidden(
                row,
                not visible
            )
    def show_player_info(self, row, column):

        rank = self.table.item(row, 0).text()
        player = self.table.item(row, 1).text()
        level = self.table.item(row, 2).text()
        crime = self.table.item(row, 3).text()
        job = self.table.item(row, 4).text()
        weapon = self.table.item(row, 5).text()
        upgrade = self.table.item(row, 6).text()

        self.detail.setText(
f"""
닉네임 : {player}

순위 : {rank}

레벨 : {level}

직업 : {job}

무기 : {weapon}

강화 : {upgrade}

범죄도 : {crime}
"""
    )
    def search_player(self):

        text = self.search.text().lower()

        for row in range(self.table.rowCount()):

            item = self.table.item(row, 1)

            if item and text in item.text().lower():

                self.table.selectRow(row)

                self.show_player_info(row, 0)

                break