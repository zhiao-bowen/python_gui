import base64
import telnetlib
import tkinter as tk
from io import BytesIO

import socket
from PIL import Image, ImageTk
from tkinter import messagebox, scrolledtext
import img


# ==================== 开始窗口 ====================
def Win_start():
    global root, ent_username
    root = tk.Tk()
    root.title('Chat & Tran')
    center_window(root, 300, 370)
    root.resizable(False, False)
    photo = ImageTk.PhotoImage(Code_to_img(img.code_start))
    label_bg = tk.Label(width=300, height=375, image=photo)
    label_bg.pack()

    # 登入按钮
    def fun_but_login():
        conn = telnetlib.Telnet()
        Win_main(conn)

    but_login = tk.Button(root, bg='#84c1ff', width=8, font=("Kaiti", 14),
                          text='登录', command=fun_but_login)
    but_login.place(x=105, y=250)
    root.bind('<Return>', lambda event: fun_but_login())

    def on_enter_l(event):
        but_login.config(bg="#4efeb3")

    def on_leave_l(event):
        but_login.config(bg='#84c1ff')

    but_login.bind("<Enter>", on_enter_l)
    but_login.bind("<Leave>", on_leave_l)

    # 退出按钮
    but_exit = tk.Button(root, bg='#84c1ff', width=8, font=("Kaiti", 14),
                         text='退出', command=root.destroy)
    but_exit.place(x=105, y=300)

    def on_enter_e(event):
        but_exit.config(bg="#ff9797")

    def on_leave_e(event):
        but_exit.config(bg='#84c1ff')

    but_exit.bind("<Enter>", on_enter_e)
    but_exit.bind("<Leave>", on_leave_e)

    # 帮助按钮
    but_tip = tk.Button(root, bg='#ff9224', text='帮助', command=Win_tip)
    but_tip.place(x=265, y=0)

    def on_enter_t(event):
        but_tip.config(bg="#ffffaa")

    def on_leave_t(event):
        but_tip.config(bg='#ff9224')

    but_tip.bind("<Enter>", on_enter_t)
    but_tip.bind("<Leave>", on_leave_t)

    # 输入框占位提示
    def on_entry_click(event):
        if ent_username.get() == '输入昵称':
            ent_username.delete(0, tk.END)
            ent_username.config(fg='black')

    ent_username = tk.Entry(root, bg="#ceceff", width=10, font=("Kaiti", 14))
    ent_username.place(x=98, y=200)
    ent_username.insert(0, '输入昵称')
    ent_username.config(fg='grey')
    ent_username.bind('<FocusIn>', on_entry_click)

    root.mainloop()


# ==================== 帮助窗口 ====================
def Win_tip():
    root.destroy()

    tip = tk.Tk()
    tip.title('Chat & Tran')
    center_window(tip, 300, 370)
    tip.resizable(False, False)
    photo = ImageTk.PhotoImage(Code_to_img(img.code_main))
    label_bg = tk.Label(width=300, height=375, image=photo)
    label_bg.pack()

    tip_str = '使用方法：\n不用注册，直接输入昵称即可使用！'
    label_tip = tk.Label(tip, bg="#ceceff", width=33, font=("Kaiti", 13), text=tip_str)
    label_tip.place(x=0, y=50)
    tip.mainloop()

    Win_start()


# ==================== 主聊天窗口 ====================
def Win_main(conn):
    username = ent_username.get().strip()
    if username == '输入昵称':
        username = ''

    # 【修复1】空用户名不建立连接，避免服务端产生无效 session
    if not username:
        messagebox.showwarning('提示', '请输入用户名')
        return

    # 【修复2】连接失败 / 登录失败时均关闭连接，防止服务端 NoneType.remove
    try:
        conn.open("127.0.0.1", 6666, timeout=10)
    except (socket.error, OSError):
        messagebox.showwarning('提示', '连接失败，请检查服务器设置')
        conn.close()
        return

    try:
        # 【修复3】用 read_until 替代 read_some，确保读到完整响应行
        resp = conn.read_until(b'\n', timeout=5).strip()
        if resp != b'Connect Success':
            messagebox.showwarning('提示', f'服务器响应异常: {resp}')
            conn.close()
            return

        conn.write(('login ' + username + '\n').encode('utf-8'))

        resp = conn.read_until(b'\n', timeout=5).strip()
        if resp == b'Username exists':
            messagebox.showwarning('提示', '用户名已存在')
            conn.close()
            return
        elif resp == b'Username empty':
            messagebox.showwarning('提示', '用户名不能为空')
            conn.close()
            return
        elif resp != b'login success':
            messagebox.showwarning('提示', f'登录失败: {resp}')
            conn.close()
            return

        messagebox.showinfo('提示', '登录成功')

    except Exception as e:
        messagebox.showwarning('提示', f'登录过程出错: {e}')
        conn.close()
        return

    # 登录成功后才销毁启动窗口
    root.destroy()

    # ---------- 构建聊天界面 ----------
    main = tk.Tk()
    main.title('Chat & Tran')
    center_window(main, 400, 400)
    main.resizable(False, False)
    photo = ImageTk.PhotoImage(Code_to_img(img.code_main))
    label_bg = tk.Label(main, width=400, height=400, image=photo)
    label_bg.pack()

    label_username = tk.Label(main, bg='#ffbb77', font=('KaiTi', 15),
                              text=f'（{username}）聊天窗口:')
    label_username.place(x=0, y=0)

    text_box = scrolledtext.ScrolledText(main, bg='#00caca', font=('KaiTi', 15),
                                         width=35, height=15)
    text_box.place(x=15, y=40)

    ent_send = tk.Entry(main, width=24, font=('KaiTi', 18))
    ent_send.place(x=15, y=355)

    def send_msg():
        msg = ent_send.get().strip()
        if msg:
            conn.write(('say ' + msg + '\n').encode('utf-8'))
            ent_send.delete(0, tk.END)

    but_send = tk.Button(main, width=8, text='发送', command=send_msg)
    but_send.place(x=320, y=355)
    main.bind('<Return>', lambda event: send_msg())

    # 【修复4】窗口关闭时主动通知服务端并断开连接
    def on_closing():
        try:
            conn.write(b'logout\n')
        except Exception:
            pass
        finally:
            conn.close()
            main.destroy()

    main.protocol("WM_DELETE_WINDOW", on_closing)

    # 【修复5】带缓冲区的消息接收，正确处理 TCP 粘包/拆包
    recv_buffer = b''

    def update():
        nonlocal recv_buffer
        try:
            data = conn.read_very_eager()
            if data:
                recv_buffer += data
                while b'\n' in recv_buffer:
                    line, recv_buffer = recv_buffer.split(b'\n', 1)
                    text = line.decode('utf-8', errors='replace').strip()
                    if not text:
                        continue
                    if text.startswith('Online Users:'):
                        messagebox.showinfo('当前在线用户', text)
                    else:
                        text_box.insert(tk.END, text + '\n')
                        text_box.see(tk.END)
        except EOFError:
            text_box.insert(tk.END, '\n[服务器已断开连接]\n')
            text_box.see(tk.END)
            return  # 停止轮询
        except Exception:
            pass

        if main.winfo_exists():
            main.after(100, update)

    update()
    main.mainloop()


# ==================== 工具函数 ====================
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry('%dx%d+%d+%d' % (width, height, x, y))


def Code_to_img(code_v):
    im_data = base64.b64decode(code_v)
    return Image.open(BytesIO(im_data))


if __name__ == "__main__":
    Win_start()