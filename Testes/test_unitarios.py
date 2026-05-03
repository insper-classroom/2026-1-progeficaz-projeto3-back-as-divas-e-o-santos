from urllib import response
from servidor import app
from services.services_auth import valida_informacoes, alterar_senha
from unittest.mock import patch, MagicMock
import pytest   
import json
import requests

@pytest.fixture
def mock_db():
    #Simulação do banco de dados no MongoDB
    db = MagicMock()
    return db


def test_email_al_insper_valido(mock_db):
     #Email @al.insper.edu.br deve ser aceito   
    mock_db.users.find_one.return_value = None  # usuário não existe ainda

    result, erro = valida_informacoes(
        mock_db, "Nicole Common", "nicole@al.insper.edu.br", "senha123"
    )

    assert erro is None
    assert result is not None


def test_email_insper_valido(mock_db):
    """Email @insper.edu.br deve ser aceito"""
    mock_db.users.find_one.return_value = None

    result, erro = valida_informacoes(
        mock_db, "Price Prairie", "price@insper.edu.br", "senha123"
    )

    assert erro is None
    assert result is not None


def test_email_gmail_invalido(mock_db):
    """Email @gmail.com deve ser rejeitado"""
    result, erro = valida_informacoes(
        mock_db, "Taylor Ranch", "taylor@gmail.com", "senha123"
    )

    assert result is None
    assert erro == "Use um email institucional da faculdade."


def test_email_hotmail_invalido(mock_db):
    """Email @hotmail.com deve ser rejeitado"""
    result, erro = valida_informacoes(
        mock_db, "Michele Vidal", "michele@hotmail.com", "senha123"
    )

    assert result is None
    assert erro == "Use um email institucional da faculdade."


# --- Testes dos outros critérios de valida_informacoes ---

def test_senha_curta(mock_db):
    """Senha com menos de 8 caracteres deve ser rejeitada"""
    result, erro = valida_informacoes(
        mock_db, "Nicole Common", "nicole@al.insper.edu.br", "123"
    )

    assert result is None
    assert erro == "Senha muito curta. Use pelo menos 8 caracteres."


def test_usuario_ja_cadastrado(mock_db):
    """Usuário já existente no banco deve ser rejeitado"""
    mock_db.users.find_one.return_value = {"email": "nicole@al.insper.edu.br"}

    result, erro = valida_informacoes(
        mock_db, "Nicole Common", "nicole@al.insper.edu.br", "senha123"
    )

    assert result is None
    assert erro == "Usuário já cadastrado."


def test_alterar_senha_email_inexistente(mock_db):
    """Usuário já existente no banco deve ser rejeitado"""
    mock_db.users.find_one.return_value = None

    result, erro = alterar_senha(
        mock_db, "inexistente@al.insper.edu.br"
    )

    assert result is None
    assert erro == "Este email não está cadastrado."

