import tkinter.messagebox
from tkinter import *
import os.path
import configparser
import cryptocode
import win32security
import subprocess

settings = configparser.ConfigParser()
settings.read('settings.ini')

width = 330
height = 220


def center(win, w, h):
    """
    centers a tkinter window
    :param w: width win
    :param h: height win
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    # width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = w + 2 * frm_width
    # height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = h + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(w, h, x, y))
    win.deiconify()


def normal(word=''):
    layout = dict(zip(map(ord, "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                               'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'),
                      "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                      'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'))
    log = login.translate(layout).lower()
    pas = password.translate(layout)
    if word == 'login':
        return log
    if word == 'password':
        return pas
    return log, pas


login = ''
password = ''
current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
desc = win32security.GetFileSecurity(".", win32security.OWNER_SECURITY_INFORMATION)
sid = desc.GetSecurityDescriptorOwner()
sidstr = win32security.ConvertSidToStringSid(sid)
key = current_machine_id[-12:] + sidstr[-15:-5] + current_machine_id[:8] + sidstr[-4:]


def return_id():
    return login, password


def btn_click():
    global login
    global password
    login = loginInput.get()
    password = passInput.get()
    login = normal('login')
    password = normal('password')
    rem = remember_value.get()
    if rem == 'Yes':
        login_crypt = cryptocode.encrypt(login, key)
        password_crypt = cryptocode.encrypt(password, key)
        settings.set('autorization', 'avtologin', 'yes')
        settings.set('autorization', 'login', login_crypt)
        settings.set('autorization', 'password', password_crypt)
    else:
        login_crypt = cryptocode.encrypt('paste_login', key)
        password_crypt = cryptocode.encrypt('paste_pass', key)
        settings.set('autorization', 'avtologin', 'no')
        settings.set('autorization', 'login', login_crypt)
        settings.set('autorization', 'password', password_crypt)
    with open('settings.ini', 'w') as configfile:
        settings.write(configfile)
    root.destroy()


root = Tk()

if os.path.isfile('rosreestr.png'):
    photo = tkinter.PhotoImage(file='rosreestr.png')
    root.iconphoto(False, photo)  # смена иконки
root['bg'] = '#fafafa'
root.resizable(False, False)  # не изменять размеры
root.title('Форма для авторизации')
center(root, width, height)  # вызываем функцию центровки окна
root.attributes('-topmost', 1)  # поверх окон
# root.wm_attributes('-alpha', 0.7) # прозрачность
root.geometry(f'{width}x{height}')  # размер и сдвиг в пикселях
remember_value = StringVar()

canvas = Canvas(root, height=200, width=300, bg='#EBE8DB')
canvas.pack()

frame = Frame(root, bg='#71D8E8')
frame.place(relx=0.15, rely=0.15, relwidth=0.7, relheight=0.7)

title = Label(frame, text='Введите логин и пароль от ФГИС', bg='gray')
title.pack()

loginInput = Entry(frame, bg='white')
loginInput.pack(pady=10)
passInput = Entry(frame, show="*", bg='white')
passInput.pack()

remember = Checkbutton(frame, text='запомнить пароль', bg='white', variable=remember_value, offvalue='No',
                       onvalue='Yes', relief='groove', bd=2)
remember.pack(pady=5)

btn = Button(frame, text='Ввод', bg='#51CB38', command=btn_click, relief=tkinter.RAISED, bd=3)
btn.pack(pady=10)

loginInput.insert(0, cryptocode.decrypt(settings['autorization']['login'], key))
passInput.insert(0, cryptocode.decrypt(settings['autorization']['password'], key))

if settings['autorization']['avtologin'] == 'yes':
    remember_value.set("Yes")
else:
    remember_value.set("No")


def btn_enter(event):
    btn_click()


root.bind('<Return>', btn_enter)  # кнопка Ввод по нажатию Enter

root.mainloop()

if __name__ == '__main__':
    print(return_id())
