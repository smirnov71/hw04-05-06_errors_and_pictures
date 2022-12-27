# posts/tests/test_main_cash.py
# on main page record stored and refreshed every 20 seconds
def cash_20():
# создадим тестовую запись  POST_00 на главной странице, 
# изменим его на POST_19 и через 19.9 сек сравним- не должно измениться
# обратимся через 20.1 сек, сравним - должно измениться
