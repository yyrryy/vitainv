import os

# activate the virtual environment
activate_this = os.path.expanduser("C:\Users\hp\Desktop\projects\inventory\venv\Scripts\activate")
exec(open(activate_this).read(), dict(__file__=activate_this))
os.chdir("C:\Users\hp\Desktop\projects\inventory")
os.system("py manage.py runserver")