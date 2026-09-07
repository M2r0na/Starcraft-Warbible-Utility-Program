import sys
import time
import json
import os
import cv2
import numpy as np
import pydirectinput
import pygetwindow as gw
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect, QPoint, QCoreApplication, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QScreen
from core.ocr_reader import *
pydirectinput.FAILSAFE = False
# ==========================================
# ⚙️ 설정 파일(JSON) 관리 함수 (전역 변수 연동)
# ==========================================
CONFIG_FILE = "config.json"
USER_CROP_RECT = None  # (X, Y, W, H) 좌표 저장용 전역 변수

def load_config():
    """config.json 파일에서 기존에 저장된 좌표를 불러옵니다."""
    global USER_CROP_RECT
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 파일에 좌표 데이터가 있다면 전역 변수에 로드
            if "crop_rect" in data:
                USER_CROP_RECT = tuple(data["crop_rect"])
            return data
    except Exception:
        return {}

def save_config(rect_data):
    """지정한 좌표 데이터를 config.json 파일에 영구 보존합니다."""
    data = {"crop_rect": list(rect_data)}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class ScreenCaptureOverlay(QWidget):
    """화면 전체를 투명하게 덮어 마우스 드래그로 영역을 지정받는 창"""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowOpacity(0.3)
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())
        
        self.start_pos = None
        self.end_pos = None
        self.is_drawing = False

    def paintEvent(self, event):
        if self.is_drawing and self.start_pos and self.end_pos:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(0, 255, 0), 2, Qt.PenStyle.SolidLine))
            rect = QRect(self.start_pos, self.end_pos)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.position().toPoint()
            self.is_drawing = True

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_pos = event.position().toPoint()
            self.is_drawing = False
            
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y())
            w = abs(self.start_pos.x() - self.end_pos.x())
            h = abs(self.start_pos.y() - self.end_pos.y())
            
            if w > 10 and h > 10:
                self.callback(x, y, w, h)
            self.close()


class OCRTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_code = ""
        
        # ✨ 프로그램 실행 시 기존 설정 파일 자동 로드
        load_config()
        
        self.init_ui()

        # ✨ 기존 세이브된 좌표가 있다면 UI 결과창에 즉시 안내하도록 설정
        if USER_CROP_RECT is not None:
            x, y, w, h = USER_CROP_RECT
            self.result.setText(f"💾 기존 저장된 인식 영역을 불러왔습니다!\nX:{x}, Y:{y}, W:{w}, H:{h}\n(재설정을 원하시면 언제든 녹색 버튼을 누르세요.)")

    def init_ui(self):
        layout = QVBoxLayout()

        self.zone_btn = QPushButton("🎯 인식 영역 설정 (스타 창 자동 전환)")
        self.zone_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.zone_btn.clicked.connect(self.start_zone_setting)
        layout.addWidget(self.zone_btn)

        self.select_btn = QPushButton("이미지 선택")
        self.select_btn.clicked.connect(self.select_image)
        layout.addWidget(self.select_btn)

        self.copy_btn = QPushButton("복사")
        self.copy_btn.clicked.connect(self.copy_code)
        layout.addWidget(self.copy_btn)

        self.load_btn = QPushButton("로드 (스타크래프트 직접 타이핑 입력)")
        self.load_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.load_btn.clicked.connect(self.load_code_to_game)
        layout.addWidget(self.load_btn)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)

        # 🎯 이 함수 내용으로 교체해 주세요!
    def start_zone_setting(self):
        self.result.setText("🔍 스타크래프트(Brood War) 창을 찾는 중...")
        QApplication.processEvents()
        
        # 1. 현재 윈도우에 켜진 모든 창 제목 리스트 확보
        all_titles = gw.getAllTitles()
        
        # 2. 스타크래프트와 관련된 창 제목 딱 '하나' 찾기
        target_title = None
        for title in all_titles:
            if 'starcraft' in title.lower() or 'brood war' in title.lower():
                target_title = title  # 리스트가 아니라 순수한 문자열(String)을 저장
                break
        
        # 3. 창을 찾았다면 강제 활성화 시퀀스 작동
        if target_title:
            try:
                # 💡 getWindowsWithTitle은 결과값을 리스트로 주므로 반드시 뒤에 [0]을 붙여야 창 객체가 됩니다!
                star_win = gw.getWindowsWithTitle(target_title)[0]
                
                # 최소화 상태면 정상 크기로 복구
                if star_win.isMinimized:
                    star_win.restore()
                
                # 스타크래프트 창을 화면 맨 앞으로 가져오기 (포커싱)
                star_win.activate()
                self.result.append(f"🎮 '{target_title}' 창을 활성화했습니다.")
                
            except Exception as e:
                self.result.append(f"\n⚠️ 창 제어 중 예외 발생: {e}")
        else:
            self.result.append("\n❌ 켜져 있는 스타크래프트 창을 찾지 못했습니다. 게임을 먼저 실행해 주세요.")
            self.window().showMinimized()

        QApplication.processEvents()
        
        # 스타 화면 전환 및 포커싱이 완전히 안착하도록 0.5초 대기 후 드래그 오버레이 켜기
        QTimer.singleShot(500, self.open_overlay)


    def open_overlay(self):
        self.overlay = ScreenCaptureOverlay(self.save_crop_zone)
        self.overlay.show()

    def save_crop_zone(self, x, y, w, h):
        global USER_CROP_RECT
        USER_CROP_RECT = (x, y, w, h)
        
        # ✨ 사용자가 설정한 좌표를 json 파일로 즉시 세이브 보존
        save_config(USER_CROP_RECT)
        
        self.window().showNormal()
        self.window().activateWindow()
        self.result.setText(f"✅ 영역 설정 완료 및 파일 저장 완료!\nX:{x}, Y:{y}, W:{w}, H:{h}\n\n'이미지 선택' 후 '로드' 버튼을 누르세요.")

    def select_image(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not file:
            return

        if USER_CROP_RECT is not None:
            try:
                img = Image.open(file)
                x, y, w, h = USER_CROP_RECT
                cropped_img = img.crop((x, y, x + w, y + h))
                
                opencv_img = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)
                
                # 초정밀 가공 1단계: 해상도 3배 뻥튀기 확장
                opencv_img = cv2.resize(opencv_img, (0, 0), fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
                
                # 초정밀 가공 2단계: HSV 변환 및 초록색 마스크
                hsv = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2HSV)
                
                # 스타크래프트 연두색 글자 검출 마스크
                lower_green = np.array([35, 50, 100])
                upper_green = np.array([85, 255, 255])
                mask = cv2.inRange(hsv, lower_green, upper_green)
                
                # 초정밀 가공 3단계: 글자 마디 벌어짐 방지용 팽창 필터
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                mask = cv2.dilate(mask, kernel, iterations=1)
                
                # 초정밀 가공 4단계: 흑백 이진화 및 가우시안 블러 스무딩
                _, binary_img = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
                binary_img = cv2.GaussianBlur(binary_img, (3, 3), 0)
                _, binary_img = cv2.threshold(binary_img, 127, 255, cv2.THRESH_BINARY)
                
                # 초정밀 가공 5단계: 흰바탕 검은글씨 완성 (인식률 Max 상태)
                final_ocr_input = cv2.bitwise_not(binary_img)
                final_processed_img = Image.fromarray(final_ocr_input)

                custom_config = r"--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                code = pytesseract.image_to_string(final_processed_img, config=custom_config).strip().upper().replace(" ", "").replace("\n", "")
            except Exception as e:
                self.result.setText(f"❌ 초정밀 전처리 중 오류 발생: {e}")
                return
        else:
            code = read_code(file)

        fixed = fix_code(code)
        self.current_code = fixed
        self.result.setText(f"OCR 결과\n\n{code}\n\n보정 결과\n\n{fixed}")

    def copy_code(self):
        if not self.current_code:
            return
        QApplication.clipboard().setText(self.current_code)

    def load_code_to_game(self):
        if not self.current_code:
            return
        
        self.result.append("\n⏱️ 3초 뒤 코드 입력을 시작합니다. 스타크래프트 화면을 확인하세요!")
        QCoreApplication.processEvents()
        
        time.sleep(3)

        for char in self.current_code:
            char_lower = char.lower()

            pydirectinput.keyDown(char_lower)
            pydirectinput.keyUp(char_lower) 

        pydirectinput.keyDown('enter')
        pydirectinput.keyUp('enter')
        pydirectinput.keyDown('enter')
        pydirectinput.keyUp('enter')
        
        self.result.append("✅ 로드 완료!")
