# posts/tests/test_404.py
# test_404_returns_custom_template
def test_404_returns_custom_template():
    # Создаем экземпляр клиента
    guest_client = Client()
    # обратимся к несуществующей странице, убедимся, 
    response = guest_client.get('/')
    # что возвращается шаблон core/404.html
    self.assertRedirects(response, 'core/404.html')