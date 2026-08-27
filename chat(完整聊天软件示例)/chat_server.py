import asynchat
import asyncore
import socket


class EndSession(Exception):
    """用于通知会话结束"""
    pass


class ChatServer(asyncore.dispatcher):
    """聊天服务器主类，监听连接并管理用户和房间"""

    def __init__(self, ip, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((ip, port))
        self.listen(5)
        self.users = {}  # 记录当前在线用户 {name: session}
        self.main_room = ChatRoom(self)

    def handle_accepted(self, sock, addr):
        print('当前连接:', addr)
        ChatSession(self, sock)


class ChatSession(asynchat.async_chat):
    """负责和单个客户端进行通信"""

    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.room = None
        self.name = None
        self.data = []
        self.set_terminator(b'\n')
        self.enter(LoginRoom(self.server))

    def enter(self, room):
        """从当前房间移除自身，然后添加到指定房间"""
        cur = self.room
        if cur is not None:
            try:
                cur.remove(self)
            except (ValueError, AttributeError):
                pass
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data.decode('utf-8', errors='replace'))

    def found_terminator(self):
        """当客户端的一条完整数据（以\\n结尾）到达时调用"""
        line = ''.join(self.data).strip()
        self.data = []
        if not line:
            return
        try:
            self.room.handle(self, line.encode('utf-8'))
        except EndSession:
            self.handle_close()

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        if not isinstance(self.room, LogoutRoom):
            self.enter(LogoutRoom(self.server))


class CommandHandler:
    """命令解析基类，将 'cmd arg' 格式的命令分发给 do_cmd 方法"""

    def handle(self, session, line):
        line = line.decode('utf-8', errors='replace')
        if not line.strip():
            return

        parts = line.split(' ', 1)
        cmd = parts[0]
        arg = parts[1].strip() if len(parts) > 1 else ''

        method = getattr(self, 'do_' + cmd, None)
        if method is not None:
            try:
                method(session, arg)
            except TypeError as e:
                print(f'[命令执行错误] {cmd}: {e}')
        else:
            session.push(f'未知命令: {cmd}\n'.encode('utf-8'))


class Room(CommandHandler):
    """房间基类，包含多个用户，负责基本的命令处理和广播消息"""

    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        if session not in self.sessions:
            self.sessions.append(session)

    def remove(self, session):
        try:
            self.sessions.remove(session)
        except ValueError:
            pass

    def broadcast(self, line):
        """向房间内所有用户广播消息（遍历副本防止列表修改异常）"""
        for session in self.sessions[:]:
            try:
                session.push(line)
            except Exception:
                self.remove(session)

    def do_logout(self, session, line):
        raise EndSession


class LoginRoom(Room):
    """登录房间，等待用户输入用户名"""

    def add(self, session):
        Room.add(self, session)
        session.push(b'Connect Success\n')

    def do_login(self, session, line):
        name = line.strip()
        if not name:
            session.push(b'Username empty\n')
        elif name in self.server.users:
            session.push(b'Username exists\n')
        else:
            session.name = name
            session.enter(self.server.main_room)


class ChatRoom(Room):
    """聊天房间，代表正在聊天的用户集合"""

    def add(self, session):
        Room.add(self, session)
        self.server.users[session.name] = session
        session.push(b'login success\n')
        self.broadcast(f'< {session.name} 加入了房间>\n'.encode('utf-8'))

    def remove(self, session):
        if session.name and session.name in self.server.users:
            del self.server.users[session.name]
        Room.remove(self, session)
        self.broadcast(f'< {session.name} 退出了房间>\n'.encode('utf-8'))

    def do_say(self, session, line):
        """广播聊天消息"""
        self.broadcast(f'{session.name}: {line}\n'.encode('utf-8'))

    def do_look(self, session, line):
        """查询当前在线用户"""
        session.push(b'Online Users:\n')
        for user in self.sessions:
            if user.name:
                session.push((user.name + '\n').encode('utf-8'))


class LogoutRoom(Room):
    """处理退出的用户，仅做清理工作"""

    def add(self, session):
        # 不调用 Room.add()，LogoutRoom 不需要维护 sessions 列表
        if session.name and session.name in self.server.users:
            del self.server.users[session.name]
            print(f'用户 {session.name} 离线啦')
        else:
            print(f'未登录用户断开连接')


def start_server():
    IP = "127.0.0.1"
    PORT = 6666
    ChatServer(IP, PORT)
    print(f'服务器已经在 {IP}:{PORT} 开始运行...')
    asyncore.loop()


if __name__ == '__main__':
    start_server()