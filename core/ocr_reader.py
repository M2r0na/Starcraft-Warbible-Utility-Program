# //core/ocr_reader.py
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def read_code(path):
    # 1. 원본 이미지 열기
    img = Image.open(path)
    width, height = img.size

    # 2. 🔥 핵심 패치: 화면 중앙의 세이브 코드 부근만 강제로 잘라내기 (Crop)
    # 보내주신 스크린샷 기준 정중앙 비율을 계산하여 타겟 박스를 잡습니다.
    left = int(width * 0.35)
    top = int(height * 0.30)
    right = int(width * 0.65)
    bottom = int(height * 0.45)
    
    # 설정한 범위로 이미지를 자릅니다 (주변 노이즈 원천 차단)
    cropped_img = img.crop((left, top, right, bottom))
    
    # (선택 사항) 디버깅용: 프로그램이 어디를 잘랐는지 확인하고 싶다면 아래 주석을 해제하세요.
    # cropped_img.save("debug_cropped.png")

    # 3. 테서랙트 세이브 코드 전용 옵션 설정
    # --psm 6: 하나의 단일 텍스트 블록으로 취급
    # 화이트리스트: 영어 대문자와 숫자만 인식하도록 제한
    custom_config = (
        r"--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    # 잘라낸 영역만 OCR 돌리기
    text = pytesseract.image_to_string(
        cropped_img,
        config=custom_config
    )

    # 불필요한 줄바꿈, 공백 제거 후 대문자 통일
    cleaned_text = text.strip().upper().replace(" ", "").replace("\n", "")
    return cleaned_text

def fix_code(text):
    """
    스타크래프트 폰트 특성상 오인하기 쉬운 문자만 선별해서 최종 보정합니다.
    """
    # 텍스트가 여러 줄 섞여 들어왔을 수 있으므로 첫 줄이나 가장 긴 문자열만 취하는 안전장치
    # (중앙만 잘랐으므로 보통 1줄만 들어옵니다)
    lines = [line for line in text.split() if line]
    if lines:
        # 가장 세이브 코드처럼 생긴(보통 가장 긴) 문자열을 선택
        text = max(lines, key=len)

    replace_table = {}

    for old, new in replace_table.items():
        text = text.replace(old, new)

    return text
