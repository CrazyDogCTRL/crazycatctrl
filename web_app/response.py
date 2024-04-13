from http import cookies
from urllib.parse import unquote_plus
from Control.control import Control
import time
from views import *
from logs.logs import *

logs = Logs()
control = Control()
active_sessions = {}
COOKIE_NAME = "session_id"
HOST = ("localhost", 7777)

URLS = {
    "/": home,
    "/login": login,
    "/main": main,
    "/register": register,
    "/verification": verification,
    "/verif_main": verif_main,
    "/credit": credit,
    "/debit": debit,
    "/deposit": deposit,
    "/open_acc_debit": open_acc_debit,
    "/close_acc_debit": close_acc_debit,
    "/send_money_debit": send_money_debit,
    "/open_acc_credit": open_acc_credit,
    "/close_acc_credit": close_acc_credit,
    "/open_acc_deposit": open_acc_deposit,
    "/close_acc_deposit": close_acc_deposit,
    "/send_money_credit": send_money_credit,
    '/balance': 0,
    "/send_money_deposit": send_money_deposit,
    "/local_send_money": local_send_money
}

POST_urls = {
    "/login": login,
    "/register": register,
    "/command": command,
    "/open_acc_debit": open_acc_debit,
    "/close_acc_debit": close_acc_debit,
    "/send_money_debit": send_money_debit,
    "/credit": credit,
    "/debit": debit,
    "/deposit": deposit,
    "/open_acc_credit": open_acc_credit,
    "/close_acc_credit": close_acc_credit,
    "/open_acc_deposit": open_acc_deposit,
    "/close_acc_deposit": close_acc_deposit,
    "/send_money_credit": send_money_credit,
    "/send_money_deposit": send_money_deposit
}


