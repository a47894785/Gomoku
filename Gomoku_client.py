from typing import Text
import pygame
import sys
import numpy as np
import time
from pygame.event import wait
from pygame.locals import *
import xmlrpc.client
import os

PORT = 8888
# 視窗長寬
width = 900
height = 600
# 顏色
win_color = [255, 165, 79]
black = [0, 0, 0]
white = [255, 255, 255]
button_on = [176, 196, 222]
button_off = [119, 136, 153]
color = []
# flags
clicked = False
press_flag = 0
press_flag1 = 0
msg_flag = 0  # 0(normal) 1(turnError) 2()
delay = 50
# 棋子位置
chess_pos = []
# 建立pygame視窗
win = pygame.display.set_mode((width, height))
win_temp = pygame.display.set_mode((width, height))
win_start = pygame.display.set_mode((900, 600))
pygame.display.set_caption('Gomoku Client')
# Restart矩形
rect1 = pygame.Rect(700, 200, 100, 50)
rec_new_user = pygame.Rect(50, 50, 400, 100)
rec_log_in = pygame.Rect(50, 200, 400, 100)
rec_exit_game = pygame.Rect(50, 350, 400, 100)
rect_input_username = pygame.Rect(50, 200, 800, 100)
rect_input_password = pygame.Rect(50, 400, 800, 100)
rect_erase = pygame.Rect(100, 170, 700, 30)
text_create = ["Create Username:", "Create Password:"]  # 帳號 以及 密碼
text_log = ["Input Username:", "Input Password:"]
text_start = ["New User", "Log In", "Exit Game"]
text_warning = ""
text_username = ""  # 存入帳號
text_password = ""  # 存入密碼


class Player():
    def __init__(self, id, name, ip, port):
        self.id = id
        self.name = name
        self.ip = ip
        self.port = port
        self.color = []  # 棋子顏色
        self.is_host = False  # 是否為房主
        self.msg = "normal"

    def set_msg(self, str):
        self.msg = str

    def posInfo(self, x, y):
        for i in range(20, 600, 40):
            for j in range(20, 600, 40):
                L1 = i - 20
                L2 = i + 20
                R1 = j - 20
                R2 = j + 20
                if x >= L1 and x <= L2 and y >= R1 and y <= R2:
                    return i, j
        return x, y

    def set_host(self, isHost):
        self.is_host = isHost

    def set_color(self, color):
        self.color = color

    def get_isHost(self):  # 回傳是否為房主
        host = self.is_host
        return host

    def check_pos(self, x, y):  # 確認可否落棋
        global chess_pos
        for pos in chess_pos:
            if pos[0][0] == x and pos[0][1] == y:
                return False
        return True

    def drawChessBoard(self):  # 繪製棋盤畫面
        win.fill(win_color)
        for i in range(20, 600, 40):
            if i == 20 or i == 580:
                pygame.draw.line(win, black, [i, 20], [i, 580], 4)
                pygame.draw.line(win, black, [20, i], [580, i], 4)
            else:
                pygame.draw.line(win, black, [i, 20], [i, 580], 2)
                pygame.draw.line(win, black, [20, i], [580, i], 2)
        pygame.draw.circle(win, black, [300, 300], 6, 0)
        pygame.draw.circle(win, black, [140, 140], 6, 0)
        pygame.draw.circle(win, black, [140, 460], 6, 0)
        pygame.draw.circle(win, black, [460, 460], 6, 0)
        pygame.draw.circle(win, black, [460, 140], 6, 0)
        if self.is_host:
            pygame.draw.rect(win, button_on, rect1)
        else:
            pygame.draw.rect(win, button_off, rect1)
        # 顯示文字
        font = pygame.font.SysFont("", 35)
        text1 = font.render('Restart', True, black)
        if self.color == black:
            text2 = font.render('BLACK', True, black)
        elif self.color == white:
            text2 = font.render('WHITE', True, white)
        text3 = font.render('You are room host', True, black)
        win.blit(text1, (707, 213))
        win.blit(text2, (700, 20))
        if self.is_host:
            win.blit(text3, (620, 350))

    def drawChess(self):  # 在棋盤上繪製棋子
        global chess_pos
        for chess in chess_pos:
            pygame.draw.circle(win, chess[1], chess[0], 18, 0)

    def get_color(self):  # 回傳棋子顏色
        myColor = self.color
        return myColor

    def printWin(self, side):  # 顯示勝利方
        font = pygame.font.SysFont("", 35)
        if side == 0:
            text = font.render('BLACK WIN', True, black)
        elif side == 1:
            text = font.render('WIHTE WIN', True, white)
        win.blit(text, (670, 400))

    def message(self, situation):
        font = pygame.font.SysFont("", 35)
        if situation == 'turnError':
            turnErr = font.render('Cannot drop chess!', True, [255, 0, 0])
        win.blit(turnErr, (625, 60))


