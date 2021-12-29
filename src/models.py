"""Data models."""
import json
from . import db
from datetime import datetime

class Users(db.Model):

    __tablename__ = 'user'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(20))
    pw = db.Column(db.String(100))
    salt = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=datetime.now().replace(microsecond=0))

    def __init__(self, id, pw, salt, date):
        # self.user_id = user_id
        self.id = id
        self.pw = pw
        self.salt = salt
        self.date = date

    def search_events_by_id(id, get):
        if get == 'json' : 
            result = Users.query.filter_by(id=id).all()
        else : 
            result = Users.query.filter_by(id=id).first()

        return result

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    def __repr__(self):
        data = {
            'user_id' : self.user_id,
            'id' : self.id,
            'pw' : self.pw,
            'salt' : self.salt,
            'date' : str(self.date)
        }
        json_data = json.dumps(data, indent = 4)
        return json_data

    def select(id, get='all') :
        result = Users.search_events_by_id(id, get)
        if result != None :
            if get == 'user_id' :
                result = result.user_id
            elif get == 'id' :
                result = result.id 
            elif get == 'pw' :
                result = result.pw
            elif get == 'salt' :
                result = result.salt
            elif get == 'date' :
                result = result.date
            elif get == 'json' :
                result = result[0]
        return result

    def insert(id, pw, salt) :
        if id == Users.select(id, 'id'):
            return False

        record = Users(id, pw, salt ,datetime.now().replace(microsecond=0))
        db.session.add(record)
        db.session.commit()
        return True

class File(db.Model):
    __tablename__ = 'file'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    file_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, name, type, date):
        self.name = name
        self.type = type
        self.date = date

    def search_events_by_file_id(file_id, get):
        if get == 'json' : 
            result = File.query.filter_by(file_id=file_id).all()
        else : 
            result = File.query.filter_by(file_id=file_id).first()
        
        return result

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    def __repr__(self):
        data = {
            'file_id' : self.file_id,
            'name' : self.name,
            'type' : self.type,
            'date' : str(self.date)
        }
        json_data = json.dumps(data)

        return json_data
    
    def select(file_id, get='json'):
        result = File.search_events_by_file_id(file_id, get)
        if result != None :
            if get == 'file_id' :
                result = result.file_id
            elif get == 'name' :
                result = result.name
            elif get == 'type' :
                result = result.type
            elif get == 'date' :
                result = result.date
            elif get == 'json' :
                result = result[0]
        return result

    def insert(name, type):
        record = File(name, type, datetime.now().replace(microsecond=0))
        db.session.add(record)
        db.session.commit()
        
    def get_all():
        record = File.query.order_by(db.desc(File.file_id)).all()
        return record

    def get_file_by_game_id(game_id):
        # join not working..... 
        record = GameResult.select(game_id)
        record = File.select(record.file_id)
        return record

    def get_files_by_rnd(rnd):
        result = File.query.order_by(db.func.rand()).limit(rnd).all()
        return result

class GameResult(db.Model):
    __tablename__ = 'game_result'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_id = db.Column(db.Integer)
    rnd = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, user_id, file_id, rnd, date):
        self.user_id = user_id
        self.file_id = file_id
        self.rnd = rnd
        self.date = date

    def search_events_by_game_id(game_id, get):
        if get == 'json' : 
            result = GameResult.query.filter_by(game_id=game_id).all()
        else : result = GameResult.query.filter_by(game_id=game_id).first()
        
        return result

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    def __repr__(self):
        data = {
            'game_id' : self.game_id,
            'user_id' : self.user_id,
            'file_id' : self.file_id,
            'rnd' : self.rnd,
            'date' : str(self.date)
        }
        json_data = json.dumps(data)

        return json_data

    def select(game_id, get='json'):
        result = GameResult.search_events_by_game_id(game_id, get)
        if result != None :
            if get == 'game_id' :
                result = result.game_id
            elif get == 'user_id' :
                result = result.user_id
            elif get == 'file_id' :
                result = result.file_id
            elif get == 'rnd' :
                result = result.rnd
            elif get == 'json' :
                result = result[0]
        return result
    
    def select_top3():
        result = db.session.query(GameResult.file_id, db.func.count()).group_by('file_id').order_by(db.desc(db.func.count())).limit(3).all()
        data = []
        for file_id, rank in result:
            temp = File.select(file_id)
            data.append(temp)
        return data

    def insert(user_id, file_id, rnd):
        record = GameResult(user_id, file_id, rnd, datetime.now().replace(microsecond=0))
        db.session.add(record)
        db.session.commit()
        return record.game_id

class GameToken(db.Model):
    __tablename__ = 'game_token'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(40))
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, user_id, token, date):
        self.user_id = user_id
        self.token = token
        self.date = date

    def search_events_by_user_id(user_id, get):
        if get == 'json' : 
            result = GameToken.query.filter_by(user_id=user_id).all()
        else : result = GameToken.query.filter_by(user_id=user_id).first()
        
        return result

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    def __repr__(self):
        data = {
            'user_id' : self.user_id,
            'token' : self.token,
            'date' : str(self.date)
        }
        json_data = json.dumps(data)

        return json_data

    def select(user_id, get):
        result = GameToken.search_events_by_user_id(user_id, get)
        if result != None :
            if get == 'user_id' :
                result = result.user_id
            elif get == 'token' :
                result = result.token
            elif get == 'date' :
                result = result.date
            elif get == 'json' :
                result = result[0]
        return result

    def insert(user_id, token):
        if user_id == GameToken.select(user_id, 'user_id'):
            # already exists.. update
            result = GameToken.query.filter_by(user_id=user_id).first()
            result.token = token
            result.date = datetime.now().replace(microsecond=0)
        else:
            record = GameToken(user_id, token, datetime.now().replace(microsecond=0))
            db.session.add(record)
        db.session.commit()

    def delete(user_id):
        result = GameToken.query.filter_by(user_id=user_id).first()
        db.session.delete(result)
        db.session.commit()

    def is_valid_token(user_id, token):
        result = GameToken.select(user_id, 'token')
        if result == token:
            return True
        return False
