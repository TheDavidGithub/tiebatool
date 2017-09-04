# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\tiebatool\\tiebatool.py'],
             pathex=['C:\\Users\\username\\Desktop\\TIEBAT~1'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
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
