from flask import render_template, session, redirect, url_for, current_app, flash, request
from .. import db
from ..models import User, Role
from ..email import send_email, send_simple_message
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    user_all = User.query.all();
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name='User').first();
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            print('FLASKY_ADMIN: ' + str(current_app.config['FLASKY_ADMIN']), flush=True)            
            if current_app.config['FLASKY_ADMIN']:
                #send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
                print('Enviando mensagem...', flush=True)
                send_simple_message([current_app.config['FLASKY_ADMIN'], "flaskaulasweb@zohomail.com", form.email.data], 'Novo usuário', form.name.data)
                print('Mensagem enviada...', flush=True)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index')) # Aciona o método index() novamente, mas agora com o método GET
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False), user_all=user_all)


@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuário removido com sucesso.', 'success')
    return redirect(url_for('.index'))


@main.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    new_username = request.form.get('new_username', '').strip()
    if new_username:
        user.username = new_username
        db.session.commit()
        flash('Nome do usuário atualizado com sucesso.', 'success')
    else:
        flash('Nome inválido.', 'warning')
    return redirect(url_for('.index'))
