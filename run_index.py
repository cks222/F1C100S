import streamlit.web.cli as stcli
import os
import sys


def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def streamlit_run():
    src = get_path("./src_code/index.py")
    sys.argv = [
        "streamlit",
        "run",
        src,
        "--global.developmentMode=false",
        "--server.port=8000",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    streamlit_run()
