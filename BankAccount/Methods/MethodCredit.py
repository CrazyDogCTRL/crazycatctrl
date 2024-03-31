import sqlite3
from datetime import datetime


class MethodCredit:
    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['request']
            try:
                method = getattr(MethodCredit, request_type)()
                return method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")
                return {"status": "failed"}

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {IdentificationAccount} уже существует.")
                return {"status": "failed"}
            else:
                Money = request.get('Money', 0)
                BIC = request.get('BIC', 'DEFAULT')
                CreditLimit = request['CreditLimit']
                Rank = request['Rank']
                TimeActive = request.get('TimeActive', datetime.now().strftime('%s'))
                LastPayTime = request.get('LastPayTime', datetime.now().strftime('%s'))
                PayTime = request.get('PayTime', 0)
                cursor.execute("INSERT INTO credit_accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               (IdentificationAccount, Money, BIC, CreditLimit, Rank, TimeActive, LastPayTime, PayTime))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно открыт.")
                return {"status": "success"}

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account[1] >= 0:
                if account:
                    cursor.execute("DELETE FROM credit_accounts WHERE IdentificationAccount = ?",
                                   (IdentificationAccount,))
                    conn.commit()
                    print(f"Счет {IdentificationAccount} успешно закрыт.")
                    return {"status": "success"}
                else:
                    print(f"Счет {IdentificationAccount} не найден.")
                    return {"status": "failed"}
            else:
                print("Пожалуйста, погасите кредит")
                return {"status": "failed"}

    class GetMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT * FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                cursor.execute("UPDATE credit_accounts SET Money = Money + ? WHERE IdentificationAccount = ?",
                               (Money, IdentificationAccount))
                conn.commit()
                print(f"Сумма {Money} успешно зачислена на счет {IdentificationAccount}.")
                return {"status": "success"}
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return {"status": "failed"}

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT Money, CreditLimit FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                CurrentMoney = account[0]
                CreditLimit = account[1]
                if CurrentMoney + CreditLimit >= Money:
                    cursor.execute("UPDATE credit_accounts SET Money = Money - ? WHERE IdentificationAccount = ?",
                                   (Money, IdentificationAccount))
                    conn.commit()
                    print(f"Сумма {Money} успешно списана со счета {IdentificationAccount}.")
                    return {"status": "success"}
                else:
                    print(f"Недостаточно средств на счете {IdentificationAccount}.")
                    return {"status": "failed"}
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return {"status": "failed"}

    class PayCredit:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute(
                "SELECT TimeActive,"
                "LastPayTime,"
                "PayTime,"
                "Money FROM credit_accounts WHERE IdentificationAccount = ?",
                (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                TimeActive, LastPayTime, PayTime, Balance = account
                current_time = int(datetime.now().strftime('%s'))
                if Balance < 0:
                    if int(current_time) - int(LastPayTime) >= int(PayTime):
                        Money = request['Money']
                        BIC = request['BIC']
                        get_money_request = {
                            'request': 'GetMoney',
                            'IdentificationAccount': IdentificationAccount,
                            'Money': Money
                        }
                        MethodCredit.AnalyzeRequest()(get_money_request, cursor, conn)
                        cursor.execute("UPDATE credit_accounts SET LastPayTime = ? WHERE IdentificationAccount = ?",
                                       (current_time, IdentificationAccount,))
                        conn.commit()
                        print(f"Время последнего зачисления для счета {IdentificationAccount} успешно обновлено.")
                    else:
                        print(
                            f"Баланс счета {IdentificationAccount} отрицательный, но время для начисления пени еще не пришло.")
                else:
                    print(f"Баланс счета {IdentificationAccount} положительный, пени не начисляются.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class GetBalance:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT Money, CreditLimit FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            money = cursor.fetchone()
            if money:
                return money[0], money[1]
            else:
                print('Счёта с указанными данными не существует.')
                return {"status": "failed"}
