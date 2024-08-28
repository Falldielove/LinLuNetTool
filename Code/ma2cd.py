import xml.etree.ElementTree as ET
import os
import shutil
import subprocess
from colorama import init, Fore
import re  # 添加這行來導入 re 模組
import sys

# 獲取臨時目錄路徑
if getattr(sys, 'frozen', False):
    # 如果是打包後的可執行文件
    application_path = sys._MEIPASS
else:
    # 如果是直接運行的腳本
    application_path = os.path.dirname(os.path.abspath(__file__))

# 將模塊路徑添加到系統路徑
sys.path.append(application_path)

# 現在可以導入模塊
import ma2_converter
import image_processor

# 初始化 colorama
init()
LIGHT_PURPLE = Fore.LIGHTMAGENTA_EX
GRAY = Fore.LIGHTBLACK_EX
WHITE = Fore.WHITE
GREEN = Fore.GREEN
LIGHT_YELLOW = Fore.LIGHTYELLOW_EX

# 常量定義
TEMPLATE_PATH = 'Input/music_template.xml'
OUTPUT_DIRECTORY = 'Output'
DIFFICULTY_OPTIONS = ['BASIC', 'ADVANCED', 'EXPERT', 'MASTER', 'RE:MASTER']
DIFFICULTY_CODES = ['00', '01', '02', '03', '04']

