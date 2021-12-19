from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import time
import threading
import numpy as np
import random

PORT = 8888
white = [255, 255, 255]
black = [0, 0, 0]


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class Gomoku:
    def __init__(self):
        self.lock = threading.Lock()
        self.chess_pos = []
        self.color = [white, black]  # 預設list含有white,black
        self.host = ''
        self.have_host = False
        self.end = False
        self.reset = False
        self.winSide = -1
        self.player = 0

    def get_color_list(self):
        list = self.color
        return list

    def get_player(self):
        player = self.player
        return player

    def set_player(self, cmd):
        if self.player <= 2:
            if cmd == True:
                self.lock.acquire()
                self.player += 1
                self.lock.release()
            elif cmd == False:
                self.lock.acquire()
                self.player -= 1
                self.lock.release()
            return True
        elif self.player > 2:
            return False

    def set_host_false(self):
        self.lock.acquire()
        self.have_host = False
        self.host = ""
        self.lock.release()
        return True

    def putColorBack(self, color):
        print("color list: " + str(self.color))
        self.lock.acquire()
        self.color.append(color)
        self.lock.release()
        print("color list: " + str(self.color))
        return True

    def get_reset(self):
        reset = self.reset
        return reset

    def set_reset(self, flag):
        self.reset = flag

    def get_end(self):
        end = self.end
        return end

    def is_end(self):
        end = self.end
        return end
    # 回傳勝利方 init = -1, black = 0, white = 1

    def get_winSide(self):
        winside = self.winSide
        return winside
    # 設定棋局是否結束

    def game_end(self, value):
        self.lock.acquire()
        if value == True:
            self.end = True
        else:
            self.end = False
        self.lock.release()
        return True
    # 給予房主的權限

    def is_host(self, name):
        if self.have_host == False:  # 尚未有房主，指定房主(第一個連到Server者)
            self.lock.acquire()
            self.host = name
            self.have_host = True
            self.lock.release()
            return True
        elif self.host == name:
            return True
        else:  # 已經有房主回傳False
            return False
    # 隨機分配棋子顏色

    def get_color(self):
        print('=====# length of color = %d' % (len(self.color)))
        if len(self.color) == 2:  # 尚未分配任何一個棋子
            randnum = random.randint(0, 1)
            tmp = self.color[randnum]
            self.lock.acquire()
            self.color.remove(tmp)  # 從list移除該顏色
            self.lock.release()
            return tmp
        elif len(self.color) == 1:  # 已分配一個顏色
            tmp = self.color[0]
            self.lock.acquire()
            self.color.remove(self.color[0])  # 從list移除該顏色，之後color list為空
            self.lock.release()
            return tmp
        else:
            return False

    # 根據player的顏色落棋
    def dropChess(self, x0, y0, color):
        if len(self.chess_pos) % 2 == 0 and color == black:
            self.lock.acquire()
            self.chess_pos.append([[x0, y0], black])
            self.lock.release()
            return True
        elif len(self.chess_pos) % 2 == 1 and color == white:
            self.lock.acquire()
            self.chess_pos.append([[x0, y0], white])
            self.lock.release()
            return True
        else:
            return False

    # 回傳當前各棋子位置
    def get_chess_pos(self):
        pos = self.chess_pos
        return pos

    # 判斷勝負
    def check_win(self):
        map = np.zeros([15, 15], dtype=int)
        for val in self.chess_pos:
            x = int((val[0][0]-20)/40)
            y = int((val[0][1]-20)/40)
            if val[1] == white:
                map[x][y] = 2  # 表示白子
            else:
                map[x][y] = 1  # 表示黑子

        for i in range(15):
            pos1 = []
            pos2 = []
            for j in range(15):
                if map[i][j] == 1:
                    pos1.append([i, j])
                else:
                    pos1 = []
                if map[i][j] == 2:
                    pos2.append([i, j])
                else:
                    pos2 = []
                if len(pos1) >= 5:  # 五子連心
                    self.lock.acquire()
                    self.winSide = 0
                    self.lock.release()
                    return [1, pos1]
                if len(pos2) >= 5:
                    self.lock.acquire()
                    self.winSide = 1
                    self.lock.release()
                    return [2, pos2]

        for j in range(15):
            pos1 = []
            pos2 = []
            for i in range(15):
                if map[i][j] == 1:
                    pos1.append([i, j])
                else:
                    pos1 = []
                if map[i][j] == 2:
                    pos2.append([i, j])
                else:
                    pos2 = []
                if len(pos1) >= 5:
                    self.lock.acquire()
                    self.winSide = 0
                    self.lock.release()
                    return [1, pos1]
                if len(pos2) >= 5:
                    self.lock.acquire()
                    self.winSide = 1
                    self.lock.release()
                    return [2, pos2]
        for i in range(15):
            for j in range(15):
                pos1 = []
                pos2 = []
                for k in range(15):
                    if i+k >= 15 or j+k >= 15:
                        break
                    if map[i+k][j+k] == 1:
                        pos1.append([i+k, j+k])
                    else:
                        pos1 = []
                    if map[i+k][j+k] == 2:
                        pos2.append([i+k, j+k])
                    else:
                        pos2 = []
                    if len(pos1) >= 5:
                        self.lock.acquire()
                        self.winSide = 0
                        self.lock.release()
                        return [1, pos1]
                    if len(pos2) >= 5:
                        self.lock.acquire()
                        self.winSide = 1
                        self.lock.release()
                        return [2, pos2]
        for i in range(15):
            for j in range(15):
                pos1 = []
                pos2 = []
                for k in range(15):
                    if i+k >= 15 or j-k < 0:
                        break
                    if map[i+k][j-k] == 1:
                        pos1.append([i+k, j-k])
                    else:
                        pos1 = []
                    if map[i+k][j-k] == 2:
                        pos2.append([i+k, j-k])
                    else:
                        pos2 = []
                    if len(pos1) >= 5:
                        self.lock.acquire()
                        self.winSide = 0
                        self.lock.release()
                        return [1, pos1]
                    if len(pos2) >= 5:
                        self.lock.acquire()
                        self.winSide = 1
                        self.lock.release()
                        return [2, pos2]
        return [0, []]

    # 重新開始棋局，清空chess_pos並將winSide設回初始值
    def game_reset(self):
        self.lock.acquire()
        self.chess_pos.clear()
        self.winSide = -1
        # self.color = [white, black]
        self.reset = True
        self.lock.release()
        return True


def main():
    obj = Gomoku()
    server = ThreadXMLRPCServer(('', PORT))
    server.register_instance(obj)
    print('Listening on port %d' % (PORT))
    try:
        print('Use Control-C to exit!')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server exit')


if __name__ == '__main__':
    main()
