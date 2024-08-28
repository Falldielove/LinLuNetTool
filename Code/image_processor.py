import os
import subprocess
import shutil
import sys
import time
from PIL import Image
from colorama import Fore, Style, init

# 初始化 colorama
init(autoreset=True)

# 定義顏色變數為全局變數
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
LIGHTBLACK_EX = Fore.LIGHTBLACK_EX

# 獲取父目錄路徑
PARENT_DIR = os.path.dirname(os.getcwd())

# 定義所有相關文件夾的路徑
IMG_INPUT_DIR = os.path.join(PARENT_DIR, "img_input")
IMG_OUTPUT_DIR = os.path.join(PARENT_DIR, "img_output")
DAT_INPUT_DIR = os.path.join(PARENT_DIR, "dat_input")
DAT_OUTPUT_DIR = os.path.join(PARENT_DIR, "dat_output")


def ensure_dir(directory):
    """確保目錄存在，如果不存在則創建它"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"{GREEN}已創建目錄：{directory}{Style.RESET_ALL}")

def get_image_file_name():
    """從img_input文件夾中列出並選擇圖片文件"""
    ensure_dir(IMG_INPUT_DIR)
    
    image_files = [f for f in os.listdir(IMG_INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"{RED}錯誤：img_input 文件夾中沒有圖片文件。{Style.RESET_ALL}")
        return None
    
    print("")
    print(f"{YELLOW}可用的圖片文件：{Style.RESET_ALL}")
    for i, file in enumerate(image_files, 1):
        print(f"{LIGHTBLACK_EX}[{i}] {file}{Style.RESET_ALL}")
    
    while True:
        try:
            choice = int(input(f"{LIGHTBLACK_EX}請選擇要處理的圖片文件（輸入數字）：{Style.RESET_ALL}"))
            if 1 <= choice <= len(image_files):
                return os.path.join(IMG_INPUT_DIR, image_files[choice-1])
            else:
                print(f"{RED}無效的選擇，請輸入有效的數字。{Style.RESET_ALL}")
        except ValueError:
            print(f"{RED}請輸入一個數字。{Style.RESET_ALL}")

def find_executable(executable_name):
    """查找可執行文件的路徑"""
    path = shutil.which(executable_name)
    if path:
        return path
    elif executable_name == "ffmpeg":
        return r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"
    else:
        return None

def check_ffmpeg():
    """檢查 ffmpeg 是否安裝，如果沒有安裝則提供安裝指導"""
    if not find_executable("ffmpeg"):
        print(f"{RED}錯誤：未找到 ffmpeg。{Style.RESET_ALL}")
        print(f"{YELLOW}請按照以下步驟安裝 ffmpeg：{Style.RESET_ALL}")
        print("1. 訪問 https://ffmpeg.org/download.html")
        print("2. 下載適合您系統的 ffmpeg 版本")
        print("3. 解壓下載的文件")
        print("4. 將解壓後的 ffmpeg.exe 文件所在的文件夾路徑添加到系統的 PATH 環境變量中")
        print("5. 重啟您的命令提示符或 IDE")
        print(f"{YELLOW}安裝完成後，請重新運行此腳本。{Style.RESET_ALL}")
        sys.exit(1)

def resize_image(input_path, output_path, size):
    """調整圖片大小並保存"""
    try:
        with Image.open(input_path) as image:
            image = image.resize(size, Image.LANCZOS)
            image.save(output_path)
        print(f"{GREEN}已生成調整大小的圖片：{output_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{RED}無法調整圖片大小：{e}{Style.RESET_ALL}")

def process_image(input_file_name, delete_original=False):
    """處理輸入的圖像文件，生成400x400和200x200的圖片"""
    ensure_dir(IMG_OUTPUT_DIR)
    input_id = input(f"{LIGHTBLACK_EX}請輸入ID（例：009403）：{Style.RESET_ALL}")
    print("")
    if not input_id:
        print(f"{RED}ID不能為空。{Style.RESET_ALL}")
        return
    base_name = os.path.basename(input_file_name)
    name, ext = os.path.splitext(base_name)
    output_file_name_400 = os.path.join(IMG_OUTPUT_DIR, f"UI_Jacket_{input_id}{ext}")
    output_file_name_200 = os.path.join(IMG_OUTPUT_DIR, f"UI_Jacket_{input_id}_s{ext}")
    resize_image(input_file_name, output_file_name_400, (400, 400))
    resize_image(input_file_name, output_file_name_200, (200, 200))

    # 根據 delete_original 參數決定是否刪除原始圖片
    if delete_original:
        delete_image(input_file_name)

def delete_image(file_path):
    """刪除指定的文件"""
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"{GREEN}已刪除原始圖片：{file_path}{Style.RESET_ALL}")
    else:
        print(f"{RED}要刪除的文件不存在。{Style.RESET_ALL}")

def convert_mp4_to_ivf(input_path, output_path, resolution="1080x610", bitrate="3000K"):
    """將MP4視頻文件轉換成IVF視頻文件"""
    try:
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            check_ffmpeg()
        command = [ffmpeg_path, '-i', input_path, '-vf', f'scale={resolution}', '-c:v', 'libvpx-vp9', '-b:v', bitrate, output_path]
        print("執行命令:", " ".join(command))
        subprocess.run(command, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"{RED}轉換 MP4 到 IVF 失敗：{e}{Style.RESET_ALL}")
        return None

def convert_image_to_video(input_path, output_path, duration=10, resolution="1080x1080", bitrate="3000K"):
    """將圖片轉換成視頻"""
    try:
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            check_ffmpeg()
        command = [
            ffmpeg_path, '-loop', '1', '-framerate', '10', '-i', input_path, 
            '-vf', f'scale={resolution}', '-t', str(duration), 
            '-c:v', 'libvpx-vp9', '-b:v', bitrate, '-pix_fmt', 'yuva420p', 
            output_path
        ]
        print("執行命令:", " ".join(command))
        subprocess.run(command, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"{RED}轉換圖片到視頻失敗：{e}{Style.RESET_ALL}")
        return None

def convert_ivf_to_usm(input_path, output_path):
    """將IVF視頻文件轉換成USM文件"""
    try:
        wannacri_path = find_executable("wannacri")
        if not wannacri_path:
            raise FileNotFoundError("未找到 wannacri 可執行文件")
        
        input_filename = os.path.basename(input_path)
        current_dir = os.getcwd()
        
        command = [
            wannacri_path, 'createusm', input_filename, '--key', '0x7F4551499DF55E68', '-o', output_path
        ]
        
        print(f"{YELLOW}執行命令: {' '.join(command)}{Style.RESET_ALL}")
        
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=current_dir)
        
        print(result.stdout)
        
        time.sleep(1)
        
        if os.path.exists(output_path):
            print(f"{GREEN}USM 文件成功創建：{output_path}{Style.RESET_ALL}")
            print(f"文件大小：{os.path.getsize(output_path)} 字節")
            os.remove(input_path)
            return output_path
        else:
            print(f"{RED}USM 文件未在預期位置找到：{output_path}{Style.RESET_ALL}")
            current_dir_files = os.listdir(current_dir)
            print(f"當前目錄中的文件：{current_dir_files}")
            usm_files = [f for f in current_dir_files if f.endswith('.usm')]
            if usm_files:
                print(f"找到以下 USM 文件：{usm_files}")
                actual_output_path = os.path.join(current_dir, usm_files[0])
                print(f"{YELLOW}使用找到的 USM 文件：{actual_output_path}{Style.RESET_ALL}")
                os.rename(actual_output_path, output_path)
                print(f"{GREEN}已將文件重命名為：{output_path}{Style.RESET_ALL}")
                os.remove(input_path)
                return output_path
            return None
    
    except subprocess.CalledProcessError as e:
        print(f"{RED}轉換 IVF 到 USM 失敗：{e}{Style.RESET_ALL}")
        print(f"錯誤輸出：\n{e.stdout}\n{e.stderr}")
        return None
    except FileNotFoundError as e:
        print(f"{RED}{e}{Style.RESET_ALL}")
        return None

def convert_video_files(input_folder=None):
    """將輸入的MP4文件或圖片文件轉換成USM文件"""
    if input_folder is None:
        input_folder = input(f"{LIGHTBLACK_EX}請輸入要處理的文件夾路徑（按下回車使用預設路徑 dat_input）：{Style.RESET_ALL}").strip()
        if not input_folder:
            input_folder = DAT_INPUT_DIR
    
    ensure_dir(input_folder)
    ensure_dir(DAT_OUTPUT_DIR)

    input_file_names = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.png', '.jpg', '.jpeg'))]
    if not input_file_names:
        print(f"{RED}{input_folder} 文件夾中沒有 MP4 文件或圖片文件。{Style.RESET_ALL}")
        return

    for input_file_name in input_file_names:
        input_file_path = os.path.join(input_folder, input_file_name)
        output_id = input(f"{LIGHTBLACK_EX}請輸入ID（例：009403）對於文件 {input_file_name}：{Style.RESET_ALL}").strip()
        if not output_id:
            print(f"{RED}ID不能為空。{Style.RESET_ALL}")
            continue
        
        if input_file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 如果是圖片文件，先生成封面圖片，但不刪除原始圖片
            process_image(input_file_path, delete_original=False)
            # 然後將圖片轉換為1:1的視頻
            resolution = "1080x1080"
            output_filename = f"{output_id}_1to1.ivf"
            ivf_file_name = convert_image_to_video(input_file_path, output_filename, duration=10, resolution=resolution, bitrate="3000K")
        else:
            # 如果是MP4文件，根據用戶選擇的比例進行轉換
            video_ratio = input(f"{LIGHTBLACK_EX}請輸入視頻比例（1:1 或 16:9）對於文件 {input_file_name}：{Style.RESET_ALL}").strip()
            resolution = "1080x1080" if video_ratio == "1:1" else "1080x610"
            output_filename = f"{output_id}_{video_ratio.replace(':', 'to')}.ivf"
            ivf_file_name = convert_mp4_to_ivf(input_file_path, output_filename, resolution=resolution, bitrate="3000K")

        if ivf_file_name:
            usm_file_name = convert_ivf_to_usm(ivf_file_name, f"{output_id}.usm")
            if usm_file_name:
                dat_file_name = os.path.join(DAT_OUTPUT_DIR, f"{output_id}.dat")
                os.rename(usm_file_name, dat_file_name)
                print(f"{GREEN}已將文件重命名為：{dat_file_name}{Style.RESET_ALL}")

            # 不刪除原始圖片

def main():
    """主函數，提供用戶操作菜單"""
    check_ffmpeg()
    while True:
        print(f"\n{GREEN}程序正常啟動{Style.RESET_ALL}")
        print("")
        print(f"{LIGHTBLACK_EX}[1] 生成封面圖片{Style.RESET_ALL}")
        print(f"{LIGHTBLACK_EX}[2] 轉換背景PV影片{Style.RESET_ALL}")
        print(f"{LIGHTBLACK_EX}[3] 自動處理指定文件夾中的文件{Style.RESET_ALL}")
        print(f"{LIGHTBLACK_EX}[4] 離開{Style.RESET_ALL}")
        print("")
        try:
            choice = int(input("請選擇要執行的操作："))
            if choice == 1:
                input_file_name = get_image_file_name()
                if input_file_name:
                    process_image(input_file_name, delete_original=True)  # 修改這裡，添加 delete_original=True
            elif choice == 2:
                convert_video_files()
            elif choice == 3:
                convert_video_files(input_folder=None)
            elif choice == 4:
                print(f"{Fore.LIGHTBLUE_EX}感謝使用，再見！{Style.RESET_ALL}")
                break
            else:
                print(f"{RED}請輸入有效的選項。{Style.RESET_ALL}")
        except ValueError:
            print(f"{RED}請輸入一個數字。{Style.RESET_ALL}")
    print(f"{YELLOW}崩鐵 啟動 ！{Style.RESET_ALL}")

if __name__ == "__main__":
    main()