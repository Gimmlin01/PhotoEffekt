# -*- mode: python -*-

block_cipher = None

added_files = [
         ( 'icons/*.png', 'icons' ),
         ( 'devices/*.py', 'bundled' )
         ]

a = Analysis(['main.py','devices/Ut61c.py'],
             pathex=['D:/Voltmeter/','/media/yoxcu/Daten/Voltmeter/'],
             binaries=[],
             datas=added_files,
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
          name='Voltmeter',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon='icons/AppIcon.ico' )
