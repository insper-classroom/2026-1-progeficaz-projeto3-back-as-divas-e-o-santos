from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages, Blueprint, jsonify
from dotenv import load_dotenv
from banco import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_mailman import EmailMessage, Mail
import os
import secrets
from datetime import datetime, timedelta
from services.services_adm import validar_produto,criar_produto
import cloudinary
import cloudinary.uploader


adm_bp = Blueprint('admin', __name__)

@adm_bp.route('/registro', methods=['POST'])
def registro():
    data, error = validar_produto(request)

    if error:
        return error

    result = cloudinary.uploader.upload(data["file"])

    produto = criar_produto({
        **data,
        "image_url": result["secure_url"]
    })

    return {"msg": "Produto criado", "produto": produto}
