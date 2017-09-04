## 贴吧自动签到、关注、刷贴工具，支持多帐号登录使用，基于python2.7开发

## 文件说明
* ```tiebatool.py``` 主脚本文件，ubuntu可以直接编译运行
* ```tiebatool.exe``` 打包好的exe文件，可以直接在Windows下单独使用
* ```tieba.ico``` 打包exe的图标文件
* ```tiebatool.spec``` 打包exe的配置文件示例
* ```users_info.json``` 贴吧用户名和密码的配置文件
* ```phantomjs.exe``` 打包exe必要的依赖文件，仅Windows下需要使用

## Windows打包exe过程
1. 安装python的相关依赖包
2. 把```tiebatool.py```，```tieba.ico```，```phantomjs.exe```放到同一目录下
3. 切换到目录下运行"```pyinstaller -w -F -i tieba.ico tiebatool.py```"，现在生成的exe文件还不能使用，因为```phantomjs.exe```没有打包进去，这一步是为了生成```tiebatool.spec```文件，为后面做准备
4. 修改上一步生成的```tiebatool.spec```文件，增加```phantomjs.exe```的引用，如下所示，```a.datas```下面添加一行"```[('\\phantomjs.exe','C:\\Users\\username\\Desktop\\TIEBAT~1\\phantomjs.exe','DATA')]```"，路径改成自己对应的路径
    ```
    exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('\\phantomjs.exe','C:\\Users\\username\\Desktop\\TIEBAT~1\\phantomjs.exe','DATA')],
          name='tiebatool',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='tieba.ico')
    ```
5. 修改"```selenium/webdriver/common/service.py```"的start方法的```subprocess.Popen```一行，增加Popen的参数"```shell=True, stdin=subprocess.PIPE```"，否则打包好的exe运行时会报"```window error 6```"错误
6. 删除第一次打包生成的dist和build文件夹，执行"```pyinstaller tiebatool.spec```"
7. 打包好的```tiebatool.exe```文件已经在dist文件夹下面了，可以直接单独使用，build文件夹和dist文件夹可以删除了
