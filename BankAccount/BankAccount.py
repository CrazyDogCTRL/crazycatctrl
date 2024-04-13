import os
import sqlite3
from BankAccount.Methods.MethodDebit import MethodDebit
from BankAccount.Methods.MethodCredit import MethodCredit
from BankAccount.Methods.MethodDeposit import MethodDeposit


class BankAccount:
    def __init__(self):
        self.accounts = {
            'Debit': self.Debit(),
            'Credit': self.Credit(),
            'Deposit': self.Deposit()
        }

    def process_request(self, request):
        kind_of_account = request['kind_of_account']
        try:
            treatment_request = self.accounts[kind_of_account]
            return treatment_request.treatment_request(request)
        except KeyError:
            print(f"Unsupported kind of account: {kind_of_account}. Supported types are: {list(self.accounts.keys())}.")
            return {"status": "failed"}
        except AttributeError:
            print(f"Unsupported request type: {request['request']}")
            return {"status": "failed"}

    class Debit:
        def __init__(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.conn = sqlite3.connect(os.path.join(current_dir, 'debit_accounts.db'))
            self.cursor = self.conn.cursor()
            self.create_table()
            self.analyzer = MethodDebit.AnalyzeRequest()

        def create_table(self):
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS debit_accounts
                                   (IdentificationAccount TEXT,
                                   Money REAL DEFAULT 0,
                                   BIC TEXT DEFAULT 'AAA')''')
            self.conn.commit()

        def treatment_request(self, request):
            return self.analyzer(request, self.cursor, self.conn)

    class Credit:
        def __init__(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.conn = sqlite3.connect(os.path.join(current_dir, 'credit_accounts.db'))
            self.cursor = self.conn.cursor()
            self.create_table()
            self.analyzer = MethodCredit.AnalyzeRequest()

        def create_table(self):
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS credit_accounts
                                   (IdentificationAccount TEXT,
                                   Money REAL DEFAULT 0,
                                   BIC TEXT,
                                   CreditLimit REAL,
                                   Rank TEXT DEFAULT 'AAA',
                                   TimeActive INTEGER DEFAULT (strftime('%s', 'now')),
                                   LastPayTime INTEGER DEFAULT (strftime('%s', 'now')),
                                   PayTime INTEGER,
                                   Percent REAL DEFAULT 0)''')
            self.conn.commit()

        def treatment_request(self, request):
            return self.analyzer(request, self.cursor, self.conn)

    class Deposit:
        def __init__(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.conn = sqlite3.connect(os.path.join(current_dir, 'deposit_accounts.db'))
            self.cursor = self.conn.cursor()
            self.create_table()
            self.analyzer = MethodDeposit.AnalyzeRequest()

        def create_table(self):
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS deposit_accounts
                                   (IdentificationAccount TEXT,
                                   Money REAL DEFAULT 0,
                                   BIC TEXT,
                                   StatusDeposit TEXT DEFAULT 'ON',
                                   TimeActive INTEGER DEFAULT (strftime('%s', 'now')),
                                   LastPayTime INTEGER DEFAULT (strftime('%s', 'now')),
                                   PayTime INTEGER DEFAULT 0,
                                   TimeClose INTEGER DEFAULT 0,
                                   Percent REAL DEFAULT 0)''')
            self.conn.commit()

        def treatment_request(self, request):
            return self.analyzer(request, self.cursor, self.conn)


bank_account = BankAccount()

request = {
    'kind_of_account': 'Debit',
    'request': 'OpenAccount',
    'IdentificationAccount': '777',
    'Money': 50,
    'BIC': 'ABC123'
}

