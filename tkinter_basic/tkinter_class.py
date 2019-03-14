#C:\Python27\Doc python
#--encoding=UTF-8--
__author__='Sean Wang'
#data@:2016-10-13
# coding=utf8
# coding=gbk
#print out.decode('gbk').encode('utf-8')   #output have Chinese word and English word

from Tkinter import *
import Tkinter as tk
from ttk import *
from tkMessageBox import *
from tkFileDialog import *
from tkSimpleDialog import askstring
from telnetlib import Telnet
#from E7.SLV384.deco_slv import addspam, slv_log, locker, deco, log_pa
import multiprocessing
import subprocess, string
import os, sys, logging, datetime, time
import re as sre
import telnetlib
from multiprocessing import Process
import tkMessageBox



# rePrompt                  = sre.compile('E3VCP\d+>')
# redebugPrompt             = sre.compile('\w+>')
# reTL1Prompt               = sre.compile('\w+\d+>|\w+\.>')
# reShellPrompt             = sre.compile('\w+:\d+\.\d+:>|\w+\d+:\d+\.\d+:>')
# reLinuxPrompt             = sre.compile('\S*\:\~\#')
# reLoginPrompt             = sre.compile('login: ',    sre.IGNORECASE)
# rePasswordPrompt          = sre.compile('Password: ',    sre.IGNORECASE)
# reConfirmPrompt           = sre.compile('y/n',    sre.IGNORECASE)
# reAXOSConfirmPrompt       =  sre.compile('~# ',    sre.IGNORECASE)
# reAXOSCLIPrompt           =  sre.compile('# ',    sre.IGNORECASE)


rePrompt                    =  sre.compile('\w+\d+>')
reTL1Prompt                 =  sre.compile('\w+\d+>|\w+\.>')
reShellPrompt               =  sre.compile('\w+:\d+\.\d+:>|\w+\d+:\d+\.\d+:>')
reLinuxPrompt               =  sre.compile('\w+# ')
reC7Prompt                  =  sre.compile('COMPLD|DENY')    #This is for C7 TL1 specically, TL1 command not need 'COMPLD' instead of self.enter
reLoginPrompt               =  sre.compile('\w+\s+login:',    sre.IGNORECASE)
rePasswordPrompt            =  sre.compile('Password:',    sre.IGNORECASE)
reConfirmPrompt             =  sre.compile('y/N',    sre.IGNORECASE)
reAXOSConfirmPrompt         =  sre.compile('~# ',    sre.IGNORECASE)
reAccuteConfirmPrompt         =  sre.compile('E3VCP>',    sre.IGNORECASE)

filename=''
connected=None

class bar_label(object):
    def __init__(self):
        pass

    def author(self):
        showinfo('作者信息', '本软件由Sean Wang研究出来的')

    def about(self):
        showinfo('版权信息.Copyright.V1.0', '本软件归属Maojun Wang，哈哈！')


    def E3_help(self):
        """show help info"""
        tkMessageBox.showinfo("help",
                              """Maojun using command manual
  -----------------------------------------------------------------
  1. IP&cmd: Telnet IP(please enter you eqpt ip), cmd(please enter cli command)
  2. Listbox: click mouse left key to selected IP to Telenet
  3. Version: check E3 system version.
  4. UPGRADE E3: upgrade E3 all IPs..
  5. Release version: can enter by yourself.
  6. Please send email to maojunwan@163.com if you find any bugs, thanks.
  ------------------------------------------------------------------""")

    def openfile(self):
        global filename
        filename = askopenfilename(defaultextension='.txt')
        if filename == '':
            filename = None
        else:
            root.title('FileName:' + os.path.basename(filename))
            textPad.delete(1.0, END)
            f = open(filename, 'r')
            textPad.insert(1.0, f.read())
            f.close()

    def new(self):
        global filename
        root.title('New file')
        filename = None
        textPad.delete(1.0, END)

    def save(self):
        global filename
        try:
            f = open(filename, 'w')
            msg = textPad.get(1.0, END)
            f.write(msg)
            f.close
        except:
            save_as()

    def save_as(self):
        f = asksaveasfilename(initialfile='New.txt', defaultextension='.txt')
        global filename
        filename = f
        fh = open(f, 'w+')
        if fh:
            msg = textPad.get(1.0, END)
            fh.write(msg)
            fh.close()
        root.title('FileName:' + os.path.basename(f))

    def cut(self):
        textPad.event_generate('<<Cut>>')

    def copy(self):
        textPad.event_generate('<<Copy>>')

    def paste(self):
        textPad.event_generate('<<Paste>>')

    def redo(self):
        textPad.event_generate('<<Redo>>')

    def undo(self):
        textPad.event_generate('<<Undo>>')

    def selectAll(self):
        textPad.tag_add('sel', '1.0', END)

    ##Find replace with search
    # def search():
    #     topsearch=Toplevel(root)
    #     topsearch.geometry('300x30+200+250')
    #     label1=Label(topsearch,text='Find')
    #     label1.grid(row=0, column=0, padx=5)
    #     entry1=Entry(topsearch, width=20)
    #     entry1.grid(row=0, column=1, padx=5)
    #     button1=Button(topsearch,text='查找')
    #     button1.grid(row=0, column=2)

    def onFind(self):
        target = askstring('SimpleEditor', 'Search String?')
        if target:
            where = textPad.search(target, INSERT, END)
            if where:
                print where
                pastit = where + ('+%dc' % len(target))
                # text.tag_remove(SEL, '1.0', END)
                textPad.tag_add(SEL, where, pastit)
                textPad.mark_set(INSERT, pastit)
                textPad.see(INSERT)
                textPad.focus()

