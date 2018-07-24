import pandas as pd


class PersonBill():
    def __init__(self, name):
        self.name = name
        self.income = {}
        self.payment = {}
        self.need_pay = {}
        self.items = []

    def print_payment(self):
        for name, money in self.payment.items():
            print('需要向{}支付{}'.format(name, money))

    def print_need_pay(self):

        for obj, money in self.need_pay.items():
            _type = '收取' if money > 0 else '支付'
            print('{}需要向{}{}{}'.format(name, obj, _type, abs(money)))


class Bill():
    def __init__(self, csv_file):
        bill_df = pd.read_csv(csv_file)
        self.bill_df = bill_df[bill_df['支付状态'] == 'Yes']
        self.persons = self.get_all_person()
        self.person_detail = {}

        for person in self.persons:
            self.set_person_bill_detail(person)

    def set_person_bill_detail(self, name):
        self.person_detail[name] = PersonBill(name)

    def get_all_person(self):
        persons = set(self.bill_df['参与人'])
        persons.update(set(self.bill_df['实际支付人']))

        all_multi_person = [person for person in persons if ',' in str(person)]
        one_persons = persons.difference(all_multi_person)

        for multi_person in all_multi_person:
            one_persons.update(set(multi_person.split(',')))

        return one_persons

    def a_pay_to_b(self, a, b, money):
        """
        a需要向b支付
        :param a:
        :param b:
        :return:
        """
        # payment
        if not self.person_detail[a].payment.get(b, None):
            self.person_detail[a].payment[b] = money
        else:
            self.person_detail[a].payment[b] += money

        # income
        if not self.person_detail[b].income.get(a, None):
            self.person_detail[b].income[a] = money
        else:
            self.person_detail[b].income[a] += money

    def handle_bill(self):
        for index, item in self.bill_df.iterrows():
            self.handle_item(item)

    def handle_item(self, item):
        payer = item['实际支付人']
        if not isinstance(payer, float):
            if not isinstance(item['参与人'], float):
                participant = item['参与人'].split(',')
                money = item['金额']
                _type = item['支付类型']
                if _type == '平分':
                    avg = money / len(participant)
                    for person in participant:
                        if person != payer:
                            self.a_pay_to_b(person, payer, avg)

                if _type == '个人':
                    assert len(participant) == 1
                    if participant[0] != payer:
                        self.a_pay_to_b(participant[0], payer, money)

    def get_person_need_pay(self, name):
        payment = self.person_detail[name].payment
        income = self.person_detail[name].income

        person = [name for name in income.keys()]
        person.extend([name for name in payment.keys()])

        need_pay = {}
        for obj in person:
            need_pay[obj] = (income.get(obj, 0)) - (payment.get(obj, 0))

        self.person_detail[name].need_pay = need_pay


if __name__ == '__main__':
    csv_file = '/Users/mayne/bill.csv'

    bill = Bill(csv_file)
    bill.handle_bill()
    bill.get_all_person()

    for name, detail in bill.person_detail.items():
        bill.get_person_need_pay(name)
        detail.print_need_pay()
