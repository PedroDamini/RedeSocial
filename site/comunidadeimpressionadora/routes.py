from comunidadeimpressionadora import app, database, bcrypt
from flask import render_template, redirect, url_for, flash, request
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil
from comunidadeimpressionadora.models import Usuario
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

lista_usuarios = ['joao das cove', 'pedrin reidelas', 'polisorbato']

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/contatos")
def contatos():
    return render_template('contato.html')


@app.route("/usuarios")
@login_required
def usuarios():
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'falha no login e-mail ou senha incorretos', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript) 
        database.session.add(usuario)
        database.session.commit()
        print('request ', request.form)
        flash(f'conta criada com sucesso para o e-mail {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))

    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f'logout feito com sucesso', 'alert-success')
    return redirect(url_for('home'))

@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template('perfil.html',foto_perfil=foto_perfil)

@app.route("/post/criar")
@login_required
def criar_post():
    return render_template('criarpost.html')

############################################################################################################################################

def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (200, 200)
    #Reduzindo o tamanho da imagem
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    #Salvando
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)

############################################################################################################################################

@app.route("/perfil/editar", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash(f'perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username 
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("editarperfil.html", foto_perfil=foto_perfil, form=form)