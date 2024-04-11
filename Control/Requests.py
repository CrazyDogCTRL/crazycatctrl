class Requests:

    def id_user_request(self, session):
        email = session["email"]
        return {"email": email, "request": "GetID"}

    def id_number_user_request(self, request):
        return {"number": request['phoneNumber'], "request": "NumberGetID"}

    def open_request(self, request, id_user):
        return {
            'kind_of_account': request["kind_of_account"],
            'request': 'OpenAccount',
            'IdentificationAccount': id_user,
            'Money': 1000,
            'BIC': 'ABC123',
            'Rank': 'AAA',
            'CreditLimit': 5000,
            'PayTime': 5,
            'TimeClose': 10,
            'StatusDeposit': 'ON',
            'Percent': request.get("Percent")
        }

    def close_request(self, request, id_user):
        return {
            'kind_of_account': request['kind_of_account'],
            'request': 'CloseAccount',
            'IdentificationAccount': id_user,
        }

    def balance_request(self, request, id_user):
        return {
            'IdentificationAccount': id_user,
            "request": "GetBalance",
            "kind_of_account": request['kind_of_account']
        }

    def id_balance_request(self, request, id_giver):
        return {
            'kind_of_account': request["kind_of_account"],
            'request': 'GetBalance',
            'IdentificationAccount': id_giver
        }

    def giver_request(self, request, id_giver):
        return {
            'kind_of_account': request["kind_of_account"],
            'request': 'GiveMoney',
            'IdentificationAccount': id_giver,
            'Money': request["amount"]
        }

    def from_giver_request(self, request, id_giver):
        return {
            'kind_of_account': request["from_kind_of_account"],
            'request': 'GiveMoney',
            'IdentificationAccount': id_giver,
            'Money': request["amount"]
        }

    def receiver_request(self, request, id_receiver):
        return {
            'kind_of_account': 'Debit',
            'request': 'GetMoney',
            'IdentificationAccount': id_receiver,
            'Money': request["amount"]
        }

    def to_receiver_request(self, request, id_receiver):
        return {
            'kind_of_account': request["to_kind_of_account"],
            'request': 'GetMoney',
            'IdentificationAccount': id_receiver,
            'Money': request["amount"]
        }

    def pay_credit_request(self):
        return {
            'kind_of_account': 'Credit',
            'request': 'PayCredit'
        }

    def pay_deposit_request(self):
        return {
            'kind_of_account': 'Deposit',
            'request': 'PayDeposit'
        }

    def id_balance_from_request(self, request, id_giver):
        return {
            'kind_of_account': request["from_kind_of_account"],
            'request': 'GetBalance',
            'IdentificationAccount': id_giver
        }

    def get_number_by_id(self, id_user):
        return {
            "request": "GetNumberById",
            "id": id_user
        }

    def get_email_by_id(self, id_user):
        return {
            "request": "GetEmailById",
            "id": id_user
        }
