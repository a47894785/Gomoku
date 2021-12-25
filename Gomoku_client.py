from typing import Text
import pygame
import sys
import numpy as np
import time
from pygame.event import wait
from pygame.font import SysFont
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
press_flag2 = 0
press_createRoom = 0
msg_flag = 0
delay = 50
# 棋子位置
chess_pos = []
# 建立pygame視窗
win = pygame.display.set_mode((width, height))
win_temp = pygame.display.set_mode((width, height))
win_start = pygame.display.set_mode((900, 600))
win_room = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gomoku Client')
# image
img = pygame.image.load('texture\\bg.jpg')
img_info = pygame.image.load('texture\\info.png')
img.convert()
img_info.convert()

# Rect
rect_info = pygame.Rect(600, 0, 300, 600)
rect_restart = pygame.Rect(700, 430, 100, 50)
rect_exit = pygame.Rect(700, 500, 100, 50)
rec_new_user = pygame.Rect(50, 50, 800, 100)
rec_log_in = pygame.Rect(50, 200, 800, 100)
rec_exit_game = pygame.Rect(50, 350, 800, 100)
rect_input_username = pygame.Rect(50, 100, 800, 100)
rect_input_password = pygame.Rect(50, 300, 800, 100)
rect_exit_log_or_new = pygame.Rect(100, 450, 200, 100)
rect_submit_log_or_new = pygame.Rect(550, 450, 200, 100)
rect_room_exit = pygame.Rect(650, 500, 200, 80)
rect_erase = pygame.Rect(100, 200, 700, 99)
rect_enter = pygame.Rect(400, 275, 100, 50)
rect_create_room = pygame.Rect(650, 400, 200, 80)
# text
text_create = ["Create Username:", "Create Password:"]  # 帳號 以及 密碼
text_log = ["Input Username:", "Input Password:"]
text_start = ["New User", "Log In", "Exit Game"]
text_warning = ""
text_username = ""  # 存入帳號
text_password = ""  # 存入密碼
text_exit_log_or_new = ["exit", "submit"]
text_create_room = ["Create", "Room"]
# data
room_id = int(0)
new_dict = {}


class Player():
    def __init__(self, id, name, ip, port):
        self.id = id
        self.name = name
        self.ip = ip
        self.port = port
        self.color = []  # 棋子顏色
        self.is_host = False  # 是否為房主
        self.msg = 'normal'

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

    def drawChessBoard(self, dict, hostID):  # 繪製棋盤畫面
        win.fill(white)
        win.blit(img, (0, 0))
        pygame.draw.rect(win, [132, 138, 130], rect_info)
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
            pygame.draw.rect(win, button_on, rect_restart)
        else:
            pygame.draw.rect(win, button_off, rect_restart)
        pygame.draw.rect(win, button_on, rect_exit)
        # 顯示文字
        font = pygame.font.SysFont("", 35)
        font_userInfo = pygame.font.SysFont("", 30)
        text1 = font.render('Restart', True, black)
        text2 = ""
        text_exit = font.render('Exit', True, black)
        text_username = font_userInfo.render("Name: " + dict['username'], True, black)
        text_hostID = font_userInfo.render("Host is " + hostID, True, black)
        if self.color == black:
            text2 = font.render('BLACK', True, black)
        elif self.color == white:
            text2 = font.render('WHITE', True, white)
        text3 = font.render('You are room host', True, black)
        win.blit(text_username, (620, 80))
        win.blit(text_hostID, (620, 100))
        win.blit(text1, (707, 443))
        win.blit(text2, (700, 20))
        win.blit(text_exit, (724, 513))
        if self.is_host:
            win.blit(text3, (635, 350))

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
            text = font.render('WHITE WIN', True, white)
        win.blit(text, (670, 400))

    def message(self, situation):
        font = pygame.font.SysFont("", 35)
        if situation == "turnError":
            turnErr = font.render("Cannot drop chess!", True, [220, 182, 128])
        win.blit(turnErr, (633, 220))

    def warming_text(self, string):
        global text_warning
        if string == 'nameisrepeat':  # flag為false表示新增失敗(可能某行 整個都是空白...)
            text_warning = ""
            text_warning = text_warning + "Username is already exist"
            # 等待幾秒後，再把提醒字眼給覆蓋掉
        elif string == 'nameisempty':  # flag為false表示新增失敗(可能某行 整個都是空白...)
            text_warning = ""
            text_warning = text_warning + "Username is empty"
            # 等待幾秒後，再把提醒字眼給覆蓋掉
        elif string == 'passisempty':  # flag為false表示新增失敗(可能某行 整個都是空白...)
            text_warning = ""
            text_warning = text_warning + "Password is empty"
        elif string == 'usernameislong':
            text_warning = ""
            text_warning = text_warning + "Username is too long"
        elif string == "passwordislong":
            text_warning = ""
            text_warning = text_warning + "Password is too long"
        elif string == 'notfindusername':
            text_warning = ""
            text_warning = text_warning + "Username Input Error"
        elif string == 'passworderror':
            text_warning = ""
            text_warning = text_warning + "Password input Error"
        elif string == 'loginalready':
            text_warning = ""
            text_warning = text_warning + "Account is already login"
        font = pygame.font.SysFont("", 35)
        text1 = font.render(text_warning, True, [255, 0, 0])
        win_start.blit(text1, (300, 250))
        pygame.display.update()
        # 上面就是顯示提醒的字眼
        time.sleep(1.0)
        pygame.draw.rect(win_start, win_color, rect_erase)
        pygame.display.update()
        # 等待幾秒後，再把提醒字眼給覆蓋掉