# ne = bar_label()


class Example():

    def __init__(self):
        self.promptList = [rePrompt, reTL1Prompt, reShellPrompt, reLinuxPrompt, reLoginPrompt, rePasswordPrompt,
                           reConfirmPrompt, reC7Prompt, reAXOSConfirmPrompt, reAccuteConfirmPrompt]
        self.timeout = 15
        self.enter='\r'
        self.Tel = ''

    # def __call__(self, E7, x):  ##__call__ will be using by func(func, *args), E(E, *args)   ##This will cause multi process running then show error
    #     print getattr(E7, '__init__', '__init__ Telnet not find')
    #     if hasattr(E7, '__init__'):
    #         print "E7 has __init__ function"
    #         setattr(E7, 'timeout', 100)
    #     print E7.timeout
    #     return "%s running with __call__" % x

    def session(self, host):
        print "telnet host is: ", host
        try:
            self.Tel = Telnet(host, '23', self.timeout)
            self.Tel.set_debuglevel(0)
            connected = True
            return connected
        except Exception, ex:
            Tel_error=re.compile('((\*Errno)|(\*timed out))')
            if Tel_error.search(str(ex)):
                print '*' * 100 + '\n' + str(ex) + '\n' + '*' * 100
            connected=False
        return "Telnet successfully!!!" + '\n\r' * 2

    def cli_command(self, *args):
        log = ''
        self.Tel.write(args[0] + self.enter)
        res =self.Tel.expect(self.promptList, self.timeout)
        # logging.warning(self.enter + res[2])
        return res[2]

    def cli_command_run(self, *args):
        log = ''
        self.Tel.write(args[0] + self.enter)
        res =self.Tel.expect(self.promptList, self.timeout)
        # logging.warning(self.enter + res[2])
        # print res[2]
        return res

    def version(self):
        ip = content_ip.get()
        print "Lb1.curselection() value: ", Lb1.curselection()
        if ip == '' and Lb1.curselection() == ():
            tkMessageBox.showwarning("Warning", "Please enter IP or selected IP")
            if Lb1.curselection() != ():
                ip = Lb1.get(Lb1.curselection())
                print ip
            else:
                pass
        elif content_ip.get() or Lb1.get(Lb1.curselection()):
            if content_ip.get():
                ip = content_ip.get()
            else:
                ip = Lb1.get(Lb1.curselection())
            self.session(ip)
            steps = '''e3support
                                admin
                                set se pa di ti di'''
            for step in steps.split('\n'):
                self.cli_command(step.strip())
            version_content = self.cli_command("show version")
            version = sre.compile("\d+.\d+.\d+.\d+")
            version_match = version.search(version_content)
            version_split = version_content.split("\r\n")
            print version_split
            print "Running version: ", version_split[1].split(":")[1]
            print "Committed version: ", version_split[2].split(":")[1]
            print "Alternate version: ", version_split[3].split(":")[1]
            for res in version_match.group():
                # E3.insert(END, res)
                pass
            return version_match.group()
        else:
            tkMessageBox.showwarning("Warning", "Please enter IP first!")







    def tel_e3(self):
        ip = content_ip.get()
        # ip  = '10.245.46.10'
        if ip:
            self.session(ip)
            print "-------------log into E3 !!!!--------------------"
            steps='''e3support
                                admin
                                set se pa di ti di
                                debug
                                cd envmgr
                                temp display
                                exit'''
            # steps = '''#This is for AXOS system slowly respond with switch to LINUX interface
            #             root
            #             root
            #             cli
            #             cli
            #             paginate false
            #             show card
            #             show run slot'''
            for step in steps.split('\n'):
                self.cli_command(step.strip())
            print "--------------login successfully-----------------"
            self.manual_msg()
        return None

    def tel_e7(self):
        ip = content_ip.get()
        ip = '10.245.46.205'
        if ip:
            self.session(ip)
            print "-------------log into e7 !!!!--------------------"
            steps='''e7support
                                admin
                                set se pa di ti di
                                show card
                                show version
                                show mcast
                                show dhcp lease'''
            for step in steps.split('\n'):
                self.cli_command(step.strip())
            print "--------------login successfully-----------------"
            msg=content_cli.get().encode('gbk')
            self.manual_msg()
        return None



    def tel_e7_TPS(self, ip):
        try:
            self.session(ip)
            print "-------------log into e7_TPS !!!!--------------------"
            steps='''e7support
                                admin
                                set se pa di ti di
                                set session event-notif disabled
                                set session alarm-notif disabled
                                show card'''
            for step in steps.split('\n'):
                self.cli_command(step.strip())
            print "--------------login successfully-----------------"
        except:
            print "telnet e7 error!"
        return None

    def tel_axos(self, content_ip_axos):
        res = []
        if content_ip_axos.get():
            self.session(content_ip_axos.get())
            print "-------------log into AXOS 35B !!!!--------------------"
            steps='''#this is axos system, welcome in!
                                root
                                root
                                cli
                                cli
                                idle-timeout
                                paginate false
                                show run slot 1/1'''
            for step in steps.split('\n'):
                res = self.cli_command(step.strip())
        if res:
            return res[2]


    """
    upgrade 5 E3 card to the newest version
    """
    # @log_pa("telnet to E3")
    def E3_run(self, *args):
        ip, card, vector, times = args
        tn = lib_card_E3()
        upgrade_version = content_ver.get().encode('gbk')
        if upgrade_version == "":
            upgrade_version = self.version()
            steps = '''e3support
                                admin
                                commit system version %s''' % upgrade_version
        else:
            steps = '''e3support
                                admin
                                set se pa di ti di
                                set session event-notif disabled
                                set session alarm-notif disabled
                                upgrade system server 10.245.46.202 user sean directory-path \ version %s reset
                                sean'''% upgrade_version
        print "Telnet ip is: ", ip
        try:
            Session = telnetlib.Telnet(ip, port=23)
            Session.set_debuglevel(0)
            for step in steps.split('\n'):
                tn.E3_command(Session, step.strip(), self.promptList)

            Session.close()
            self.manual_msg()

        except Exception, ex:
            tel_error = sre.compile(r"((error)|(time))")
            if tel_error.search(str(ex)):
                print '*' * 100 + '\r\n' + ex + '\r\n' + '*' * 100
        return "thread running successfully"

    def upgrade(self):
        """    E7 change card mode with threading on different shelves    """
        E3IPs = [ '10.245.47.231', '10.245.47.232', '10.245.47.233', '10.245.47.234', '10.245.47.235']
        for i in E3IPs:
            vector = ['vector', 'nonvector']
            times = 3
            card = "1/1"
            self.E3_run(i, card, vector[1], times)
            # pool = multiprocessing.Pool(processes=4)
            # for ip in E3IPs:
            #     pool.apply_async(E3_run, args=(ip, card, vector[1], times))  # thread running two E7 process
            # pool.close()
            # pool.join()
            print "Sub-process(es) done."

    def today_news(self):
        import requests
        from bs4 import BeautifulSoup
        # import urllib3
        from urllib3.packages import six
        total_news =''
        url = "http://news.qq.com/"
        # 请求腾讯新闻的URL，获取其text文本
        wbdata = requests.get(url).text
        # 对获取到的文本进行解析
        soup = BeautifulSoup(wbdata, 'lxml')
        # 从解析文件中通过select选择器定位指定的元素，返回一个列表
        news_titles = soup.select("div.text > em.f14 > a.linkto")
        # news_titles_sohu= soup.select("div.focus-news> div.news> a.href")

        # 对返回的列表进行遍历
        for n in news_titles:
            title = n.get_text()
            link = n.get("href")
            data = {
                '标题': title,
                '链接': link
            }
            for news in data.values():
                total_news += (news + '\r\n')
        return total_news
        #         textPad.insert(END, news + '\r\n')
        # textPad.insert(END, "news.qq.com as above....")
        # return None
