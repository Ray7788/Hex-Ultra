import sys
import re
import subprocess


logo_art = """
 _   _              ___  _____ 
| | | |            / _ \|_   _|
| |_| | _____  __ / /_\ \ | |  
|  _  |/ _ \ \/ / |  _  | | |  
| | | |  __/>  <  | | | |_| |_ 
\_| |_/\___/_/\_\ \_| |_/\___/ 
                               
                               
  _______                     ______ ____  
 |__   __|                   |____  |___ \ 
    | | ___  __ _ _ __ ___       / /  __) |
    | |/ _ \/ _` | '_ ` _ \     / /  |__ < 
    | |  __/ (_| | | | | | |   / /   ___) |
    |_|\___|\__,_|_| |_| |_|  /_/   |____/ 
                                           
                                                                   
"""

print(logo_art)

if len(sys.argv) != 2:
    print("Usage: python script.py your_commands.txt")
    sys.exit(1)

filename = sys.argv[1]
with open(filename, 'r') as file:
    lines = file.readlines()

for line in lines:
    # 去除首尾空白字符
    line = line.strip()

    # 使用正则表达式提取引号括起来的部分
    commands = re.findall(r'"([^"]+)"', line)

    # 对于每个命令，提取文件名并添加"agent="前缀
    modified_commands = [f'agent={re.search(r"/([^/]+)$", cmd).group(1)};{cmd}' for cmd in commands]

    # 拼接两个命令的两种顺序
    command1 = f'python3 Hex.py "{modified_commands[0]}" "{modified_commands[1]}"'
    command2 = f'python3 Hex.py "{modified_commands[1]}" "{modified_commands[0]}"'

    # 执行命令1
    process1 = subprocess.run(command1, shell=True)

    # 检查命令1是否成功完成
    if process1.returncode == 0:
        print(f"Command 1 successful: {command1}")
        print(logo_art)

        # 执行命令2
        process2 = subprocess.run(command2, shell=True)

        # 检查命令2是否成功完成
        if process2.returncode == 0:
            print(f"Command 2 successful: {command2}")
            print(logo_art)

        else:
            print(f"Command 2 failed: {command2}")
            print(logo_art)

    else:
        print(f"Command 1 failed: {command1}")
        print(logo_art)
