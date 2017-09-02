#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import copy
import base64
import codecs
import Tkinter
import requests
import traceback
import tkMessageBox
from urllib import urlencode
from requests import Session
from selenium import webdriver

try:
    from tkinter import scrolledtext
except Exception:
    import ScrolledText as scrolledtext

requests.packages.urllib3.disable_warnings()


class LoginFrame(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.loginButton = Tkinter.Button(self, text=u'登录', width=25, height=3, command=self.login)
        self.loginButton.grid(row=0, column=0, padx=150, pady=155)

    def login_baidu(self, user, password):
        self.master.driver.delete_all_cookies()
        self.master.driver.get('https://tieba.baidu.com/index.html')
        login_button = self.master.driver.find_element_by_xpath('//li[@class="u_login"]//a[contains(text(), "登录")]')
        login_button.click()
        user_data = self.master.driver.find_elements_by_xpath('//div[@id="FP_USERDATA"]')
        for i in range(100):
            if user_data:
                break
            elif i == 99:
                return
            time.sleep(0.1)
            user_data = self.master.driver.find_elements_by_xpath('//div[@id="FP_USERDATA"]')
        username_input = self.master.driver.find_element_by_xpath('//input[@id="TANGRAM__PSP_10__userName"]')
        password_input = self.master.driver.find_element_by_xpath('//input[@id="TANGRAM__PSP_10__password"]')
        login_input = self.master.driver.find_element_by_xpath('//input[@id="TANGRAM__PSP_10__submit"]')
        username_input.send_keys(user)
        password_input.send_keys(password)
        for i in range(3):
            try:
                login_input.click()
                break
            except Exception:
                pass
        if self.master.driver.get_cookie('BDUSS'):
            for i in range(100):
                if self.master.driver.get_cookie('STOKEN'):
                    break
                elif i == 99:
                    return
                time.sleep(0.1)
            return self.master.driver.get_cookies()
        else:
            return

    def login(self):
        config_file_path = os.path.join(os.path.abspath(os.path.curdir), 'users_info.json')
        config_file = open(config_file_path, 'r')
        if not os.path.exists(config_file_path):
            tkMessageBox.showinfo(u'提示', u'请在程序运行目录下创建配置文件"users_info.json"')
            return
        try:
            users_info = json.load(config_file)
            if not users_info:
                tkMessageBox.showinfo(u'提示', u'用户信息不存在')
                return
        except Exception:
            tkMessageBox.showinfo(u'提示', u'配置文件异常，请检查修复')
            return
        config_file.close()
        self.master.log_frame.backButton.configure(state='disabled')
        self.pack_forget()
        self.master.log_frame.pack()
        self.master.update()
        user_info_url = 'https://tieba.baidu.com/f/user/json_userinfo?_=%s'
        has_driver = False
        self.master.log_frame.show_log(self.master.cut)
        try:
            for username, keys in users_info.items():
                self.master.log_frame.show_log(u'帐号"%s"正在登录...' % username)
                login_ok = False
                if len(keys) > 1:
                    try:
                        cookies = eval(base64.b64decode(keys[1]))
                        self.master.session.cookies.clear()
                        for cookie in cookies:
                            name = cookie.pop('name')
                            value = cookie.pop('value')
                            cookie.pop('expiry')
                            cookie['expires'] = None
                            cookie['rest'] = {'HttpOnly': cookie.pop('httponly', False)}
                            self.master.session.cookies.set(name, value, **cookie)
                        self.master.session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
                        resp = self.master.session.get(user_info_url % int(time.time() * 1000))
                        self.master.session.headers.pop('X-Requested-With')
                        if resp.content:
                            self.master.cookies[username] = copy.deepcopy(self.master.session.cookies._cookies)
                            login_ok = True
                    except Exception:
                        pass
                if not login_ok:
                    if not has_driver:
                        self.master.driver = self.master.get_driver_by_phantomjs()
                        has_driver = True
                        if not self.master.driver:
                            break
                    try:
                        cookies = self.login_baidu(username, keys[0])
                        if cookies:
                            users_info[username] = [keys[0], base64.b64encode(str(cookies))]
                            config_file = codecs.open(config_file_path, 'w+', 'utf-8')
                            config_file.write(json.dumps(users_info, ensure_ascii=False, indent=4))
                            config_file.close()
                            self.master.session.cookies.clear()
                            for cookie in cookies:
                                name = cookie.pop('name')
                                value = cookie.pop('value')
                                cookie.pop('expiry')
                                cookie['expires'] = None
                                cookie['rest'] = {'HttpOnly': cookie.pop('httponly', False)}
                                self.master.session.cookies.set(name, value, **cookie)
                            self.master.cookies[username] = copy.deepcopy(self.master.session.cookies._cookies)
                            login_ok = True
                    except Exception:
                        raise
                msg = (u'帐号"%s"登录' % username) + (u'成功' if login_ok else u'失败')
                self.master.log_frame.show_log(msg)
            if has_driver and not self.master.driver:
                self.master.log_frame.pack_forget()
                self.pack()
            elif self.master.cookies:
                tkMessageBox.showinfo(u'提示', u'登录完成')
                self.master.log_frame.pack_forget()
                self.master.main_fram.pack()
            else:
                tkMessageBox.showinfo(u'提示', u'没有用户登录')
                self.master.log_frame.pack_forget()
                self.pack()
        except Exception as e:
            tkMessageBox.showinfo(u'提示', u'登录失败：%s' % traceback.format_exc(e))
            self.master.log_frame.pack_forget()
            self.pack()
        self.master.log_frame.backButton.configure(state='normal')
        if has_driver and self.master.driver:
            self.master.driver.quit()


class MainFrame(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.followButton = Tkinter.Button(self, text=u'关注', command=self.follow)
        self.followButton.grid(row=0, column=0, padx=30, pady=160)
        self.signButton = Tkinter.Button(self, text=u'签到', command=self.sign)
        self.signButton.grid(row=0, column=1, padx=30, pady=160)
        self.sendButton = Tkinter.Button(self, text=u'发贴', command=self.send)
        self.sendButton.grid(row=0, column=2, padx=30, pady=160)

    def follow(self):
        self.pack_forget()
        self.master.title(u'自动关注')
        self.master.show_frame = self.master.fllow_frame
        self.master.fllow_frame.pack()

    def sign(self):
        self.master.show_frame = self.master.main_fram
        self.pack_forget()
        self.master.title(u'自动签到')
        self.master.log_frame.pack()
        get_tiebas_url = 'http://tieba.baidu.com/f/like/mylike?v=%s'
        sign_url = 'https://tieba.baidu.com/sign/add'
        self.master.log_frame.show_log(self.master.cut)
        try:
            for username, cookies in self.master.cookies.items():
                self.master.log_frame.show_log(u'帐号"%s"正在签到...' % username)
                self.master.session.cookies._cookies = cookies
                resp = self.master.session.get(get_tiebas_url % int(time.time() * 1000))
                table = re.search(r'<table.*?</table>', resp.content, re.DOTALL).group()
                tiebainfos = re.findall(r'<tr.*?title="(.*?)".*?tbs="(.*?)".*?</tr>', table, re.DOTALL)
                for tiebainfo in tiebainfos:
                    data = {'ie': 'utf-8', 'kw': tiebainfo[0].decode('gbk').encode('utf-8'), 'tbs': tiebainfo[1]}
                    for i in range(3):
                        resp = self.master.session.post(sign_url, data=urlencode(data))
                        result_code = resp.json().get('no')
                        if result_code in [0, 1101]:
                            break
                    msg = u'帐号"%s"在"%s"吧签到' % (username, tiebainfo[0].decode('gbk'))
                    msg += u'成功' if result_code in [0, 1101, 1102] else (u'失败: %s' % result_code)
                    self.master.log_frame.show_log(msg)
                msg = u'帐号"%s"签到完成' % username
                self.master.log_frame.show_log(msg)
            tkMessageBox.showinfo(u'提示', u'签到完成')
        except Exception as e:
            tkMessageBox.showinfo(u'提示', u'签到失败：%s' % traceback.format_exc(e))
        self.master.title(u'选择功能')
        self.pack()

    def send(self):
        self.pack_forget()
        self.master.title(u'自动发贴')
        self.master.show_frame = self.master.send_frame
        self.master.send_frame.pack()


class FllowFrame(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        Tkinter.Label(self, text=u"以英文逗号或换行分隔的贴吧名称：").grid(
            row=0, column=0, columnspan=2, padx=3, pady=3, sticky='W')
        self.tiebanamesInput = scrolledtext.ScrolledText(self, width=69, height=18)
        self.tiebanamesInput.bind("<Control-Key-a>", self.selecttext)
        self.tiebanamesInput.bind("<Control-Key-A>", self.selecttext)
        self.tiebanamesInput.grid(row=1, column=0, columnspan=2, padx=3, pady=3, sticky='W')
        self.tiebanamesInput.focus()

        self.backButton = Tkinter.Button(self, text=u'返回', command=self.back)
        self.backButton.grid(row=2, column=0, pady=3, padx=20, sticky='E')

        self.fllowButton = Tkinter.Button(self, text=u'开始关注', command=self.fllow)
        self.fllowButton.grid(row=2, column=1, pady=3, sticky='W')

    def selecttext(self, event):
        self.tiebanamesInput.tag_add(Tkinter.SEL, "1.0", Tkinter.END)
        return 'break'

    def back(self):
        self.pack_forget()
        self.master.title(u'选择功能')
        self.master.main_fram.pack()

    def fllow(self):
        tiebanames = self.tiebanamesInput.get("1.0", 'end-1c')
        if not tiebanames:
            tkMessageBox.showinfo(u'提示', u'请输入贴吧名称')
            self.tiebanamesInput.focus()
            return
        tiebanames = tiebanames.replace('\n', ',').split(',')
        tiebanames = [tiebaname for tiebaname in tiebanames if tiebaname]
        tieba_url = 'https://tieba.baidu.com/f?%s'
        fllow_url = 'https://tieba.baidu.com/f/like/commit/add'
        self.pack_forget()
        self.master.log_frame.pack()
        self.master.log_frame.show_log(self.master.cut)
        try:
            for username, cookies in self.master.cookies.items():
                self.master.log_frame.show_log(u'帐号"%s"正在关注...' % username)
                self.master.session.cookies._cookies = cookies
                for tiebaname in tiebanames:
                    resp = self.master.session.get(tieba_url % urlencode({'kw': tiebaname.encode('utf-8')}))
                    resp = self.master.session.get(resp.url)
                    real_name = re.search(r'PageData\.forum.*?name[\'"]:.*?"(.*?)"', resp.content, re.DOTALL).group(1)
                    real_name = eval('u\'%s\'' % real_name)
                    if real_name != tiebaname:
                        tiebanames.pop(tiebaname)
                        msg = u'"%s"吧不存在' % tiebaname
                        self.master.log_frame.show_log(msg)
                        continue
                    fid = re.search(r'PageData\.forum.*?id[\'"]:\s*?(\d+?)\D', resp.content, re.DOTALL).group(1)
                    uid = re.search(r'PageData\.user.*?name_url[\'"]:\s*?"(.*?)"', resp.content, re.DOTALL).group(1)
                    tbs = re.search(r'PageData[\s=]+?{.*?tbs[\'"]:\s*?"(.*?)"', resp.content, re.DOTALL).group(1)
                    data = {'fid': fid, 'fname': tiebaname.encode('utf-8'), 'uid': uid, 'ie': 'gbk', 'tbs': tbs}
                    for i in range(3):
                        resp = self.master.session.post(fllow_url, data=urlencode(data))
                        result_code = resp.json().get('no')
                        if result_code in [0, 221]:
                            break
                    msg = u'帐号"%s"关注"%s"吧' % (username, tiebaname)
                    msg += u'成功' if result_code in [0, 221] else (u'失败: %s' % result_code)
                    self.master.log_frame.show_log(msg)
                msg = u'帐号"%s"关注完成' % username
                self.master.log_frame.show_log(msg)
            tkMessageBox.showinfo(u'提示', u'关注完成')
        except Exception as e:
            tkMessageBox.showinfo(u'提示', u'关注失败：%s' % traceback.format_exc(e))
        self.pack()


class SendFrame(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)

        Tkinter.Label(self, text=u"图片路径：").grid(row=0, column=0, pady=3, sticky='E')
        self.tieziimageInput = Tkinter.Entry(self, width=60)
        self.tieziimageInput.bind("<Control-Key-a>", self.selectpath)
        self.tieziimageInput.bind("<Control-Key-A>", self.selectpath)
        self.tieziimageInput.grid(row=0, column=1, columnspan=2, pady=3, sticky='W')
        self.tieziimageInput.focus()

        Tkinter.Label(self, text=u"帖子标题：").grid(row=1, column=0, pady=2, sticky='E')
        self.tieziitieleInput = Tkinter.Entry(self, width=60)
        self.tieziitieleInput.bind("<Control-Key-a>", self.selecttitle)
        self.tieziitieleInput.bind("<Control-Key-A>", self.selecttitle)
        self.tieziitieleInput.grid(row=1, column=1, columnspan=2, pady=3, sticky='W')

        Tkinter.Label(self, text=u"帖子内容：").grid(row=2, column=0, pady=3, sticky='E')
        self.tiezicontentInput = scrolledtext.ScrolledText(self, width=60, height=16)
        self.tiezicontentInput.bind("<Control-Key-a>", self.selecttext)
        self.tiezicontentInput.bind("<Control-Key-A>", self.selecttext)
        self.tiezicontentInput.grid(row=2, column=1, columnspan=2, pady=3, sticky='W')

        self.backButton = Tkinter.Button(self, text=u'返回', command=self.back)
        self.backButton.grid(row=3, column=1, pady=3, sticky='E')

        self.sendButton = Tkinter.Button(self, text=u'开始发贴', command=self.send)
        self.sendButton.grid(row=3, column=2, pady=3, padx=20, sticky='W')

    def selectpath(self, event):
        self.tieziimageInput.selection_range(0, Tkinter.END)
        return 'break'

    def selecttitle(self, event):
        self.tieziitieleInput.selection_range(0, Tkinter.END)
        return 'break'

    def selecttext(self, event):
        self.tiezicontentInput.tag_add(Tkinter.SEL, "1.0", Tkinter.END)
        return 'break'

    def back(self):
        self.pack_forget()
        self.master.title(u'选择功能')
        self.master.main_fram.pack()

    def send(self):
        img_path = self.tieziimageInput.get().strip()
        title = self.tieziitieleInput.get().strip()
        content = self.tiezicontentInput.get("1.0", 'end-1c')
        if not title:
            tkMessageBox.showinfo(u'提示', u'请输入贴子标题')
            self.tieziitieleInput.focus()
            return
        elif not img_path and not content:
            tkMessageBox.showinfo(u'提示', u'请输入贴子内容')
            self.tieziimageInput.focus()
            return
        elif img_path and not os.path.exists(img_path):
            tkMessageBox.showinfo(u'提示', u'图片路径错误，请重新输入')
            self.tieziimageInput.focus()
            return
        if img_path:
            images = {'jpg': 'jpeg', 'png': 'png', 'gif': 'gif'}
            if img_path.split('.')[-1] not in images:
                tkMessageBox.showinfo(u'提示', u'仅支持jpg, png, gif类型的图片')
                self.tieziimageInput.focus()
                return
        content = content.replace('\n', '[br]')
        get_tiebas_url = 'http://tieba.baidu.com/f/like/mylike?v=%s'
        img_tbs_url = 'https://tieba.baidu.com/dc/common/imgtbs'
        upload_image = 'https://uploadphotos.baidu.com/upload/pic?%s'
        img_tab = '[img pic_type=0 width=%s height=%s]%s[/img]'
        add_url = 'https://tieba.baidu.com/f/commit/thread/add'
        mouse_pwd = '82,83,82,77,80,85,85,83,104,80,77,81,77,80,77,81,77,80,77,81,77,80,77,81,77,80,77,81,104,87,88,86,82,87,104,80,82,87,87,77,86,87,89,%s0'
        bsk = '''JVwVUWcLBBpwRQdsUnVCAl5LZyBuB08VTT0CQyZdFSk/RDgKQCA3URZSPj8BXgYaPUcvGBEgXSlyHw0GN0UI
        SCobVTYTIVpAGAgoJy4JBUVXIxMKN1A3JTRDJC5dICkcAVoyOSJfSwQsBDxVEDNdKx8QCA4kRU1EKzNBPgwpWkIPFjAyK
        VE8U1IoJEcpWSQxMlt8DFInJxgZejk7AW5LBSVKPlcVfFsmLgoUESB0Uk4rAUBzEykaVQsUIBIsQBtDTWEAQzF2KT0hRS
        QKVxowBBlWcToFWUkBBE07XR98VSgoGzUMaVxLXSA3SnMTKQVZEAIROHZXEERXNwJkPBkhNSVjNQNWKjAUGl1/e0ZZG0t
        zCjlBEDNMLjEQQRcqYlBZLBtUd0hsDRAxCSQjM1MQF10iA0MYFTtyfRI+XBFzZE9FAmpnURwbRWtYbBZEcF4mMg0ET2dQ
        Fgl/VQRrVWBUU1tFf3cuVwBSEm8QFGcPZB4EfBxNH2spTFcJfzUFXkMFIFs0ax8cTnc0GUNPZ18WCX9VAW9Qe0YFW1Zpd
        SoXVw0cAQ5IME1mKGkGD1kHa2hfGQJ/bUZXQkQKZn0YXDwKZWReFREwVAgJIEQRZUF+RgFdV3BmawlXQA1vXQYjVCojNB
        xyGgJrfl84XCc+CEFLRnwGbxRWCAl2ZV4tCitEXAs9TQUAV3hfECsXNTs/chBVdSQTCXAGcX5iBnBHeAEQMDkffTsNRk9
        JDk08XxF5GAQ2DA4OIB4RHWtFHW1YfkIeUlBlBDtDFEVXYlIVcht1ZnMcchwBa35dRABrYUgPWlhrEn0RSRIddWwKAxBg
        AxYOdjQWbVN5RlJeXidgOUAWBV0sBUAkBHNgZQNjVgBwdlhHAXhgIA8GSygcfQ5eNlkrLRtNQTIABhFnO2YTLW5aEhlUZ
        216UQdCW2FFSHQXfHBjAGFYA3x1TFkRPGRGFwoPKEQsUVJySnZ8REMFMF9HXywaXX8TLRhUBQptfnpeVWxQLBNPM1BmMz
        5UNTITNGZRV1psdV4NXhs8TXMWH2EafX5PUlVzHQZYdFcJf1Z6ThxIA3R1YAc7YnIBRVs='''
        bsk = bsk.replace('\n', '').replace(' ', '')
        self.pack_forget()
        self.master.log_frame.pack()
        self.master.log_frame.show_log(self.master.cut)
        try:
            requests_info = {}
            for username, cookies in self.master.cookies.items():
                self.master.log_frame.show_log(u'获取帐号"%s"贴吧信息...' % username)
                self.master.session.cookies._cookies = cookies
                resp = self.master.session.get(get_tiebas_url % int(time.time() * 1000))
                table = re.search(r'<table.*?</table>', resp.content, re.DOTALL).group()
                tiebainfos = re.findall(r'<tr.*?title="(.*?)".*?balvid="(\d*?)".*?tbs="(.*?)".*?</tr>', table, re.DOTALL)
                for tiebainfo in tiebainfos:
                    tiebainfo = list(tiebainfo)
                    tiebainfo[0] = tiebainfo[0].decode('gbk')
                    if tiebainfo[0] not in requests_info:
                        requests_info[tiebainfo[0]] = []
                    requests_info[tiebainfo[0]].append([username, copy.deepcopy(cookies), tiebainfo])
                self.master.log_frame.show_log(u'获取帐号"%s"贴吧信息完成' % username)
            for tieba_name, request_info in requests_info.items():
                self.master.log_frame.show_log(u'正在"%s"吧发贴...' % tieba_name)
                for request in request_info:
                    username, cookies, tiebainfo = request
                    self.master.session.cookies._cookies = cookies
                    send_content = content
                    if img_path:
                        # 上传图片
                        self.master.session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
                        resp = self.master.session.get(img_tbs_url)
                        self.master.session.get(img_tbs_url)
                        self.master.session.headers.pop('X-Requested-With')
                        img_tbs = resp.json().get('data').get('tbs')

                        params = {'tbs': img_tbs, 'fid': tiebainfo[1], 'save_yun_album': '1'}
                        self.master.session.options(upload_image % urlencode(params))

                        files = {'file': (os.path.basename(img_path), open(img_path, 'rb'),
                                 'image/%s' % images.get(img_path.split('.')[-1]))}
                        resp = self.master.session.post(upload_image % urlencode(params), files=files)

                        # 获取上传后的图片信息，生成图片链接、宽、高
                        image_json = resp.json()
                        image_id = image_json.get('info').get('pic_id_encode')
                        image_type = image_json.get('info').get('pic_water').split('.')[-1]
                        height = image_json.get('info').get('fullpic_height')
                        width = image_json.get('info').get('fullpic_width')
                        if width > 560:
                            height = int(float(height) / width * 560)
                            width = 560
                        image_url = 'https://imgsa.baidu.com/forum/pic/item/%s.%s' % (image_id, image_type)

                        # 生成图片标签
                        send_content = send_content.replace('[img]', img_tab % (width, height, image_url))
                    time_stamp = str(int(time.time() * 1000))
                    data = {
                        'ie': 'utf-8', 'kw': tiebainfo[0].encode('utf-8'), 'fid': tiebainfo[1], 'tid': '0',
                        'vcode_md5': '', 'floor_num': '0', 'rich_text': '1', 'tbs': tiebainfo[2], 'prefix': '',
                        'content': send_content.encode('utf-8'), 'basilisk': '1', 'title': title.encode('utf-8'),
                        'files': '[]', 'mouse_pwd': mouse_pwd % time_stamp, 'mouse_pwd_t': time_stamp,
                        'mouse_pwd_isclick': '0', '__type__': 'thread', '_BSK': bsk}
                    for i in range(3):
                        resp = self.master.session.post(add_url, data=urlencode(data))
                        result_code = resp.json().get('no')
                        if result_code == 0:
                            break
                    msg = u'帐号"%s"在"%s"吧发贴' % (username, tiebainfo[0])
                    msg += u'成功' if result_code == 0 else (u'失败: %s' % result_code)
                    self.master.log_frame.show_log(msg)
                msg = u'"%s"吧发贴完成' % tieba_name
                self.master.log_frame.show_log(msg)
            tkMessageBox.showinfo(u'提示', u'发贴完成')
        except Exception as e:
            tkMessageBox.showinfo(u'提示', u'发贴失败：%s' % traceback.format_exc(e))
        self.pack()


class LogFrame(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.text = scrolledtext.ScrolledText(self, width=69, height=20)
        self.text.grid(row=0, column=0, pady=3, sticky='E')
        self.backButton = Tkinter.Button(self, text=u'返回', command=self.back)
        self.backButton.grid(row=1, column=0, pady=3)

    def show_log(self, msg):
        self.text.configure(state='normal')
        self.text.insert(Tkinter.END, msg + '\n')
        self.text.see(Tkinter.END)
        self.text.configure(state='disabled')
        self.master.update()

    def back(self):
        self.pack_forget()
        self.master.show_frame.pack()


class App(Tkinter.Tk):
    def __init__(self):
        Tkinter.Tk.__init__(self)
        self.login_fram = LoginFrame()
        self.main_fram = MainFrame()
        self.fllow_frame = FllowFrame()
        self.send_frame = SendFrame()
        self.log_frame = LogFrame()

        self.headers = {
            'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Pragma': 'no-cache',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/60.0.3112.113 Chrome/60.0.3112.113 Safari/537.36'}
        self.session = Session()
        self.session.headers.update(self.headers)
        self.cookies = {}
        self.cut = '**********************************************************'

        self.withdraw()
        self.title(u'登录')
        self.login_fram.pack()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight() - 100
        self.resizable(False, False)
        self.update_idletasks()
        self.geometry('%sx%s+%s+%s' % (
            self.winfo_reqwidth() + 10, self.winfo_reqheight() + 10,
            (screen_width - self.winfo_reqwidth()) / 2,
            (screen_height - self.winfo_reqheight()) / 2))
        self.deiconify()

    def get_driver_by_phantomjs(self):
            self.log_frame.show_log(u'初始化浏览器驱动...')
            desired_capabilities = {'phantomjs.page.settings.loadImages': False,
                                    'phantomjs.page.settings.userAgent': self.headers.get('User-Agent')}
            for i in range(3):
                try:
                    driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities,
                                                 service_log_path='/dev/null')
                    break
                except Exception:
                    pass
                if i == 2:
                    tkMessageBox.showinfo(u'提示', u'初始化浏览器驱动失败')
                    return
            self.log_frame.show_log(u'初始化浏览器驱动成功')
            return driver


app = App()
app.mainloop()
