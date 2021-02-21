def test_naked_get_says_hello(client):
    response = client.get('/api/hello')
    json = response.get_json()
    assert json['error_code'] == 0
    assert json['message'] == 'Hello, World!'
