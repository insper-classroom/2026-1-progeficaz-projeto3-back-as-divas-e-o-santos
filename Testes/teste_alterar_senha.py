from urllib import response
from servidor import app
from services import valida_informacoes, alterar_senha
from unittest.mock import patch, MagicMock
import pytest   
import json
import requests


def test_alterar_senha_sucesso(mock_db):
    """Email existente no banco deve retornar sucesso"""
    mock_db.users.find_one.return_value = {
        "email": "nicole@al.insper.edu.br",
        "nome": "Nicole Common"
    }

    with patch("tasks.tasks.alterar_senha") as mock_task:
        mock_task.delay.return_value = None
        result, erro, status = alterar_senha(mock_db, "nicole@al.insper.edu.br")

    assert erro is None
    assert status == 200
    assert result["email"] == "nicole@al.insper.edu.br"


def test_alterar_senha_email_nao_encontrado(mock_db):
    """Email inexistente no banco deve retornar 404"""
    mock_db.users.find_one.return_value = None

    result, erro, status = alterar_senha(mock_db, "inexistente@al.insper.edu.br")

    assert result is None
    assert status == 404
    assert erro == "Este email não está cadastrado."