def main():
    global chess_pos, clicked, press_flag, color, press_flag1, delay, msg_flag
    if (len(sys.argv) < 3):
        print('Usage: python Gomoku_client.py ServerIP name')
        exit(1)
    server = xmlrpc.client.ServerProxy(
        'http://' + sys.argv[1] + ':' + str(PORT))
    run = False
    pygame.init()
    # 建立物件
    player = Player('abcd', sys.argv[2], '127.0.0.1', 8888)
    print('server color list: ' + str(server.get_color_list()))
    # num = server.set_player(True)
    # if not num:
    #     print('Room is full.')
    #     sys.exit()
    # color = server.get_color()
    # player.set_color(color)
    run_system = True
    run_write = False
    run_identify = False
    global win_start
    global text_create, text_log, text_password, text_username, text_warning
    index = 0
    while(run_system):
        win_start.fill(win_color)
        pygame.draw.rect(win_start, button_on, rec_new_user)
        pygame.draw.rect(win_start, button_on, rec_log_in)
        pygame.draw.rect(win_start, button_on, rec_exit_game)
        font = pygame.font.SysFont("", 100)
        text1 = font.render(text_start[0], True, black)
        text2 = font.render(text_start[1], True, black)
        text3 = font.render(text_start[2], True, black)
        win.blit(text1, (85, 70))
        win.blit(text2, (125, 220))
        win.blit(text3, (80, 373))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                run_system = False
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                clicked = True
            elif event.type == MOUSEBUTTONUP:
                clicked = False
                press_flag = 0
            x, y = pygame.mouse.get_pos()
            if clicked and press_flag == 0:
                if 50 <= x <= 450 and 50 <= y <= 150:  # 進入新增帳號介面
                    win_start.fill(win_color)
                    pygame.display.update()
                    run_write = True
                    while run_write:
                        pygame.draw.rect(win_start, button_on,
                                         rect_input_username)
                        pygame.draw.rect(win_start, button_on,
                                         rect_input_password)
                        font = pygame.font.SysFont("", 75)
                        text1 = font.render(text_create[0], True, black)
                        text2 = font.render(text_create[1], True, black)
                        win_start.blit(text1, (55, 225))
                        win_start.blit(text2, (55, 425))
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                run_write = False
                                sys.exit()
                            elif event.type == MOUSEBUTTONDOWN:
                                clicked = True
                            elif event.type == MOUSEBUTTONUP:
                                clicked = False
                                press_flag = 0
                            x, y = pygame.mouse.get_pos()  # 判斷滑鼠位子去判斷要輸入哪一個，就不一定只能由name開始輸入，而且有錯誤時就可以直接點選錯誤的那一行
                            if clicked and press_flag == 0:
                                if 50 <= x <= 850 and 200 <= y <= 300:
                                    index = 0
                                elif 50 <= x <= 850 and 400 <= y <= 500:
                                    index = 1
                                press_flag = 1
                            if event.type == KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    index += 1
                                elif event.key == pygame.K_BACKSPACE:  # backspace的按鍵
                                    # 此行要判斷一定要加入，若不加入，可能連顯示的"create usernmae:"..的字樣都會沒有，因此要確保
                                    if len(text_create[index]) > 16:
                                        text_create[index] = text_create[index][:-1]
                                    if index == 0:
                                        text_username = text_username[:-1]
                                    elif index == 1:
                                        text_password = text_password[:-1]
                                    # 上述兩行再去判斷次哪個要減少字元，index = 0(表示username)，index = 1(表示password)
                                else:
                                    if index == 0:  # index = 0(表示username)
                                        # 去判定新增的name不能大於9個(為啥是9個，我也不知道)
                                        if (len(text_username) >= 10):
                                            text_warning = ""
                                            text_warning = text_warning + "Username is too long"
                                            font = pygame.font.SysFont("", 35)
                                            text1 = font.render(
                                                text_warning, True, black)
                                            win_start.blit(text1, (300, 170))
                                            pygame.display.update()
                                            # 上面就是顯示提醒的字眼
                                            time.sleep(1.0)
                                            pygame.draw.rect(
                                                win_start, win_color, rect_erase)
                                            pygame.display.update()
                                            # 等待幾秒後，再把提醒字眼給覆蓋掉
                                        else:
                                            text_create[index] += event.unicode
                                            text_username += event.unicode
                                    elif index == 1:  # index = 1(表示password)
                                        if (len(text_password) >= 10):
                                            text_warning = ""
                                            text_warning = text_warning + "Password is too long"
                                            font = pygame.font.SysFont("", 35)
                                            text1 = font.render(
                                                text_warning, True, black)
                                            win_start.blit(text1, (300, 170))
                                            pygame.display.update()
                                            # 上面就是顯示提醒的字眼
                                            time.sleep(1.0)
                                            pygame.draw.rect(
                                                win_start, win_color, rect_erase)
                                            pygame.display.update()
                                            # 等待幾秒後，再把提醒字眼給覆蓋掉
                                        else:
                                            text_create[index] += '*'
                                            text_password += event.unicode
                            if index == 2:  # 進入此判斷表示要給server輸入的name和password
                                new_dict = {}
                                new_dict["username"] = text_username
                                new_dict["password"] = text_password
                                # 運用dict來傳入
                                flag = server.add_new_user(new_dict)
                                # server.add_new_user會傳出 true 或是 false
                                if(flag):  # flag為true表示新增成功
                                    index = 0
                                    text_create[0] = "Create Username:"
                                    text_create[1] = "Create Password:"
                                    text_username = ""
                                    text_password = ""
                                    run_write = False
                                else:  # flag為false表示新增失敗(可能某行 整個都是空白...)
                                    text_warning = ""
                                    text_warning = text_warning + "Creation error"
                                    font = pygame.font.SysFont("", 35)
                                    text1 = font.render(
                                        text_warning, True, black)
                                    win_start.blit(text1, (300, 170))
                                    pygame.display.update()
                                    # 上面就是顯示提醒的字眼
                                    time.sleep(1.0)
                                    pygame.draw.rect(
                                        win_start, win_color, rect_erase)
                                    pygame.display.update()
                                    index = 0  # 此行讓index為0是因為若不為0，迴圈又會再跑一次接著又出現提醒的字眼，防止再出現
                                    # 等待幾秒後，再把提醒字眼給覆蓋掉
                elif 50 <= x <= 450 and 200 <= y <= 300:  # 進入登入帳號介面(基本上和新增差不多)
                    win_start.fill(win_color)
                    pygame.display.update()
                    run_identify = True
                    while run_identify:
                        pygame.draw.rect(win_start, button_on,
                                         rect_input_username)
                        pygame.draw.rect(win_start, button_on,
                                         rect_input_password)
                        font = pygame.font.SysFont("", 75)
                        text1 = font.render(text_log[0], True, black)
                        text2 = font.render(text_log[1], True, black)
                        win_start.blit(text1, (55, 225))
                        win_start.blit(text2, (55, 425))
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                run_write = False
                                sys.exit()
                            elif event.type == MOUSEBUTTONDOWN:
                                clicked = True
                            elif event.type == MOUSEBUTTONUP:
                                clicked = False
                                press_flag = 0
                            x, y = pygame.mouse.get_pos()
                            if clicked and press_flag == 0:
                                if 50 <= x <= 850 and 200 <= y <= 300:
                                    index = 0
                                elif 50 <= x <= 850 and 400 <= y <= 500:
                                    index = 1
                                press_flag = 1
                            if event.type == KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    index += 1
                                elif event.key == pygame.K_BACKSPACE:
                                    if len(text_log[index]) > 15:
                                        text_log[index] = text_log[index][:-1]
                                    if index == 0:
                                        text_username = text_username[:-1]
                                    elif index == 1:
                                        text_password = text_password[:-1]
                                else:
                                    if index == 0:
                                        if (len(text_username) >= 10):
                                            text_warning = ""
                                            text_warning = text_warning + "Username is too long"
                                            font = pygame.font.SysFont("", 35)
                                            text1 = font.render(
                                                text_warning, True, black)
                                            win_start.blit(text1, (300, 170))
                                            pygame.display.update()
                                            time.sleep(1.0)
                                            pygame.draw.rect(
                                                win_start, win_color, rect_erase)
                                            pygame.display.update()
                                        else:
                                            text_log[index] += event.unicode
                                            text_username += event.unicode
                                    elif index == 1:
                                        if (len(text_password) >= 10):
                                            text_warning = ""
                                            text_warning = text_warning + "Password is too long"
                                            font = pygame.font.SysFont("", 35)
                                            text1 = font.render(
                                                text_warning, True, black)
                                            win_start.blit(text1, (300, 170))
                                            pygame.display.update()
                                            time.sleep(1.0)
                                            pygame.draw.rect(
                                                win_start, win_color, rect_erase)
                                            pygame.display.update()
                                        else:
                                            text_log[index] += '*'
                                            text_password += event.unicode
                            if index == 2:  # 進入此判斷表示要給server輸入的name和password
                                new_dict = {}
                                new_dict["username"] = text_username
                                new_dict["password"] = text_password
                                flag = server.identify_user(new_dict)
                                # server.identify_user會傳出一個字串
                                if flag == "name":  # 若是name表示 登入的username是不存在的
                                    text_warning = ""
                                    text_warning = text_warning + "Didn't find this username"
                                    font = pygame.font.SysFont("", 35)
                                    text1 = font.render(
                                        text_warning, True, black)
                                    win_start.blit(text1, (300, 170))
                                    pygame.display.update()
                                    time.sleep(1.0)
                                    pygame.draw.rect(
                                        win_start, win_color, rect_erase)
                                    pygame.display.update()
                                elif flag == "pass":  # 若是pass表示username是存在但輸入的密碼是錯誤的
                                    text_warning = ""
                                    text_warning = text_warning + "Input password is error"
                                    font = pygame.font.SysFont("", 35)
                                    text1 = font.render(
                                        text_warning, True, black)
                                    win_start.blit(text1, (300, 170))
                                    pygame.display.update()
                                    time.sleep(1.0)
                                    pygame.draw.rect(
                                        win_start, win_color, rect_erase)
                                    pygame.display.update()
                                elif flag == "ok":  # 若是ok則進入遊戲了~~
                                    index = 0
                                    text_log[0] = "Input Username:"
                                    text_log[1] = "Input Password:"
                                    text_username = ""
                                    text_password = ""
                                    run_identify = False
                                    run = True
                                    num = server.set_player(True)
                                    if not num:
                                        print('Room is full')
                                    else:
                                        color = server.get_color()
                                        player.set_color(color)
                                        while run:
                                            for event in pygame.event.get():
                                                if event.type == QUIT:
                                                    quit = server.putColorBack(
                                                        player.get_color())
                                                    print(
                                                        'Put ' + str(player.get_color()) + ' back.')
                                                    print(quit)
                                                    if player.get_isHost():
                                                        server.set_host_false()
                                                        player.set_host(False)
                                                    print("---------> player : %d" %
                                                          (server.get_player()))
                                                    server.set_player(False)
                                                    chessReset = server.chess_reset()
                                                    sys.exit()
                                                elif event.type == MOUSEBUTTONDOWN:
                                                    clicked = True
                                                elif event.type == MOUSEBUTTONUP:
                                                    clicked = False
                                                    press_flag = 0  # 棋盤上
                                                    press_flag1 = 0  # Restart
                                            is_host = server.is_host(
                                                sys.argv[2])
                                            player.set_host(is_host)
                                            player.drawChessBoard()  # 繪製棋盤
                                            chess_pos = server.get_chess_pos()  # 取得棋子位置
                                            player.drawChess()  # 繪製棋子
                                            result = server.check_win()  # 判斷勝負
                                            winSide = server.get_winSide()  # 取得勝利方 init = -1, black = 0, white = 1
                                            # 若有一方勝利且棋局尚未結束，先將棋局結束後印出勝利方
                                            if winSide != -1 and not server.is_end():
                                                if winSide == 0:
                                                    print('Black Win')
                                                else:
                                                    print('White Win')
                                                if is_host:  # 若是房主則向伺服器請求將棋局結束
                                                    server.game_end(True)
                                            if winSide != -1:
                                                player.printWin(winSide)
                                            # 取得滑鼠座標
                                            x, y = pygame.mouse.get_pos()
                                            if x <= 600:  # 在棋盤範圍內
                                                x0, y0 = player.posInfo(x, y)
                                                if player.check_pos(x0, y0):
                                                    pygame.draw.rect(win, [255, 0, 0], [
                                                        x0 - 20, y0 - 20, 40, 40], 2, 1)

                                            chess_pos = server.get_chess_pos()  # 取得棋子位置
                                            if x <= 600:  # 在棋盤範圍內
                                                if not server.is_end():
                                                    if clicked and press_flag == 0:
                                                        if player.check_pos(x0, y0):
                                                            # 根據棋子顏色判斷是否為我方下棋
                                                            if (server.dropChess(x0, y0, player.get_color())):
                                                                print(
                                                                    'Drop chess in [%d, %d]' % (x0, y0))
                                                            else:
                                                                msg_flag = 1
                                                                delay = 50
                                                                print(
                                                                    'Cannot drop chess')
                                                        press_flag = 1

                                            # msg
                                            if msg_flag == 1 and delay > 0:
                                                player.message('turnError')
                                                delay -= 1
                                            # Restart 按鈕
                                            elif 700 <= x <= 800 and 200 <= y <= 250:
                                                if player.get_isHost() and clicked and press_flag1 == 0:
                                                    if server.game_reset():
                                                        server.game_end(False)
                                                        server.putColorBack(
                                                            player.get_color())
                                                        color = server.get_color()
                                                        player.set_color(color)
                                                        print('Restart')
                                                    press_flag1 = 1
                                            if player.get_isHost() == False:
                                                server.putColorBack(
                                                    player.get_color())
                                                color = server.get_color()
                                            if color:
                                                player.set_color(color)
                                            pygame.display.update()
                                flag = ""
                                index = 0
                elif 50 <= x <= 450 and 350 <= y <= 450:  # 離開遊戲
                    run_system = False
                    pygame.quit()
                    sys.exit()
                press_flag = 1


if __name__ == '__main__':
    main()
