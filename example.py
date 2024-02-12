from flask import Flask, flash, get_flashed_messages, render_template, request, redirect, url_for, session
import json
import os
# Это callable WSGI-приложение

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

user_list = ['mike', 'mishel', 'adel', 'keks', 'kamila']
ip = 0

def validate(user):
    errors = {}
    if not user['nickname']:
        errors['nickname'] = "Can't be blank"
    if len(user['nickname']) < 4:
        errors['nickname'] = "Nickname must be greater than 3 characters"
        return errors
    if not user['email']:
        errors['email'] = "Can't be blank"
    return errors


def validate_login(login):
    errors = {}
#    users = session.get('users')
    users = list(json.loads(request.cookies.get('users', json.dumps({}))))
    if users != None:
        for i in users:
            if i['email'] == login:
                return
    errors['login'] = 'No such user'
    return errors
    
    

def validate_nick(user):
    errors = {}
    if not user['nickname']:
        errors['nickname'] = "Can't be blank"
    if len(user['nickname']) < 4:
        errors['nickname'] = 'Nickname must be greater than 3 characters'
    return errors


def filter_users(term):
    final_list = []
    for elements in user_list:
        if term in elements:
            final_list.append(elements)
    return final_list
        

@app.route('/')
def index():
    return 'Hello, World!'


#@app.route('/users')
#def users_get():
#    term = request.args.get('term')
#    if term:
#        filtered_users = filter_users(term)
#    else:
#        filtered_users = user_list
#    return render_template(
#        'users/index.html',
#        users=filtered_users,
#        search=term
#    )


# @app.post('/users')
# def users():
#    return 'Users', 302


@app.route('/courses/<id>')
def courses(id):
    return f'Course id: {id}'



@app.route('/users/<id>')
def users(id):
    return render_template('users/show.html', name=id,)


@app.route('/users/new')
def users_new():
    user = {'nickname': '',
            'email': ''}
    errors = {}
#    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'users/new.html',
        user=user,
        errors=errors, 
        # messages=messages
    )

@app.post('/users')
def users_post():
    data = ''
#    with open('data.json', 'r') as file:
#        file_data = file.read()
#        if file_data != '\n' and file_data != 'null':
#            data = json.loads(file_data)
    user = request.form.to_dict()
    errors = validate(user)
    if errors:
        return render_template(
          'users/new.html',
          user=user,
          errors=errors,
        ), 422
    data = json.loads(request.cookies.get('users', json.dumps({})))
    global ip
    ip += 1
    user['id'] = ip
    if data != None:
        new_data = list(data) + [user]
    else:
        new_data = [user]
#    with open('data.json', 'w+') as f:
#        f.write(json.dumps(new_data))
    encoded_users = json.dumps(new_data)
    flash('User was added successfully', 'success')
    response =  redirect(url_for('user'), code=302)
    response.set_cookie('users', encoded_users)
    return response


@app.route('/users')
def user():
    users = []
   # with open('data.json', 'r') as file:
   #     users_dicts = json.loads(file.read())
   # if users_dicts != 'null' and users_dicts != '\n':
   #     for i in users_dicts:
   #         users.append(i)
   # file.close()
    data = json.loads(request.cookies.get('users', json.dumps({})))
    if data != None:    
        for i in data:
            users.append(i)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'users/index.html',
        users=users, messages=messages
    )


@app.route('/users/<int:id>')
def get_user(id):
    user = ''
    with open('data.json', 'r') as file:
        data_file = json.loads(file.read())
    for item in data_file:
        if item['id'] == id:
            user = item
    if user == '':
        return f'user id{id} Page not found!!!', 404
    return render_template('users/show.html', 
user=user, )


@app.route('/users/<int:id>/edit')
def edit_user(id):
    with open('data.json', 'r') as file:
        data_file = json.loads(file.read())
    for item in data_file:
        if item['id'] == id:
            user = item
    errors = []
    return render_template(
           'users/edit.html',
           user=user,
           errors=errors,
    )


@app.route('/users/<int:id>/patch', methods=['POST'])
def patch_user(id):
    with open('data.json', 'r') as file:
        data_file = json.loads(file.read())
    for item in data_file:
        if item['id'] == id:
            user = item
            break
    data = request.form.to_dict()
    file.close()
    errors = validate_nick(data)
    if errors:
        return render_template(
            'users/edit.html',
            user=user,
            errors=errors,
        ), 422

    # Ручное копирование данных из формы в нашу сущность
    user['nickname'] = data['nickname']
    data_file.remove(item)
    new_data = data_file + [user]
    with open('data.json', 'w+') as f:
        f.write(json.dumps(new_data))
    flash('User has been updated', 'success')
    return redirect(url_for('user'))


@app.route('/user/<id>/delete', methods=['POST'])
def delete_user(id):
    with open('data.json', 'r') as file:
        data_f = json.loads(file.read())
    for element in data_f:
        if element['id'] == int(id):
#            id = id + 1
            data_f.remove(element)
            file.close()
            break
    new_data_file = data_f
    with open('data.json', 'w+') as f:
        f.write(json.dumps(new_data_file))
    flash(f'{data_f}{type(id)}User id{id} has been deleted', 'success')
    return redirect(url_for('user'))


# @app.route('/users/<int:id>/delete')
# def remove_user(id):
#    with open('data.json', 'r') as file:
#        data_file = json.loads(file.read())
#    for item in data_file:
#        if item['id'] == id:
#            user = item
#            file.close()
#    return render_template(
#           'users/delete.html',
#           user=user
#    )



@app.route('/users/auth')
def users_auth():
    user = {'email': ''}
    errors = {}
#    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'users/auth.html',
        user=user,
        errors=errors,
        # messages=messages
    )

@app.post('/users/auth')
def users_apost():
    data = ''
#    with open('data.json', 'r') as file:
#        file_data = file.read()
#        if file_data != '\n' and file_data != 'null':
#            data = json.loads(file_data)
    user = request.form.to_dict()
    login = user['login']
    errors = validate_login(login)
    if errors:
        return render_template(
          'users/auth.html',
          user=user,
          errors=errors,
        ), 422
    session['login'] = login
    flash('User was logged in  successfully', 'success')
    return  redirect(url_for('user'), code=302)


@app.route("/users/authdelelete", methods=['POST', 'DELETE'])
def session_delete():
    session.pop('login')
    return redirect(url_for('users_auth'))
