import sqlite3
import os
from threading import local

class User:
    thread_local = local()

    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), 'users.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.analyzer = User.AnalyzeRequest()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               email TEXT NOT NULL,
                               password TEXT NOT NULL,
                               number TEXT,
                               name TEXT,
                               surname TEXT,
                               patronymic TEXT,
                               passport_data INTEGER,
                               verification INTEGER DEFAULT 0,
                               rank TEXT DEFAULT 'AAA')''')
        self.conn.commit()

    def treatment_request(self, request):
        self.analyzer(request)

    class AnalyzeRequest:
        def __call__(self, request):
            cursor = User.thread_local.cursor
            conn = User.thread_local.conn
            request_type = request['request']
            try:
                method = getattr(User, request_type)()
                return method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")

    class AddUser:
        def __call__(self, request, cursor, conn):
            email = request['email']
            number = request['number']
            cursor.execute("SELECT * FROM users WHERE email = ? OR number = ?",
                           (email, number))
            account = cursor.fetchone()
            if account:
                print("Аккаунт с указанными данными уже существует.")
            else:
                password = request['password']
                name = request['name']
                surname = request['surname']
                patronymic = request['patronymic']
                cursor.execute("INSERT INTO users(email,password,number,name,surname,patronymic) VALUES "
                               "(?,?,?,?,?,?)",
                               (email, password, number, name, surname, patronymic))
                conn.commit()
                return 1

    class DelUser:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()

    class VerifyUser:
        def __call__(self, request, cursor, conn):
            passport = request['passport_data']
            user_id = request['id']
            cursor.execute("UPDATE users SET passport_data=?, verification = 1 WHERE id = ?", (passport, user_id))
            conn.commit()

    class IsVerified:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            verif = cursor.execute("SELECT verification FROM users WHERE id = ?", (user_id,))
            isverif = verif.fetchone()
            if isverif:
                return isverif[0]
            else:
                print("Аккаунта с указанными данными не существует.")

    class GetID:
        def __call__(self, request, cursor, conn):
            email = request['email']
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            account = cursor.fetchone()
            if account:
                return account[0]
            else:
                print("Аккаунта с указанными данными не существует.")
                return None

    class NumberGetID:
        def __call__(self, request, cursor, conn):
            number = request['number']
            cursor.execute("SELECT id FROM users WHERE number = ?", (number,))
            account = cursor.fetchone()
            if account:
                return account[0]
            else:
                print("Аккаунта с указанными данными не существует.")
                return None

    class GetFSP:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            fsp = cursor.execute("SELECT name, surname, patronymic FROM users WHERE id = ?", (user_id,))
            fsp_fetch = fsp.fetchone()
            if fsp_fetch:
                out = {
                    'name': fsp_fetch[0],
                    'surname': fsp_fetch[1],
                    'patronymic': fsp_fetch[2]
                }
                return out
            else:
                print("Аккаунта с указанными данными не существует.")

    class GetPassword:
        def __call__(self, request, cursor, conn):
            email = request['email']
            cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
            password = cursor.fetchone()
            if password:
                return password[0]
            else:
                print("Аккаунт с указанными данными не существует.")
                return None

    class GetNumberById:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            cursor.execute("SELECT number FROM users WHERE id = ?", (user_id,))
            number = cursor.fetchone()
            if number:
                return number[0]
            else:
                print("Пользователь с указанным ID не существует.")
                return None

    class GetEmailById:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
            email = cursor.fetchone()
            if email:
                return email[0]
            else:
                print("Пользователь с указанным ID не существует.")
                return None
