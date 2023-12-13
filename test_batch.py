import sys
import re
import subprocess


logo_art = """
  _    _                      _____ 
 | |  | |               /\   |_   _|
 | |__| | _____  __    /  \    | |  
 |  __  |/ _ \ \/ /   / /\ \   | |  
 | |  | |  __/>  <   / ____ \ _| |_ 
 |_|  |_|\___/_/\_\ /_/    \_\_____|
                                    
                             
  _______                     ______ ____  
 |__   __|                   |____  |___ \ 
    | | ___  __ _ _ __ ___       / /  __) |
    | |/ _ \/ _` | '_ ` _ \     / /  |__ < 
    | |  __/ (_| | | | | | |   / /   ___) |
    |_|\___|\__,_|_| |_| |_|  /_/   |____/ 
                                           
                                                                   
"""

START_NEW ="""
   _____ _______       _____ _______   _   _ ________          __
  / ____|__   __|/\   |  __ \__   __| | \ | |  ____\ \        / /
 | (___    | |  /  \  | |__) | | |    |  \| | |__   \ \  /\  / / 
  \___ \   | | / /\ \ |  _  /  | |    | . ` |  __|   \ \/  \/ /  
  ____) |  | |/ ____ \| | \ \  | |    | |\  | |____   \  /\  /   
 |_____/   |_/_/    \_\_|  \_\ |_|    |_| \_|______|   \/  \/    

                                                                                                                            
"""

FAILED="""
  ______      _____ _      ______ _____  
 |  ____/\   |_   _| |    |  ____|  __ \ 
 | |__ /  \    | | | |    | |__  | |  | |
 |  __/ /\ \   | | | |    |  __| | |  | |
 | | / ____ \ _| |_| |____| |____| |__| |
 |_|/_/    \_\_____|______|______|_____/ 
                                         
                                         
"""

WIN="""
 __          _______ _   _ 
 \ \        / /_   _| \ | |
  \ \  /\  / /  | | |  \| |
   \ \/  \/ /   | | | . ` |
    \  /\  /   _| |_| |\  |
     \/  \/   |_____|_| \_|
                           
                           
"""

COMPLETE = """
$$$$$$$\   $$$$$$\  $$\   $$\ $$\   $$\ $$$$$$$\                                   
$$  __$$\ $$  __$$\ $$ |  $$ |$$$\  $$ |$$  __$$\                                  
$$ |  $$ |$$ /  $$ |$$ |  $$ |$$$$\ $$ |$$ |  $$ |                                 
$$$$$$$  |$$ |  $$ |$$ |  $$ |$$ $$\$$ |$$ |  $$ |                                 
$$  __$$< $$ |  $$ |$$ |  $$ |$$ \$$$$ |$$ |  $$ |                                 
$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |\$$$ |$$ |  $$ |                                 
$$ |  $$ | $$$$$$  |\$$$$$$  |$$ | \$$ |$$$$$$$  |                                 
\__|  \__| \______/  \______/ \__|  \__|\_______/                                  
                                                                                   
                                                                                   
                                                                                   
 $$$$$$\   $$$$$$\  $$\      $$\ $$$$$$$\  $$\       $$$$$$$$\ $$$$$$$$\ $$$$$$$$\ 
$$  __$$\ $$  __$$\ $$$\    $$$ |$$  __$$\ $$ |      $$  _____|\__$$  __|$$  _____|
$$ /  \__|$$ /  $$ |$$$$\  $$$$ |$$ |  $$ |$$ |      $$ |         $$ |   $$ |      
$$ |      $$ |  $$ |$$\$$\$$ $$ |$$$$$$$  |$$ |      $$$$$\       $$ |   $$$$$\    
$$ |      $$ |  $$ |$$ \$$$  $$ |$$  ____/ $$ |      $$  __|      $$ |   $$  __|   
$$ |  $$\ $$ |  $$ |$$ |\$  /$$ |$$ |      $$ |      $$ |         $$ |   $$ |      
\$$$$$$  | $$$$$$  |$$ | \_/ $$ |$$ |      $$$$$$$$\ $$$$$$$$\    $$ |   $$$$$$$$\ 
 \______/  \______/ \__|     \__|\__|      \________|\________|   \__|   \________|
                                                                                   
                                                                                                                                                                                                    
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
    command1 = f'python3 Hex.py "{modified_commands[0]}" "{modified_commands[1]}" -v'
    command2 = f'python3 Hex.py "{modified_commands[1]}" "{modified_commands[0]}" -v'

    # 执行命令1
    process1 = subprocess.run(command1, shell=True, capture_output=True, text=True)

    # 检查命令1是否成功完成
    if process1.returncode == 0:
        print(f"Command 1 successful: {command1}")
        # 检查输出是否包含 "Game over"
        game_over_line1 = next((line for line in process1.stdout.split('\n') if line.startswith("Game over")), None)

        if game_over_line1 is not None:
            with open('output1.txt', 'a') as output_file:
                output_file.write(game_over_line1 + '\n')
                # 查找包含关键词 "took" 的行并写入文件
                for line in process1.stdout.split('\n'):
                    if "took" in line:
                        output_file.write(line + '\n')
                output_file.write('\n')
        else:
            print("Game over not found in command 1 output.")

        print(START_NEW)

        # 执行命令2
        process2 = subprocess.run(command2, shell=True, capture_output=True, text=True)

        # 检查命令2是否成功完成
        if process2.returncode == 0:
            print(f"Command 2 successful: {command2}")
            # 检查输出是否包含 "Game over"
            game_over_line2 = next((line for line in process2.stdout.split('\n') if line.startswith("Game over")), None)

            if game_over_line2 is not None:
                with open('output2.txt', 'a') as output_file:
                    output_file.write(game_over_line2 + '\n')
                    # 查找包含关键词 "took" 的行并写入文件
                    for line in process2.stdout.split('\n'):
                        if "took" in line:
                            output_file.write(line + '\n')
                    output_file.write('\n')
                    
            else:
                print("Game over not found in command 2 output.")
        else:
            print(f"Command 2 failed: {command2}")
            print(FAILED)

    else:
        print(f"Command 1 failed: {command1}")
        print(FAILED)

    print(COMPLETE)
