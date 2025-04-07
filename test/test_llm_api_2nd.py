import pytest
from unittest.mock import patch
from LLM import call_llama_api, process_response, send_query

# TC-LLM-API-001-01: Sėkminga užklausa
@patch('LLM.requests.post')
def test_successful_response(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "- Patiekalas: Blynai"}}]
    }
    response = call_llama_api("valgiau blynus")
    assert "text" in response
    assert "- Patiekalas: Blynai" in response["text"]

# TC-LLM-API-001-02: Tuščia užklausa
def test_empty_query():
    result = send_query("   ")
    assert result == "Prašome įvesti tinkamą patiekalą."

# TC-LLM-API-001-03: Netinkamas API raktas (401)
@patch('LLM.requests.post')
def test_invalid_api_key(mock_post):
    from requests.exceptions import HTTPError
    mock_post.return_value.raise_for_status.side_effect = HTTPError("401 Client Error: Unauthorized")
    result = call_llama_api("valgiau kebabą")
    assert "error" in result
    assert "401" in result["error"]

# TC-LLM-API-001-04: Tinklo klaida (503)
@patch('LLM.requests.post')
def test_network_error(mock_post):
    from requests.exceptions import ConnectionError
    mock_post.side_effect = ConnectionError("Tinklo klaida")
    result = call_llama_api("valgiau cepelinus")
    assert "error" in result
    assert "Klaida jungiantis" in result["error"]

# TC-LLM-API-001-05: Atsakymas be patiekalų
def test_response_without_dishes():
    response = {"text": "Gėriau tik arbatą ir vandenį."}
    result = process_response(response)
    assert result == "Maisto produktų nerasta."

# TC-LLM-API-001-06: Tinkamas atsakymas su cepelinais
def test_response_with_dish():
    response = {"text": "- Patiekalas: Cepelinai su mėsa"}
    result = process_response(response)
    assert "Aptikti patiekalai" in result
    assert "Cepelinai" in result
