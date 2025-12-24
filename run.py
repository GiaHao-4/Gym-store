# File: run.py
# Vị trí: Nằm ngoài folder gym (ngang hàng với nó)

from gym import app
# Import index để nạp toàn bộ các đường dẫn (routes) của web
from gym import index

if __name__ == "__main__":
    app.run(debug=True)