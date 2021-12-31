from sys import setswitchinterval
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import threading
import numpy as np
import random
from flask import Flask, json, request, jsonify

PORT = 12345
white = [255, 255, 255]
black = [0, 0, 0]
FILE1 = 'people.json'
ARR1 = []


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class Gomoku:
    def __init__(self):
        self.lock = threading.Lock()
        self.roomChange_flag = False
        self.chess_pos = []
        self.color = []
        self.host = []
        self.have_host = []
        self.end = []
        self.reset = []
        self.winSide = []
        self.player = []

    def get_some_information(self):
        list = []
        for i in range(len(self.player)):
            templist = []
            templist.append(self.player[i])
            templist.append(self.host[i])
            templist.append(int(i))
            list.append(templist)
        return list

    def roomChange(self, bool):
        self.lock.acquire()
        self.roomChange_flag = bool
        self.lock.release()
        return True

    def get_roomChange(self):
        flag = self.roomChange_flag
        return flag

    def exit_room(self, id):
        self.lock.acquire()
        self.player[id] -= 1
        self.lock.release()
        return True

    def add_new_room(self):
        self.lock.acquire()
        self.chess_pos.append([])
        self.color.append([white, black])
        self.host.append("")
        self.have_host.append(False)
        self.end.append(False)
        self.reset.append(False)
        self.winSide.append(int(-1))
        self.player.append(int(0))
        self.lock.release()
        return True

    def chess_reset(self, id):
        self.lock.acquire()
        self.chess_pos[id].clear()
        self.lock.release()
        return True

    def get_color_list(self, id):
        list = self.color[id]
        return list

    def get_player(self, id):
        player = self.player[id]
        return player

    def set_player(self, cmd, id):
        if cmd == True:
            if self.player[id] == 2:
                return False
            else:
                self.lock.acquire()
                self.player[id] += 1
                self.lock.release()
                return True
        elif cmd == False:
            self.lock.acquire()
            self.player[id] -= 1
            self.lock.release()
            return True

    def set_host_false(self, id):
        self.lock.acquire()
        self.have_host[id] = False
        self.host[id] = ""
        self.lock.release()
        return True

    def putColorBack(self, color, id):
        self.lock.acquire()
        self.color[id].append(color)
        self.lock.release()
        return True

    def get_reset(self, id):
        reset = self.reset[id]
        return reset

    def set_reset(self, flag, id):
        self.reset[id] = flag

    def get_end(self, id):
        end = self.end[id]
        return end

    # 回傳棋局是否結束
    def is_end(self, id):
        end = self.end[id]
        return end
    # 回傳勝利方 init = -1, black = 0, white = 1

    def get_winSide(self, id):
        winside = self.winSide[id]
        return winside
    # 設定棋局是否結束

    def game_end(self, value, id):
        self.lock.acquire()
        if value == True:
            self.end[id] = True
        else:
            self.end[id] = False
        self.lock.release()
        return True
    # 給予房主的權限

    def is_host(self, name, id):
        if self.have_host[id] == False:  # 尚未有房主，指定房主(第一個連到Server者)
            self.lock.acquire()
            self.host[id] = name
            self.have_host[id] = True
            self.lock.release()
            return True
        elif self.host[id] == name:
            return True
        else:  # 已經有房主回傳False
            return False
    # 隨機分配棋子顏色

    def get_color(self, id):
        if len(self.color[id]) == 2:  # 尚未分配任何一個棋子
            randnum = random.randint(0, 1)
            tmp = self.color[id][randnum]
            self.lock.acquire()
            self.color[id].remove(tmp)  # 從list移除該顏色
            self.lock.release()
            return tmp
        elif len(self.color[id]) == 1:  # 已分配一個顏色
            tmp = self.color[id][0]
            self.lock.acquire()
            self.color[id].remove(tmp)  # 從list移除該顏色，之後color list為空
            self.lock.release()
            return tmp
        else:  # 沒有顏色可以分配(color list為空)
            return False

    # 根據player的顏色落棋
    def dropChess(self, x0, y0, color, id):
        if self.player[id] == 2:
            if len(self.chess_pos[id]) % 2 == 0 and color == black:
                self.lock.acquire()
                self.chess_pos[id].append([[x0, y0], black])
                self.lock.release()
                return True
            elif len(self.chess_pos[id]) % 2 == 1 and color == white:
                self.lock.acquire()
                self.chess_pos[id].append([[x0, y0], white])
                self.lock.release()
                return True
            else:
                return False
        else:
            return False

    # 回傳當前各棋子位置
    def get_chess_pos(self, id):
        pos = self.chess_pos[id]
        return pos

    # 判斷勝負
    def check_win(self, id):
        map = np.zeros([15, 15], dtype=int)
        for val in self.chess_pos[id]:
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
                    self.winSide[id] = 0
                    self.lock.release()
                    return [1, pos1]
                if len(pos2) >= 5:
                    self.lock.acquire()
                    self.winSide[id] = 1
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
                    self.winSide[id] = 0
                    self.lock.release()
                    return [1, pos1]
                if len(pos2) >= 5:
                    self.lock.acquire()
                    self.winSide[id] = 1
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
                        self.winSide[id] = 0
                        self.lock.release()
                        return [1, pos1]
                    if len(pos2) >= 5:
                        self.lock.acquire()
                        self.winSide[id] = 1
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
                        self.winSide[id] = 0
                        self.lock.release()
                        return [1, pos1]
                    if len(pos2) >= 5:
                        self.lock.acquire()
                        self.winSide[id] = 1
                        self.lock.release()
                        return [2, pos2]
        return [0, []]
    # 重新開始棋局，清空chess_pos並將winSide設回初始值

    def game_reset(self, id):
        self.lock.acquire()
        self.chess_pos[id].clear()
        self.winSide[id] = -1
        self.reset[id] = True
        self.lock.release()
        return True

    def add_new_user(self, dict):
        if(dict["username"] == ""):
            return "nameisempty"
        elif (dict["password"] == ""):
            return "passisempty"
        flag = True
        for i in range(len(ARR1)):
            if dict["username"] == (ARR1[i]['username']):
                flag = False
                return "nameisrepeat"
        if(flag):
            ARR1.append(dict)
            self.lock.acquire()
            with open(FILE1, 'w') as wfp1:
                json.dump(ARR1, wfp1)
            self.lock.release()
            print(ARR1)
            return "ok"

    def identify_user(self, dict):
        flag = False
        for i in range(len(ARR1)):
            if dict["username"] == (ARR1[i]['username']):
                if dict["password"] == ARR1[i]["password"]:
                    if ARR1[i]["login"] == "N":
                        ARR1[i]["login"] = "Y"
                        self.lock.acquire()
                        with open(FILE1, 'w') as wfp1:
                            json.dump(ARR1, wfp1)
                        self.lock.release()
                        return "ok"
                    else:
                        return "login"
                else:
                    return "pass"
                flag = True
                break
        if flag == False:
            return "name"

    def log_out(self, dict):
        for i in range(len(ARR1)):
            if dict["username"] == (ARR1[i]["username"]):
                ARR1[i]['login'] = "N"
                self.lock.acquire()
                with open(FILE1, 'w') as wfp1:
                    json.dump(ARR1, wfp1)
                self.lock.release()
                return "ok"


def main():
    global ARR1
    # load JSON file
    with open(FILE1) as fp1:
        ARR1 = json.load(fp1)
    obj = Gomoku()
    server = ThreadXMLRPCServer(('127.0.0.1', PORT))
    server.register_instance(obj)
    print('Listening on port %d' % (PORT))
    try:
        print('Use Control-C to exit!')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server exit')


if __name__ == '__main__':
    main()
