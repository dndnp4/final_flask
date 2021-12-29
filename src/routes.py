import json
from flask import current_app as app
from flask import Flask, request, Response, render_template, jsonify, make_response
from .models import Users, File, GameToken, GameResult
from .encrypt import create_salt, encrypt_password
from .uploader import run, get_object_list
from .notify import send_email, send_sms
from config import AWSConfig

@app.route('/signup', methods=['POST'])
def sign_up():
    try:
        body = json.loads(request.get_data(), encoding='utf-8')
        id = body['id']
        pw1 = body['pw1']
        pw2 = body['pw2']
        if pw1 != pw2:
            raise Exception('Unmatched')
        salt = create_salt()
        encrypted = encrypt_password(pw1, salt)
        salt = salt.hex()

        result = Users.insert(id, encrypted, salt)
        if result :
            send_email()
            send_sms()
            return '계정이 생성되었습니다.'
        raise Exception('AlreadyExist')    
    except Exception as e:
        print(e)
        e = str(e)
        message = ''
        if e == 'Unmatched':
            message = '비밀번호가 일치하지 않습니다.'
        elif e == 'AlreadyExist':
            message = '이미 존재하는 계정입니다.'
        else:
            message = '오류가 발생했습니다.'
        
        return make_response(message, 400)

@app.route('/signin', methods=['POST'])
def sign_in():
    try:
        body = json.loads(request.get_data(), encoding='utf-8')
        id = body['id']
        pw = body['pw']
        round = body['round']

        user = Users.select(id, 'json')
        encrypted = encrypt_password(pw, bytes.fromhex(user.salt))
        if user.pw == encrypted:
            token = create_salt(16).hex()
            GameToken.insert(user.user_id, token)
            return jsonify({'token': token, 'id': user.user_id})
        raise Exception()

    except Exception as e:
        print(e)
        return make_response('로그인 정보가 일치하지 않습니다.',400)

@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if request.method == 'GET':
        return render_template('uploader.html')
    else:
        # please only image types.........
        # file = request.files['file']
        files = request.files.getlist('file')
        for file in files:
            temp = file.filename.split('.')
            new_filename = create_salt(20).hex()
            ext = temp[-1]
            file.filename = new_filename + '.' + ext
            run(file)
            File.insert(new_filename, ext)
        return Response(status=200)

@app.route('/game', methods=['GET', 'POST'])
def game():
    try:
        if request.method == 'GET':
            rnd = request.args.get('rnd')
            token = request.args.get('token')
            id = request.args.get('id')
            
            if not GameToken.is_valid_token(id, token):
                raise

            if rnd in ['32', '16', '8'] :
                return render_template('game.jinja', 
                    domain=AWSConfig.ORIGIN_BUCKET_DOMAIN,
                    images=File.get_files_by_rnd(rnd), 
                    rnd=rnd, 
                    token=token,
                    id=id
                )

            else:
                raise
        else:
            body = json.loads(request.get_data(), encoding='utf-8')
            id = body['id']
            token = body['token']
            rnd = body['rnd']
            file_id = body['file_id']

            if rnd not in ['32', '16', '8'] :
                raise
            if not GameToken.is_valid_token(id, token) :
                raise
            
            file = File.select(file_id, 'json')
            if file is None:
                raise
            
            game_id = GameResult.insert(id, file_id, rnd)
            GameToken.delete(id)
            return jsonify({'game_id' : game_id})
            
    except Exception as e:
        print(e)
        return 'Error'
        

@app.route('/result', methods=['GET'])
def result():
    try:
        game_id = request.args.get('game_id')
        top_data = GameResult.select_top3()
        file_data = File.get_file_by_game_id(game_id)
        top1 = File.select(top_data[0].file_id)
        top2 = File.select(top_data[1].file_id)
        top3 = File.select(top_data[2].file_id)
        return render_template(
            'result.jinja', 
            result='%s/%s.%s' % (AWSConfig.ORIGIN_BUCKET_DOMAIN, file_data.name, file_data.type),
            top1='%s/%s.%s' % (AWSConfig.ORIGIN_BUCKET_DOMAIN, top1.name, top1.type),
            top2='%s/%s.%s' % (AWSConfig.ORIGIN_BUCKET_DOMAIN, top2.name, top2.type),
            top3='%s/%s.%s' % (AWSConfig.ORIGIN_BUCKET_DOMAIN, top3.name, top3.type),
        )
    except Exception as e:
        print(e)
        return 'Error'

@app.route('/gallery', methods=['GET'])
def gallery():
    try:
        images = File.get_all()
        return render_template(
            'gallery.jinja',
            images=images,
            origin=AWSConfig.ORIGIN_BUCKET_DOMAIN,
            thumb=AWSConfig.TUMB_BUCKET_DOMAIN
        )
    except Exception as e:
        print(e)
        return 'Error'

@app.route('/origin', methods=['GET'])
def origin():
    src = request.args.get('src')
    return render_template(
        'origin.jinja',
        src='%s/%s' % (AWSConfig.ORIGIN_BUCKET_DOMAIN, src)
    )