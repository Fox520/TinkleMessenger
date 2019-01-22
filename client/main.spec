# -*- mode: python -*-

from kivy.deps import sdl2, glew

block_cipher = None 


a = Analysis(['main.py'],
             binaries=None,
             datas=None,
             hookspath=[],
			 hiddenimports=['toto'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
         cipher=block_cipher)

a.datas += [('back.png', 'back.png', 'DATA')]
a.datas += [('cat.jpg', 'cat.jpg', 'DATA')]
a.datas += [('confirm.png', 'confirm.png', 'DATA')]
a.datas += [('left.png', 'left.png', 'DATA')]


exe = EXE(pyz,
          Tree('images','images'),
          Tree('img','img'),
          Tree('resources','resources'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='Tinkle',
          debug=False,
          strip=False,
          upx=False,
          console=False)