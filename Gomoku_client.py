import pygame
import sys
import numpy as np
import time
from pygame.locals import *
import xmlrpc.client

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
# 棋子位置
chess_pos = []
# 建立pygame視窗
win = pygame.display.set_mode((width, height))
win_temp = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gomoku Client')
# Restart矩形
rect1 = pygame.Rect(700, 200, 100, 50)
rect2 = pygame.Rect(300, 200, 200, 100)
text = ["Input the username : ", "Input your password: "]  # 帳號 以及 密碼
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
            text = font.render('WHITE WIN', True, white)
        win.blit(text, (670, 400))


def main():
    global chess_pos, clicked, press_flag, press_flag1, color
    if (len(sys.argv) < 3):
        print('Usage: python Gomoku_client.py ServerIP name')
        exit(1)
    server = xmlrpc.client.ServerProxy(
        'http://' + sys.argv[1] + ':' + str(PORT))
    run = True
    # if color == []:
    #     color = server.get_color()  # 從伺服器取得棋子顏色
    # print('$$$ Color = ' + str(color))
    # is_host = server.is_host(sys.argv[2])  # 伺服器回傳是否為房主
    # if is_host:
    #     print('You are the room host')
    # 伺服器回傳False表示已滿兩人
    # if color == False:
    #     print('Room is full')
    #     exit(1)
    # print(color)
    # 印出黑色或白色方
    # if color == white:
    #     print('You are white side')
    # else:
    #     print('You are black side')
    pygame.init()
    # 建立物件
    player = Player('abcd', sys.argv[2], '127.0.0.1', 8888)
    print('server color list: ' + str(server.get_color_list()))
    # print('player.color = ' + str(player.get_color()))
    # 房間人數+1
    num = server.set_player(True)
    if not num:
        print('Room is full')
        sys.exit()
    color = server.get_color()
    player.set_color(color)
    run_write = True
    win_temp.fill(win_color)
    global text, text_password, text_username
    index = 0
    # while run_write:
    #     pygame.draw.rect(win_temp, button_on, rect2)
    #     font = pygame.font.SysFont("", 35)
    #     text1 = font.render(text[0], True, black)
    #     text2 = font.render(text[1], True, black)
    #     win.blit(text1, (301, 201))
    #     win.blit(text2, (301, 401))
    #     pygame.display.update()
    #     for event in pygame.event.get():
    #         if event.type == QUIT or index == 2:
    #             run_write = False
    #         if event.type == KEYDOWN:
    #             if event.key == pygame.K_RETURN:
    #                 index += 1
    #             else:
    #                 if index == 0:
    #                     text[index] += event.unicode
    #                     text_username += event.unicode
    #                 elif index == 1:
    #                     text[index] += '*'
    #                     text_password += event.unicode
    #             if index == 2:
    #                 print(text_username + '\n' + text_password)

    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = server.putColorBack(player.get_color())
                print('put ' + str(player.get_color()) + ' back')
                print(quit)
                if player.get_isHost():
                    server.set_host_false()
                    player.is_host = False
                print("---------> player : %d" % (server.get_player()))
                server.set_player(False)
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                clicked = True
            elif event.type == MOUSEBUTTONUP:
                clicked = False
                press_flag = 0  # 棋盤上
                press_flag1 = 0  # Restart
        is_host = server.is_host(sys.argv[2])
        # print(is_host)
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
                            print('Drop chess in [%d, %d]' % (x0, y0))
                        else:
                            print('Not your turn')
                    press_flag = 1
        # Restart 按鈕
        elif 700 <= x <= 800 and 200 <= y <= 250:
            # 房主可按下重新開始
            if player.get_isHost() and clicked and press_flag1 == 0:
                if server.game_reset():
                    server.game_end(False)
                    server.putColorBack(player.get_color())
                    color = server.get_color()
                    player.set_color(color)
                    print('Restart')
                press_flag1 = 1
        if player.get_isHost() == False:
            server.putColorBack(player.get_color())
            color = server.get_color()
        if color:
            player.set_color(color)

        pygame.display.update()


if __name__ == '__main__':
    main()
