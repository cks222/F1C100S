import site
import os
from PyInstaller.utils.hooks import copy_metadata,collect_data_files

datas = []
datas += copy_metadata('streamlit')
block_cipher = None

assert len(site.getsitepackages()) > 0

# Choose path containing "site-packages"
package_path = site.getsitepackages()[0]
for p in site.getsitepackages():
    if "site-package" in p:
        package_path = p
        break

datas += [
  (
      os.path.join(package_path,"streamlit/static"),
      "./streamlit/static"
  ),
  (
      os.path.join(package_path,"streamlit/runtime"),
      "./streamlit/runtime"
  ),
  (
      os.path.join(package_path,"langchain/schema"),
      "./langchain/schema"
  ),
  (   os.path.join(package_path,"st_aggrid/frontend"),
      "./st_aggrid/frontend"
  ),
  (   os.path.join(package_path,"st_aggrid/json"),
      "./st_aggrid/json"
  ),
  (
      os.path.join(os.getcwd(),"src_code"),
      "./src_code"
  ),
  (
      os.path.join(os.getcwd(),"model"),
      "./model"
  )
]
a = Analysis(
    ['run_index.py'],
    pathex=[package_path],
    binaries=[],
    datas=datas,
    hiddenimports=["streamlit","langchain","chardet","st_aggrid","sentence_transformers"],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='run_index',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)