class ResponseGenerator:
    @staticmethod
    def check_session_validity(session_id):
        if session_id in active_sessions:
            session_start_time = active_sessions[session_id]["start_time"]
            if time.time() - session_start_time <= 3 * 3600:
                return True
        return False

    @staticmethod
    def generate_session_id():
        return str(time.time())

    @staticmethod
    def set_cookie_header(session_id):
        cookie = cookies.SimpleCookie()
        cookie[COOKIE_NAME] = session_id
        cookie[COOKIE_NAME]["path"] = "/"
        cookie[COOKIE_NAME]["max-age"] = 3 * 3600  # expire after 3 hours
        return cookie.output(header="").strip()

    @staticmethod
    def redirect_to(location, session_id, email=None):
        if email:
            return f"HTTP/1.1 302 Found\nLocation: {location}\nSet-Cookie: {ResponseGenerator.set_cookie_header(session_id)}\nSet-Cookie: email={email}\nContent-Type: text/html; charset=utf-8\n\n"
        else:
            return f"HTTP/1.1 302 Found\nLocation: {location}\nSet-Cookie: {ResponseGenerator.set_cookie_header(session_id)}\nContent-Type: text/html; charset=utf-8\n\n"

    @staticmethod
    def redirect_main(session_id, email=None):
        if ResponseGenerator.check_session_validity(session_id):
            # Пользователь авторизован, перенаправляем на /verif_main
            new_location = "/verif_main"
            return ResponseGenerator.redirect_to(new_location, session_id, email)
        else:
            # Пользователь не авторизован, перенаправляем на главную страницу
            new_location = "/main"
            return ResponseGenerator.redirect_to(new_location, session_id)

    @staticmethod
    def generate_headers(method, url, session_id):
        if url not in URLS:
            return "HTTP/1.1 404 Not found\nContent-Type: text/html; charset=utf-8\n\n", 404

        if url == "/login" and ResponseGenerator.check_session_validity(session_id):
            # Пользователь уже авторизован, перенаправляем на /verif_main
            new_location = "/verif_main"
            return ResponseGenerator.redirect_to(new_location, session_id), 302

        if url == "/register" and ResponseGenerator.check_session_validity(session_id):
            # Пользователь авторизован, перенаправляем на /verif_main
            new_location = "/verif_main"
            return ResponseGenerator.redirect_to(new_location, session_id), 302

        if url == "/main" and ResponseGenerator.check_session_validity(session_id):
            # Пользователь авторизован, перенаправляем на /verif_main
            new_location = "/verif_main"
            return ResponseGenerator.redirect_to(new_location, session_id), 302

        if url != "/login" and url != "/register" and url != "/main" and not ResponseGenerator.check_session_validity(
                session_id):
            return ResponseGenerator.redirect_main(session_id), 302

        if method == "POST" and url not in POST_urls:
            return "HTTP/1.1 405 Method not allowed\nContent-Type: text/html; charset=utf-8\n\n", 405

        return "HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\n", 200

    @staticmethod
    def parse_request(request):
        lines = request.split("\r\n")
        first_line_parts = lines[0].split(" ")
        if len(first_line_parts) < 2:
            raise ValueError('Неправильно отформатированная строка запроса')
        method = first_line_parts[0]
        url = first_line_parts[1]
        version = first_line_parts[2] if len(first_line_parts) > 2 else None
        index = None
        for i, line in enumerate(lines):
            if line == "":
                index = i
                break
        if index is None:
            headers = {}
            data = {}
        else:
            headers = {}
            for line in lines[1:index]:
                key, value = line.split(": ", 1)
                headers[key] = value
            body = "\r\n".join(lines[index + 1:])
            data = {}
            if method == "POST":
                if 'Content-Type' in headers and 'application/json' in headers['Content-Type']:
                    try:
                        data = json.loads(body)
                    except ValueError:
                        pass  # Обработка недопустимого JSON при необходимости
                else:
                    params = body.split("&")
                    for param in params:
                        if '=' in param:
                            key, value = param.split("=")
                            data[unquote_plus(key)] = unquote_plus(value)
                        else:
                            data[unquote_plus(param)] = ""
        return method, url, headers, data

    @staticmethod
    def generate_content(code, url):
        if code == 404:
            return "<h1>404</h1><p>Not found</p>"
        if code == 405:
            return "<h1>405</h1><p>Method not allowed</p>"
        return URLS[url]()

    @staticmethod
    def generate_result(request):
        method, url, headers, data = ResponseGenerator.parse_request(request)
        if method == "POST":
            print(data)
        session_id = None
        user_email = None
        if "Cookie" in headers:
            cookie = cookies.SimpleCookie(headers["Cookie"])
            if COOKIE_NAME in cookie:
                session_id = cookie[COOKIE_NAME].value
                if session_id in active_sessions:
                    user_email = active_sessions[session_id].get('email')

        headers, code = ResponseGenerator.generate_headers(method, url, session_id)
        if (url == '/register' or url == '/login') and method == "POST":
            control_response = control.treatment_request(data)
            logs.add_log(data, control_response, active_sessions.get(session_id))
            if control_response is not None and control_response.get('status') == 'success':
                user_email = data.get('email')
                session_id = ResponseGenerator.generate_session_id()
                new_location = "/verif_main"
                headers = ResponseGenerator.redirect_to(new_location, session_id, user_email)
                active_sessions[session_id] = {"start_time": time.time(), "email": user_email}
        session = active_sessions.get(session_id)
        balance = "Счет не существует"
        if (url != "/register" and url != "/login") and method == "POST":
            control_response = control.treatment_request(data, session)
            if data.get("method") == "Getbalance":
                balance = control_response.get("balance")
                if balance is None:
                    balance = "Счет не существует"
            logs.add_log(data, control_response, active_sessions.get(session_id))
        if url == '/balance':
            response_body = f"<p>{balance}</p>"
        else:
            response_body = ResponseGenerator.generate_content(code, url)
        response = (headers + response_body).encode()
        return response
    @staticmethod
    def auto_update():
        while True:
            control.start_payment_scheduler()
            time.sleep(60)