# 新增函數：從 maidata.txt 提取信息
def extract_info_from_maidata(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正則表達式提取信息
        title = re.search(r'&title=(.+?)(?:\n|$)', content)
        artist = re.search(r'&artist=(.+?)(?:\n|$)', content)
        des = re.search(r'&des=(.+?)(?:\n|$)', content)
        
        # 尋找 BPM
        bpm_match = re.search(r'&inote_\d+=\((\d+)\)', content)
        
        # 尋找難度等級
        level_match = re.search(r'&lv_\d+=(\d+)(\+?)', content)

        # 提取並處理等級信息
        if level_match:
            level_value = int(level_match.group(1))  # 基礎等級值
            level_decimal = 7 if level_match.group(2) == '+' else 0  # 若有 "+"，設置小數部分為7，否則為0
        else:
            level_value = 0
            level_decimal = 0

        return {
            'song_name': title.group(1) if title else '',
            'artist_name': artist.group(1) if artist else '',
            'notes_designer': des.group(1) if des else '',
            'bpm': int(bpm_match.group(1)) if bpm_match else 0,
            'level': level_value,
            'level_decimal': level_decimal
        }
    except Exception as e:
        print(f"讀取 maidata.txt 時發生錯誤：{e}")
        return {
            'song_name': '',
            'artist_name': '',
            'notes_designer': '',
            'bpm': 0,
            'level': 0,
            'level_decimal': 0
        }


def show_welcome_message():
    ascii_art = r"""
 _       _         _              _____  __   __  _   _  ______  _______
| |     (_)       | |            |  __ \ \ \ / / | \ | ||  ____||__   __|
| |      _  _ __  | |      _   _ | |  | | \ V /  |  \| || |__      | |
| |     | || '_ \ | |     | | | || |  | |  > <   | . ` ||  __|     | |
| |____ | || | | || |____ | |_| || |__| | / . \  | |\  || |____    | |
|______||_||_| |_||______| \__,_||_____/ /_/ \_\ |_| \_||______|   |_|    Ver - 1.6
    """
    print(LIGHT_PURPLE + ascii_art)
    print(LIGHT_PURPLE + "Welcome to LinLuDX Tool-MaXmlcd! Ver.1.5\n")
    print(WHITE + "十分建議將此視窗最大化！！")
    print(WHITE + "歡迎使用 凜 漉 工 具 箱 - MaXmlcd生成器！")
    print('')

def prettify_xml_element(element, level=0):
    i = "\n" + level * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + "  "
        if not element.tail or not element.tail.strip():
            element.tail = i
        for sub_element in element:
            prettify_xml_element(sub_element, level+1)
        if not element.tail or not element.tail.strip():
            element.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i

def calculate_music_level_id(level, level_decimal):
    base_music_level_id = 21 - (14 - level) * 2
    return base_music_level_id + (1 if level_decimal >= 7 else 0)

def modify_xml(file_path, music_data):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # 更新 XML 元素
    for elem in root.iter():
        if elem.tag == 'dataName':
            elem.text = f'music{music_data["music_id"]}'
        elif elem.tag == 'name':
            elem.find('str').text = music_data['song_name']
            elem.find('id').text = music_data['music_id'][-5:]
        elif elem.tag == 'sortName':
            elem.text = music_data['song_name'].replace(" ", "").upper()
        elif elem.tag == 'artistName':
            elem.find('str').text = music_data['artist_name']
        elif elem.tag == 'bpm':
            elem.text = str(music_data['bpm'])

    # 更新 Notes 元素
    for notes_elem in root.findall('.//Notes'):
        file_path_elem = notes_elem.find('.//file/path')
        if file_path_elem is not None and file_path_elem.text.endswith(f"_{music_data['difficulty_code']}.ma2"):
            notes_elem.find('.//level').text = str(music_data['level'])
            notes_elem.find('.//levelDecimal').text = str(music_data['level_decimal'])
            notes_elem.find('.//maxNotes').text = str(music_data['max_notes'])
            notes_elem.find('.//notesDesigner/id').text = '998'
            notes_elem.find('.//notesDesigner/str').text = music_data['notes_designer']
            notes_elem.find('.//isEnable').text = 'true'
            notes_elem.find('.//musicLevelID').text = str(calculate_music_level_id(music_data['level'], music_data['level_decimal']))
            file_path_elem.text = f"{music_data['music_id']}_{music_data['difficulty_code']}.ma2"
            break

    # 更新 movieName 和 cueName
    movie_name_elem = root.find('.//movieName')
    cue_name_elem = root.find('.//cueName')

    if movie_name_elem is not None:
        movie_name_elem.find('id').text = music_data['music_id'][-4:]  # 使用 music_id 的最後四位
        movie_name_elem.find('str').text = music_data['song_name']  # 使用乐曲名称

    if cue_name_elem is not None:
        cue_name_elem.find('id').text = music_data['music_id'][-4:]  # 使用 music_id 的最後四位
        cue_name_elem.find('str').text = music_data['song_name']  # 使用乐曲名称

    prettify_xml_element(root)

    xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
    ET.register_namespace('', "http://www.w3.org/2001/XMLSchema-instance")
    ET.register_namespace('', "http://www.w3.org/2001/XMLSchema")

    xml_string = ET.tostring(root, encoding='unicode')
    xml_string_with_declaration = xml_declaration + xml_string

    with open(file_path, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_string_with_declaration)

def ensure_directories_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 修改 get_user_input 函數以支持自動提取信息
def get_user_input():
    print(LIGHT_YELLOW + '------------------------------------------------------------------------------------------------------')
    print(GRAY)

    while True:
        try:
            folder_path = input('請輸入包含 maidata.txt 的資料夾路徑（或按 Enter 使用手動輸入）: ').strip()
            
            if folder_path:
                # 使用資料夾名稱作為 music_id
                music_id = os.path.basename(folder_path)
                if not music_id.isdigit() or len(music_id) < 5:
                    raise ValueError("資料夾名稱必須是至少 5 位的數字")

                maidata_path = os.path.join(folder_path, 'maidata.txt')
                if not os.path.exists(maidata_path):
                    raise FileNotFoundError(f"在 {folder_path} 中找不到 maidata.txt")

                # 從 maidata.txt 提取信息
                info = extract_info_from_maidata(maidata_path)
                
                # 使用提取的信息，但允許用戶修改
                song_name = input(f'\n請確認歌曲名稱 （預設：{info["song_name"]}）: ') or info['song_name']
                artist_name = input(f'\n請確認歌曲製作者名稱 （預設：{info["artist_name"]}）: ') or info['artist_name']
                bpm = int(input(f'\n請確認 BPM （預設：{info["bpm"]}）: ') or info['bpm'])
                notes_designer = input(f'\n請確認譜師名稱 （預設：{info["notes_designer"]}）: ') or info['notes_designer']
                level = int(input(f'\n請確認等級 （預設：{info["level"]}）: ') or info['level'])
                level_decimal = int(input(f'\n請確認定數等級 （預設：{info["level_decimal"]}）: ') or info['level_decimal'])

            else:
                # 手動輸入模式
                music_id = input('請輸入 musicID （至少5位數字 例：011619）: ')
                if len(music_id) < 5 or not music_id.isdigit():
                    raise ValueError("musicID 必須至少包含 5 位數字")

                song_name = input('\n請輸入歌曲名稱: ')
                artist_name = input('\n請輸入歌曲製作者名稱: ')
                bpm = int(input('\n請輸入 BPM: '))
                notes_designer = input('\n請輸入譜師名稱: ')
                level = int(input('\n請輸入等級（例：14 - 不須填入+）: '))
                level_decimal = int(input('\n請輸入定數等級（例：14.7 的 7）: '))

            # 在 get_user_input 函數中修改這部分
            max_notes = input('\n請輸入譜面音符數量: ').strip()
            max_notes = int(max_notes) if max_notes else 0

            print(' ')
            for i, option in enumerate(DIFFICULTY_OPTIONS):
                print(f"[{i}] {option}")
            difficulty_index = int(input('請選擇譜面難度: '))
            if not 0 <= difficulty_index < len(DIFFICULTY_OPTIONS):
                raise ValueError("無效的難度選擇")

            difficulty_code = DIFFICULTY_CODES[difficulty_index]
            return {
                'music_id': music_id,
                'song_name': song_name,
                'artist_name': artist_name,
                'bpm': bpm,
                'notes_designer': notes_designer,
                'level': level,
                'level_decimal': level_decimal,
                'max_notes': max_notes,
                'difficulty_code': difficulty_code
            }

        except ValueError as e:
            print(f"輸入錯誤：{e}。請重新輸入。")
        except FileNotFoundError as e:
            print(f"錯誤：{e}。請重新輸入。")
        except Exception as e:
            print(f"發生錯誤：{e}。請重新輸入。")

def copy_and_modify_xml(template_path, output_directory, music_data):
    ensure_directories_exist(output_directory)
    
    output_file_name = f"Music_{music_data['music_id']}.xml"
    output_file_path = os.path.join(output_directory, output_file_name)
    
    shutil.copy(template_path, output_file_path)
    
    modify_xml(output_file_path, music_data)
    print(GREEN + f"成功生成 XML 文件：{output_file_path}")

def main():
    show_welcome_message()

    use_tool = input(LIGHT_YELLOW + '是否要執行 譜面註冊表生成工具？ 如果不執行將會直接轉至ma2文件轉換工具 (Y/N): ').strip().lower()
    if use_tool == 'n':
        print('')
        print(GREEN + '正在前往 ma2 譜面轉換器...')
        subprocess.run(["python", "ma2_converter.py"])
        return
    elif use_tool != 'y':
        print('')
        print('無效的輸入，請重新執行程序。')
        return

    print(GREEN + '開始執行XML轉換程式！...')
    print('')

    music_data = get_user_input()

    copy_and_modify_xml(TEMPLATE_PATH, OUTPUT_DIRECTORY, music_data)
    
    print(GREEN + "XML 生成完成，正在啟動 ma2 譜面轉換器...")
    subprocess.run(["python", "ma2_converter.py"])

if __name__ == "__main__":
    main()