# from axos_tel import Example
# E7=Example()

class third_party(object):
    def __init__(self):
        """
        Matlib running in process
        """
        import numpy as np
        # import matplotlib.pyplot as plt

    def matlib_autolabel(self):
        pass
        # x_N = 5
        # menMeans = (20, 35, 30, 35, 27)
        # menStd =   (2, 3, 4, 1, 2)
        #
        # ind = np.arange(x_N)  # the x locations for the groups
        # width = 0.35       # the width of the bars
        #
        # fig, ax = plt.subplots()
        # rects1 = ax.bar(ind, menMeans, width, color='r', yerr=menStd)
        #
        # womenMeans = (25, 32, 34, 20, 25)
        # womenStd =   (3, 5, 2, 3, 3)
        # rects2 = ax.bar(ind+width, womenMeans, width, color='y', yerr=womenStd)
        #
        # # add some
        # ax.set_ylabel('Scores')
        # ax.set_title('Scores by group and gender')
        # ax.set_xticks(ind+width)
        # ax.set_xticklabels( ('G1', 'G2', 'G3', 'G4', 'G5') )
        # ax.legend( (rects1[0], rects2[0]), ('Men', 'Women') )
        #
        # def autolabel(rects):
        #     # attach some text labels
        #     for rect in rects:
        #         height = rect.get_height()
        #         ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
        #                 ha='center', va='bottom')
        #
        # autolabel(rects1)
        # autolabel(rects2)
        # plt.show()

    # from matlib_traincount import train_count_run, matlib_run
    def matlib_1(self):
        pass
        # session_matlib = matlib_run()
        # train_count_run(session_matlib)


