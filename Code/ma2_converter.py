import os
import subprocess
from colorama import init, Fore, Style
import re

# 初始化 colorama
init(autoreset=True)

# 定義顏色變數為全域變數
LIGHT_PURPLE = Fore.LIGHTMAGENTA_EX
WHITE = Fore.WHITE
GREY = Fore.LIGHTBLACK_EX
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW

def welcome():
    # 顯示 ASCII 藝術文字和歡迎訊息
    ascii_art = r"""
 _       _         _              _____  __   __  _   _  ______  _______
| |     (_)       | |            |  __ \ \ \ / / | \ | ||  ____||__   __|
| |      _  _ __  | |      _   _ | |  | | \ V /  |  \| || |__      | |
| |     | || '_ \ | |     | | | || |  | |  > <   | . ` ||  __|     | |
| |____ | || | | || |____ | |_| || |__| | / . \  | |\  || |____    | |
|______||_||_| |_||______| \__,_||_____/ /_/ \_\ |_| \_||______|   |_|    Ver - 1.6
    """
    print(LIGHT_PURPLE + ascii_art)
    print(GREY + "歡迎使用凜漉工具箱 - Ma2cd轉譜器！ 版本 1.6")
    print(WHITE + "建議將此視窗最大化以獲得最佳顯示效果！")
    print(WHITE + "歡迎使用 凜漉工具箱 - Ma2cd轉譜器！")

def get_input_folder():
    while True:
        folder_path = input(f"{GREY}請輸入包含 maidata.txt 的資料夾路徑：{Style.RESET_ALL}")
        if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, 'maidata.txt')):
            return folder_path
        else:
            print(f"{RED}無效的資料夾路徑或找不到 maidata.txt，請重新輸入。{Style.RESET_ALL}")

def process_maidata(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 找到所有 &inote_ 開頭的行
    inote_lines = re.findall(r'&inote_\d+=.*', content, re.DOTALL)
    
    if not inote_lines:
        print(f"{YELLOW}警告：在 maidata.txt 中找不到 &inote_ 行。{Style.RESET_ALL}")
        return None

    # 取最後一個 &inote_ 行（假設這是最高難度）
    last_inote = inote_lines[-1]
    
    # 保留 &inote_X= 部分
    processed_content = last_inote.strip()
    
    # 移除所有的換行符，確保內容在一行中
    processed_content = processed_content.replace('\n', '')
    
    if not processed_content:
        print(f"{YELLOW}警告：處理後的內容為空。{Style.RESET_ALL}")
        return None

    print(f"{GREEN}成功處理 maidata.txt 內容。{Style.RESET_ALL}")
    print(f"{YELLOW}處理後的內容：{processed_content[:100]}...{Style.RESET_ALL}")  # 顯示前100個字符
    return processed_content

def convert(input_folder, input_id, difficulty):
    # 取得目前文件所在目錄路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 建立 MaichartConverter 的目錄路徑
    maichart_dir = os.path.join(current_dir, "SimaiMa2DX")

    # 建立輸入檔案的完整路徑
    input_file_path = os.path.join(input_folder, 'maidata.txt')

    # 處理 maidata.txt 內容
    processed_content = process_maidata(input_file_path)
    if processed_content is None:
        print(f"{RED}無法在 maidata.txt 中找到有效的譜面數據。{Style.RESET_ALL}")
        return

    # 創建臨時文件
    temp_file_path = os.path.join(current_dir, "temp_maidata.txt")
    with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        temp_file.write(processed_content)

    # 定義要執行的命令提示字元指令
    output_dir = os.path.join(current_dir, "output")
    command = rf'MaichartConverter CompileSimai -p "{temp_file_path}" -f Ma2_104 -o "{output_dir}"'

    # 在命令提示字元中執行指令
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=maichart_dir)

    # 等待指令執行完成
    stdout, stderr = process.communicate()

    # 刪除臨時文件
    os.remove(temp_file_path)

    # 輸出執行結果
    if stderr:
        print(f"{RED}轉換失敗！錯誤訊息：{stderr.decode()}{Style.RESET_ALL}")
    else:
        # 建立新的檔名，使用資料夾名稱作為 ID
        new_file_name = f"{input_id}_{difficulty[:2]}.ma2"
        old_file_path = os.path.join(output_dir, 'result.ma2')
        new_file_path = os.path.join(output_dir, new_file_name)

        # 檢查檔案是否存在，若存在則更名
        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            print(WHITE + "")
            print(f"{GREEN}成功將文字轉換為ma2文件，並已更名為：{new_file_name}{Style.RESET_ALL}")
        else:
            print(WHITE + "")
            print(f"{YELLOW}雖然轉換成功，但找不到 result.ma2 檔案！{Style.RESET_ALL}")

def main():
    welcome()
    start_cmd = input(f"是否要執行 MA2 轉譜工具？不執行將直接跳至 背景 & 封面轉換器 (Y/N)：{Style.RESET_ALL}")
    print("")

    if start_cmd.lower() == "y":
        os.makedirs("img_input", exist_ok=True)
        os.makedirs("img_output", exist_ok=True)

        input_folder = get_input_folder()
        input_id = os.path.basename(input_folder)  # 使用資料夾名稱作為 ID
        print("")
        print("請選擇難度：")
        difficulties = ["Basic", "Advanced", "Expert", "Master", "Re:Master"]
        for index, difficulty in enumerate(difficulties):
            print(f"{GREY}[{index}] {difficulty}{Style.RESET_ALL}")

        difficulty_number = int(input(f"{GREY}請輸入：{Style.RESET_ALL}"))
        convert(input_folder, input_id, f"{difficulty_number:02d}_{difficulties[difficulty_number]}")
    else:
        print(f"{GREEN}跳過 ma2 譜面轉換器，直接進入背景 & 封面轉換器。{Style.RESET_ALL}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.call(['python', os.path.join(current_dir, 'image_processor.py')])

    last_path = get_last_path()
    if last_path:
        folder_path = last_path
        print(f"使用上一個腳本的路徑：{folder_path}")
    else:
        folder_path = input("請輸入資料夾路徑：")

if __name__ == "__main__":
    main()