def main():
    global chess_pos, clicked, press_flag, color, press_flag1, delay, msg_flag, room_id, press_flag2, press_createRoom
    if (len(sys.argv) < 2):
        print('Usage: python Gomoku_client.py ServerIP')
        exit(1)
    server = xmlrpc.client.ServerProxy('http://' + sys.argv[1] + ':' + str(PORT))
    run = False
    # room_id = int(sys.argv[2])
    pygame.init()
    # 建立物件
    player = Player('abcd', sys.argv[2], '127.0.0.1', 8888)
    #print('server color list: ' + str(server.get_color_list(room_id)))
    # num = server.set_player(True)
    # if not num:
    #     print('Room is full.')
    #     sys.exit()
    # color = server.get_color()
    # player.set_color(color)
    run_system = True
    run_write = False
    run_room = False
    run_identify = False
    run_room = False
    global win_start, win_room
    global text_create, text_log, text_password, text_username, text_warning, new_dict
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
        win.blit(text1, (290, 70))
        win.blit(text2, (345, 220))
        win.blit(text3, (285, 373))
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
                if 50 <= x <= 850 and 50 <= y <= 150:  # 進入新增帳號介面
                    win_start.fill(win_color)
                    pygame.display.update()
                    run_write = True
                    while run_write:
                        pygame.draw.rect(win_start, button_on, rect_input_username)
                        pygame.draw.rect(win_start, button_on, rect_input_password)
                        pygame.draw.rect(win_start, button_on, rect_exit_log_or_new)
                        pygame.draw.rect(win_start, button_on, rect_submit_log_or_new)
                        font = pygame.font.SysFont("", 75)
                        text1 = font.render(text_create[0], True, black)
                        text2 = font.render(text_create[1], True, black)
                        text3 = font.render(text_exit_log_or_new[0], True, black)
                        text4 = font.render(text_exit_log_or_new[1], True, black)
                        win_start.blit(text1, (55, 125))
                        win_start.blit(text2, (55, 325))
                        win_start.blit(text3, (150, 475))
                        win_start.blit(text4, (565, 475))
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
                                if 50 <= x <= 850 and 100 <= y <= 200:
                                    index = 0
                                elif 50 <= x <= 850 and 300 <= y <= 400:
                                    index = 1
                                elif 100 <= x <= 300 and 450 <= y <= 550:
                                    run_write = False
                                elif 550 <= x <= 750 and 450 <= y <= 550:
                                    new_dict["username"] = text_username
                                    new_dict["password"] = text_password
                                    new_dict["login"] = "N"
                                    # 運用dict來傳入
                                    flag = server.add_new_user(new_dict)
                                    # server.add_new_user會傳出 true 或是 false
                                    if flag == 'ok':  # flag為true表示新增成功
                                        run_write = False
                                    else:
                                        player.warming_text(flag)
                                    index = 0
                                    text_create[0] = "Create Username:"
                                    text_create[1] = "Create Password:"
                                    text_username = ""
                                    text_password = ""
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
                                            player.warming_text("usernameislong")
                                        else:
                                            text_create[index] += event.unicode
                                            text_username += event.unicode
                                    elif index == 1:  # index = 1(表示password)
                                        if (len(text_password) >= 10):
                                            player.warming_text("passwordislong")
                                        else:
                                            text_create[index] += '*'
                                            text_password += event.unicode
                elif 50 <= x <= 850 and 200 <= y <= 300:  # 進入登入帳號介面(基本上和新增差不多)
                    win_start.fill(win_color)
                    pygame.display.update()
                    run_identify = True
                    index = 0
                    while run_identify:
                        pygame.draw.rect(win_start, button_on, rect_input_username)
                        pygame.draw.rect(win_start, button_on, rect_input_password)
                        pygame.draw.rect(win_start, button_on, rect_exit_log_or_new)
                        pygame.draw.rect(win_start, button_on, rect_submit_log_or_new)
                        font = pygame.font.SysFont("", 75)
                        text1 = font.render(text_log[0], True, black)
                        text2 = font.render(text_log[1], True, black)
                        text3 = font.render(text_exit_log_or_new[0], True, black)
                        text4 = font.render(text_exit_log_or_new[1], True, black)
                        win_start.blit(text1, (55, 125))
                        win_start.blit(text2, (55, 325))
                        win_start.blit(text3, (150, 475))
                        win_start.blit(text4, (565, 475))
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
                                if 50 <= x <= 850 and 100 <= y <= 200:
                                    index = 0
                                elif 50 <= x <= 850 and 300 <= y <= 400:
                                    index = 1
                                elif 100 <= x <= 300 and 450 <= y <= 550:
                                    index = 0
                                    text_log[0] = "Input Username:"
                                    text_log[1] = "Input Password:"
                                    text_username = ""
                                    text_password = ""
                                    run_identify = False
                                elif 550 <= x <= 750 and 450 <= y <= 550:
                                    new_dict["username"] = text_username
                                    new_dict["password"] = text_password
                                    flag = server.identify_user(new_dict)
                                    # server.identify_user會傳出一個字串
                                    if flag == "name":  # 若是name表示 登入的username是不存在的
                                        player.warming_text("notfindusername")
                                        index = 0
                                        text_log[0] = "Input Username:"
                                        text_log[1] = "Input Password:"
                                        text_username = ""
                                        text_password = ""
                                    elif flag == "pass":  # 若是pass表示username是存在但輸入的密碼是錯誤的
                                        player.warming_text("passworderror")
                                        index = 0
                                        text_log[0] = "Input Username:"
                                        text_log[1] = "Input Password:"
                                        text_username = ""
                                        text_password = ""
                                    elif flag == "login":
                                        player.warming_text("loginalready")
                                        index = 0
                                        text_log[0] = "Input Username:"
                                        text_log[1] = "Input Password:"
                                        text_username = ""
                                        text_password = ""
                                    elif flag == "ok":  # 若是ok則進入遊戲了~~
                                        try:
                                            index = 0
                                            run_identify = False
                                            #run = True
                                            run_room = True
                                            num = False
                                            win_start.fill(win_color)
                                            pygame.display.update()
                                            room_flag = 0
                                            while(run_room):
                                                # win_start.fill(win_color)
                                                clean_room = pygame.Rect(50, 50, 600, 550)
                                                if server.get_roomChange():
                                                    pygame.draw.rect(win_start, win_color, clean_room)
                                                    time.sleep(0.1)
                                                    server.roomChange(False)
                                                temp_list = server.get_some_information()
                                                # print(temp_list)
                                                # get_some_information()與server抓資料 裡面是好幾個list EX: [ [],[] ....]，而裡面好幾個list裡的資料 都是 第0個為房間人數 第1個為hostname 第2個為房間編號
                                                x_y_room = []
                                                # x_y_room 用來儲存 畫房間 每個房間的 編號 y_上界線 y_下界線 人數
                                                global rect_room, rect_y, text_y
                                                rect_y = int(50)
                                                text_y = rect_y + 15
                                                pygame.draw.rect(win_start, button_on, rect_create_room)
                                                pygame.draw.rect(win_start, button_on, rect_room_exit)
                                                font = pygame.font.SysFont("", 55)
                                                text1 = font.render(text_create_room[0], True, black)
                                                text2 = font.render(text_create_room[1], True, black)
                                                text_logOut = font.render('Log Out', True, black)
                                                win_start.blit(text1, (690, 410))
                                                win_start.blit(text2, (700, 440))
                                                win_start.blit(text_logOut, (680, 522))
                                                pygame.display.update()
                                                for i in range(len(temp_list)):
                                                    if temp_list[i][0] != 0:
                                                        rect_room = pygame.Rect(50, rect_y, 500, 50)
                                                        if temp_list[i][0] == 2:
                                                            pygame.draw.rect(win_start, button_off, rect_room)
                                                        else:
                                                            pygame.draw.rect(win_start, button_on, rect_room)
                                                        text3 = font.render(temp_list[i][1], True, black)
                                                        if temp_list[i][1] != "":
                                                            win_start.blit(text3, (60, text_y))
                                                        else:
                                                            room_flag = 1
                                                        temp_string = str(temp_list[i][0]) + "/2"
                                                        text4 = font.render(temp_string, True, black)
                                                        win_start.blit(text4, (420, text_y))
                                                        # 以上是畫房間的 有點覽的打
                                                        temp_x_y_room = []
                                                        temp_x_y_room.append(temp_list[i][2])
                                                        temp_x_y_room.append(rect_y)
                                                        temp_x_y_room.append((rect_y+50))
                                                        temp_x_y_room.append(temp_list[i][0])
                                                        x_y_room.append(temp_x_y_room)
                                                        # 以上是 存入房間的 ID y上就現與 下界線 人數
                                                        rect_y = rect_y + 50 + 50
                                                        text_y = rect_y + 15
                                                    else:
                                                        pygame.display.update()
                                                pygame.display.update()
                                                for event in pygame.event.get():
                                                    if event.type == QUIT:
                                                        logOut = server.log_out(new_dict)
                                                        sys.exit()
                                                    elif event.type == MOUSEBUTTONDOWN:
                                                        clicked = True
                                                    elif event.type == MOUSEBUTTONUP:
                                                        clicked = False
                                                        press_createRoom = 0
                                                    x, y = pygame.mouse.get_pos()
                                                    if clicked and press_createRoom == 0:
                                                        if 650 <= x <= 850 and 400 <= y <= 480:
                                                            temp_result = server.add_new_room()
                                                            room_id = len(temp_list)
                                                            run = True
                                                        elif 650 <= x <= 850 and 500 <= y <= 580:
                                                            logOut = server.log_out(new_dict)
                                                            index = 0
                                                            text_log[0] = "Input Username:"
                                                            text_log[1] = "Input Password:"
                                                            text_username = ""
                                                            text_password = ""
                                                            run_room = False
                                                        elif 50 <= x <= 550:
                                                            for i in range(len(x_y_room)):
                                                                if x_y_room[i][1] <= y <= x_y_room[i][2]:
                                                                    if x_y_room[i][3] != 2:
                                                                        run = True
                                                                        room_id = x_y_room[i][0]
                                                                    else:
                                                                        # 只在cmd呈現應該要在遊戲畫面呈現
                                                                        print('---Room is full---')
                                                                    break
                                                        press_createRoom = 1
                                                        if run == True:
                                                            num = server.set_player(True, room_id)
                                                        # if not num:
                                                        #     print('Room is full')
                                                        # else:
                                                            color = server.get_color(room_id)
                                                            player.set_color(color)
                                                            # hostID = temp_list[room_id][1]
                                                            while run:
                                                                temp_list = server.get_some_information()
                                                                hostID = temp_list[room_id][1]
                                                                # print(temp_list[room_id])
                                                                for event in pygame.event.get():
                                                                    if event.type == QUIT:
                                                                        quit = server.putColorBack(player.get_color(), room_id)
                                                                        print('Put ' + str(player.get_color()) + ' back.')
                                                                        print(quit)
                                                                        if player.get_isHost():
                                                                            server.set_host_false(room_id)
                                                                            player.set_host(False)
                                                                        print("---------> player : %d" % (server.get_player(room_id)))
                                                                        server.set_player(False, room_id)
                                                                        chessReset = server.chess_reset(room_id)
                                                                        logOut = server.log_out(new_dict)
                                                                        sys.exit()
                                                                    elif event.type == MOUSEBUTTONDOWN:
                                                                        clicked = True
                                                                    elif event.type == MOUSEBUTTONUP:
                                                                        clicked = False
                                                                        press_flag = 0  # 棋盤上
                                                                        press_flag1 = 0  # Restart
                                                                        press_flag2 = 0  # exit
                                                                is_host = server.is_host(new_dict["username"], room_id)
                                                                player.set_host(is_host)
                                                                # print('roomHost ======> %s' % (temp_list[room_id][1]))
                                                                player.drawChessBoard(new_dict, hostID)  # 繪製棋盤
                                                                chess_pos = server.get_chess_pos(room_id)  # 取得棋子位置
                                                                player.drawChess()  # 繪製棋子
                                                                result = server.check_win(room_id)  # 判斷勝負
                                                                # 取得勝利方 init = -1, black = 0, white = 1
                                                                winSide = server.get_winSide(room_id)
                                                                # 若有一方勝利且棋局尚未結束，先將棋局結束後印出勝利方
                                                                if winSide != -1 and not server.is_end(room_id):
                                                                    if winSide == 0:
                                                                        print('Black Win')
                                                                    else:
                                                                        print('White Win')
                                                                    if is_host:  # 若是房主則向伺服器請求將棋局結束
                                                                        server.game_end(True, room_id)
                                                                if winSide != -1:
                                                                    player.printWin(winSide)
                                                                # 取得滑鼠座標
                                                                x, y = pygame.mouse.get_pos()
                                                                if x <= 600:  # 在棋盤範圍內
                                                                    x0, y0 = player.posInfo(x, y)
                                                                    if player.check_pos(x0, y0):
                                                                        pygame.draw.rect(win, [255, 0, 0], [x0 - 20, y0 - 20, 40, 40], 2, 1)

                                                                chess_pos = server.get_chess_pos(room_id)  # 取得棋子位置
                                                                # msg
                                                                if msg_flag == 1 and delay > 0:
                                                                    player.message('turnError')
                                                                    delay -= 1
                                                                if x <= 600:  # 在棋盤範圍內
                                                                    if not server.is_end(room_id):
                                                                        if clicked and press_flag == 0:
                                                                            if player.check_pos(x0, y0):
                                                                                # 根據棋子顏色判斷是否為我方下棋
                                                                                if (server.dropChess(x0, y0, player.get_color(), room_id)):
                                                                                    print('Drop chess in [%d, %d]' % (x0, y0))
                                                                                else:
                                                                                    msg_flag = 1
                                                                                    delay = 50
                                                                                    print('Cannot drop chess!')
                                                                            press_flag = 1
                                                                # Restart 按鈕
                                                                elif 700 <= x <= 800 and 430 <= y <= 480:
                                                                    if player.get_isHost() and clicked and press_flag1 == 0 and server.get_player(room_id) == 2:
                                                                        if server.game_reset(room_id):
                                                                            server.game_end(False, room_id)
                                                                            server.putColorBack(
                                                                                player.get_color(), room_id)
                                                                            color = server.get_color(room_id)
                                                                            player.set_color(color)
                                                                            print('Restart')
                                                                        press_flag1 = 1
                                                                # Exit
                                                                elif 700 <= x <= 800 and 500 <= y <= 550:
                                                                    if clicked and press_flag2 == 0:
                                                                        quit = server.putColorBack(player.get_color(), room_id)
                                                                        print('Put ' + str(player.get_color()) + ' back.')
                                                                        print(quit)
                                                                        if player.get_isHost():
                                                                            server.set_host_false(room_id)
                                                                            player.set_host(False)
                                                                        server.exit_room(room_id)
                                                                        server.roomChange(True)
                                                                        server.chess_reset(room_id)
                                                                        # server.set_player(False, room_id)
                                                                        win_start.fill(win_color)
                                                                        press_flag2 = 1
                                                                        run = False

                                                                if player.get_isHost() == False:
                                                                    server.putColorBack(
                                                                        player.get_color(), room_id)
                                                                    color = server.get_color(
                                                                        room_id)
                                                                if color:
                                                                    player.set_color(
                                                                        color)
                                                                pygame.display.update()
                                        except:
                                            logOut = server.log_out(new_dict)
                                    flag = ""
                                    index = 0
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
                                            player.warming_text("usernameislong")
                                        else:
                                            text_log[index] += event.unicode
                                            text_username += event.unicode
                                    elif index == 1:
                                        if (len(text_password) >= 10):
                                            player.warming_text("passwordislong")
                                        else:
                                            text_log[index] += '*'
                                            text_password += event.unicode
                elif 50 <= x <= 850 and 350 <= y <= 450:  # 離開遊戲
                    run_system = False
                    pygame.quit()
                    sys.exit()
                press_flag = 1


if __name__ == '__main__':
    main()
# 同時登入問題