class tk_gui(bar_label, Example, third_party):
    def __init__(self):
        super(tk_gui, self).__init__()
        Example.__init__(self)
        third_party.__init__(self)
        self.root = Tk()
        self.root.title('本软件归属Maojun，哈哈！')
        self.root.geometry("850x800+100+100")
        # root.geometry('1100x350+500+300')
        self.root.option_add("*Font", "宋体")

        # CLI command output to text
        self.textPad = Text(self.root, undo=True)
        self.textPad.pack(side=BOTTOM, expand=YES, fill=BOTH)
        scroll = Scrollbar(self.textPad)
        self.textPad.config(yscrollcommand=scroll.set)
        scroll.config(command=self.textPad.yview)
        scroll.pack(side=RIGHT, fill=BOTH)

        # create menu
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        filemenu = Menu(menubar)
        filemenu.add_command(label='新建', accelerator='Ctrl + N', command=self.new)
        filemenu.add_command(label='打开', accelerator='Ctrl + O', command=self.openfile)
        filemenu.add_command(label='保存', accelerator='Ctrl + S', command=self.save)
        filemenu.add_command(label='另存为', accelerator='Ctrl + Shife + S', command=self.save_as)
        menubar.add_cascade(label='文件', menu=filemenu)

        editmenu = Menu(menubar)
        editmenu.add_command(label='撤销', accelerator='Ctrl + Z', command=self.undo)
        editmenu.add_command(label='重做', accelerator='Ctrl + Y', command=self.redo)
        editmenu.add_separator()
        editmenu.add_command(label='剪切', accelerator='Ctrl + X', command=self.cut)
        editmenu.add_command(label='复制', accelerator='Ctrl + C', command=self.copy)
        editmenu.add_command(label='粘贴', accelerator='Ctrl + V', command=self.paste)
        editmenu.add_separator()
        editmenu.add_command(label='查找', accelerator='Ctrl + F', command=self.onFind)
        editmenu.add_command(label='全选', accelerator='Ctrl + A', command=self.selectAll)
        menubar.add_cascade(label='编辑', menu=editmenu)

        aboutmenu = Menu(menubar)
        aboutmenu.add_command(label='作者', command=self.author)
        aboutmenu.add_command(label='版权', command=self.about)
        aboutmenu.add_command(label='Help', command=self.E3_help)
        menubar.add_cascade(label='关于', menu=aboutmenu)


        # Left button running
        note = Notebook(self.root)
        toolbar = Frame(note, height=25, )
        toolbar_1 = Frame(note, height=25, )
        toolbar_2 = Frame(note, height=25, )

        # button image setting
        from PIL import Image, ImageTk
        image_home = Image.open('.\\basic\\image\\home.png')
        im_home = ImageTk.PhotoImage(image_home)
        image_save = Image.open('.\\basic\\image\\save.png')
        im_save = ImageTk.PhotoImage(image_save)
        image_run = Image.open('.\\basic\\image\\run.png')
        im_run = ImageTk.PhotoImage(image_run)
        image_clear = Image.open('.\\basic\\image\\clear.png')
        im_clear = ImageTk.PhotoImage(image_clear)
        image_matlib_1 = Image.open('.\\basic\\image\\matlib_1.png')
        im_matlib_1 = ImageTk.PhotoImage(image_matlib_1)

        E7_button_wid = 5
        E3_button_wid = 10



        #   E7 PAGE
        shortButton_0 = Button(toolbar, text='New', image=im_home, width=E7_button_wid, command=self.openfile).pack(
            side=LEFT, padx=2, pady=2)
        shortButton_1 = Button(toolbar, text='Save', image=im_save, width=E7_button_wid, command=self.save).pack(side=LEFT,
                                                                                                            padx=2,
                                                                                                            pady=2)
        shortButton_2 = Button(toolbar, text='Run', image=im_run, width=E7_button_wid, command=self.tel_e7_TPS_run).pack(
            side=LEFT, padx=5, pady=5)
        shortButton_3 = Button(toolbar, text='Clear', image=im_clear, width=E7_button_wid,
                               command=self.clear_textpad).pack(side=LEFT, padx=5, pady=5)

        #   E3 PAGE
        shortButton_4 = Button(toolbar_1, text='Upgrade E3', width=E3_button_wid, command=self.upgrade).pack(side=LEFT,
                                                                                                           padx=5,
                                                                                                           pady=5)
        shortButton_5 = Button(toolbar_1, text='E3Version', width=E3_button_wid, command=self.version).pack(side=LEFT,
                                                                                                          padx=5,
                                                                                                          pady=5)
        shortButton_7 = Button(toolbar_1, text='Matlib_1', width=E3_button_wid, command=self.matlib_1).pack(side=LEFT,
                                                                                                       padx=5, pady=5)
        shortButton_6 = Button(toolbar_1, text='Matlib', image=im_matlib_1, width=E3_button_wid,
                               command=self.matlib_autolabel)
        shortButton_6.pack(side=LEFT, padx=5, pady=5)
        shortButton_6.bind("aaaa")

        #   AXOS PAGE
        shortButton_31 = Button(toolbar_2, text='TEL_AXOS', width=E3_button_wid, command=self.tel_axos_run).pack(side=LEFT,
                                                                                                           padx=5,
                                                                                                           pady=5)
        shortButton_32 = Button(toolbar_2, text='RUN_command', width=E3_button_wid, command=self.manual_msg_axos).pack(
            side=LEFT, padx=5, pady=5)
        shortButton_32 = Button(toolbar_2, text='今日新闻', width=E3_button_wid, command=self.news_run).pack(side=LEFT,
                                                                                                         padx=5, pady=5)

        toolbar.pack(expand=NO, fill=X)

        # For scroll listbox
        scrollbar = Scrollbar(toolbar)
        scrollbar.pack(side=RIGHT, fill=Y)

        def printList(event):
            if self.Lb1.curselection():
                print "Listbox value:", self.Lb1.get(self.Lb1.curselection())

        self.Lb1 = Listbox(toolbar, yscrollcommand=scrollbar.set, selectmode=MULTIPLE, height=1, width=15)
        E3_E7_IPs = ['10.245.46.205', '10.245.47.231', '10.245.46.10', '10.245.59.210', '10.245.59.215']
        for ip_item in E3_E7_IPs:
            self.Lb1.insert(END, ip_item)
        self.Lb1.bind('<Double-Button-1>', printList)
        self.Lb1.pack(side=RIGHT)
        scrollbar.config(command=self.Lb1.yview)

        # Bottom for showing up current time
        # status=Label(root,text='TELNET SESSION',anchor=N).pack(side=BOTTOM, fill=X)  #relief= SUNKEN Label will sink down
        Label_time = Label(self.root, text=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), anchor=N,
                           font='Helvetica -16 bold')  # anchor =N is location
        Label_time.pack(side=BOTTOM, fill=X)

        def trickit():
            currentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            Label_time.config(text=currentTime, )  # background="light gray")
            self.root.update()
            Label_time.after(1000, trickit)

        Label_time.after(1000, trickit)

        # LEFT LINE & RIGHT LINE
        lnlabel_left = Label(self.root, width=1, ).pack(side=LEFT, fill=Y)
        lnlabel_right = Label(self.root, width=1, ).pack(side=RIGHT, fill=Y)

        #   E7 PAGE
        # Input CLI command value
        Entrybar_IP = Frame(toolbar, height=25)
        Entrybar_IP.pack(expand=YES, fill=X)
        L1 = Label(Entrybar_IP, text="IP").pack(side=LEFT, padx=5, pady=5)
        self.content_ip = StringVar()
        E1 = Entry(Entrybar_IP, textvariable=self.content_ip).pack(side=LEFT, padx=5, pady=5)

        # Input CLI command value
        Entrybar_cmd = Frame(toolbar, height=25)
        Entrybar_cmd.pack(expand=YES, fill=X)
        L1 = Label(Entrybar_cmd, text="Cmd").pack(side=LEFT, padx=5, pady=5)
        self.content_cli = StringVar()
        E2 = Entry(Entrybar_cmd, textvariable=self.content_cli).pack(side=LEFT, padx=5, pady=5)

        #   E3 PAGE
        # Input Version value
        Entrybar_ver = Frame(toolbar_1, height=25)
        Entrybar_ver.pack(side=LEFT, padx=5, pady=5)  # (expand=NO, fill=X)  will show different location
        L1 = Label(Entrybar_ver, text="Release Version").pack(side=LEFT, padx=5, pady=5)
        self.content_ver = StringVar()
        E3 = Entry(Entrybar_ver, textvariable=self.content_ver)
        E3.pack(side=LEFT, padx=5, pady=5)

        # (Rigth part click button running)
        self.CheckVar1 = IntVar()
        CheckVar2 = IntVar()
        CheckVar3 = IntVar()
        C1 = Checkbutton(toolbar_1, text="59.210", variable=self.CheckVar1, onvalue=1, offvalue=0,
                         command=self.tel_e7_TPS_run).pack(side=LEFT, padx=5, pady=5)
        C2 = Checkbutton(toolbar_1, text="46.205", variable=CheckVar2, onvalue=1, offvalue=0, command=self.tel_e7).pack(
            side=LEFT, padx=5, pady=5)
        C3 = Checkbutton(toolbar_1, text="46.10", variable=CheckVar3, onvalue=1, offvalue=0, command=self.tel_e3).pack(
            side=LEFT, padx=5, pady=5)

        print "c1,c2,c3:", self.CheckVar1.get(), C2, C3

        #   AXOS PAGE
        # Input CLI command value
        Entrybar_IP = Frame(toolbar_2, height=25)
        Entrybar_IP.pack(expand=YES, fill=X)
        L11 = Label(Entrybar_IP, text="IP").pack(side=LEFT, padx=5, pady=5)
        self.content_ip_axos = StringVar()
        self.content_ip_axos.set('10.245.47.10')
        E11 = Entry(Entrybar_IP, textvariable=self.content_ip_axos).pack(side=LEFT, padx=5, pady=5)

        # Input CLI command value
        Entrybar_cmd = Frame(toolbar_2, height=25)
        Entrybar_cmd.pack(expand=YES, fill=X)
        L11 = Label(Entrybar_cmd, text="Cmd").pack(side=LEFT, padx=15, pady=5)
        self.content_cli_axos = StringVar()
        self.content_cli_axos.set('show card/show ver')
        self.content_cli_axos.trace_vinfo()
        E12 = Entry(Entrybar_cmd, textvariable=self.content_cli_axos).pack(side=LEFT, padx=15, pady=15)

        # Input Version value
        Entrybar_ver = Frame(toolbar_2, height=25)
        Entrybar_ver.pack(side=RIGHT, fill=Y)  # (expand=NO, fill=X)  will show different location
        L11 = Label(Entrybar_ver, text="Version").pack(side=LEFT, padx=5, pady=5)
        self.content_ver_axos = StringVar()
        E13 = Entry(Entrybar_ver, textvariable=self.content_ver_axos)
        E13.pack(side=LEFT, padx=5, pady=5)

        self.CheckVar11 = IntVar()
        C11 = Checkbutton(toolbar_2, text="loop 5 times", variable=self.CheckVar11, onvalue=1, offvalue=0,
                          command=None).pack(side=LEFT, padx=5, pady=5)

        # PAGE.add(tab1, text = "Tab One",image=scheduledimage, compound=TOP)
        note.add(toolbar_2, text="MILAN system")
        note.add(toolbar, text="E7 system")
        note.add(toolbar_1, text="E3 system")
        note.pack(side=TOP, fill=BOTH)

        self.root.mainloop()

    def tel_e7_TPS_run(self):
        ip = self.content_ip.get()
        print "Lb1.curselection() value: ", self.Lb1.curselection(), self.CheckVar1.get()
        if ip == '' and self.Lb1.curselection() == ():
            tkMessageBox.showwarning("Warning", "Please enter IP or selected IP")
            if self.Lb1.curselection() != ():
                ip = self.Lb1.get(self.Lb1.curselection())
                print ip
            else:
                pass
        elif self.content_ip.get() or self.Lb1.get(self.Lb1.curselection()):

            if self.content_ip.get():
                print "ip1:", ip
                ip = self.content_ip.get()
                self.tel_e7_TPS(ip)
            elif self.Lb1.curselection():
                ip = self.Lb1.get(self.Lb1.curselection())
                print "ip:", ip
                self.tel_e7_TPS(ip)
            msg = self.content_cli.get().encode('gbk')
            if msg:
                self.manual_msg(self.content_cli, self.content_ver)


    def manual_msg(self, content_cli, content_ver):
        self.clear_textpad()
        msg_cli = content_cli.get().encode('gbk')
        msg_ver = content_ver.get().encode('gbk')
        if msg_cli or msg_ver:
            print msg_cli, msg_ver
            for msg in msg_cli.split('/'):
                res = self.cli_command_run(msg)
                self.textPad.insert(END, res[2] + '\r\n' + '*' * 100 + '\r\n')  # END will showing up from up to down
        return None


    def tel_axos_run(self):
        if self.tel_axos(self.content_ip_axos):
            self.textPad.insert(END, "--------------login successfully-----------------" + '\r\n')
        else:
            tkMessageBox.showwarning("Warning", "Please enter IP or selected IP")

    def manual_msg_axos(self):
        self.clear_textpad()
        msg_cli_axos = self.content_cli_axos.get().encode('gbk')
        msg_ver_axos = self.content_ver_axos.get().encode('gbk')
        if msg_cli_axos or msg_ver_axos:
            print msg_cli_axos, msg_ver_axos
            for msg in msg_cli_axos.split('/'):
                if self.CheckVar11.get() == 1:
                    loop = 5
                else:
                    loop = 1
                for i in range(loop):
                    print "CheckVar11:", self.CheckVar11.get(), "i value:", i
                    if self.Tel:
                        res = self.cli_run(msg)
                        # self.textPad.insert(END, '\r\n' + res[2])
                        self.textPad.insert(END,
                                            res[2] + '\r\n' + '*' * 100 + '\r\n')  # END will showing up from up to down
                    else:
                        tkMessageBox.showwarning("Warning", "Please telnet to EQPT first")

        return None

    def cli_run(self, msg):
        return self.cli_command_run(msg)

    def news_run(self):
        news = self.today_news()
        self.textPad.insert(END, '\r\n' + news)

    def clear_textpad(self):
        self.textPad.delete(1.0, END)  # END will showing up from up to down


if __name__=="__main__":
    tk_gui()