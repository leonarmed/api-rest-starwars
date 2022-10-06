from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, and_
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, delete

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    lname = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=False, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    favorites = relationship("Favorites")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lname": self.lname,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    pers_id = db.Column(db.Integer, ForeignKey('characters.id'))
    planet_id = db.Column(db.Integer, ForeignKey('planets.id'))

    @classmethod
    def add_favorite(cls, id_to_add_favorite, user_id, type_of_favorite):
        try:
            if type_of_favorite == 'planet':
                exist = Planets.query.filter_by(id=id_to_add_favorite).one_or_none()
            elif type_of_favorite == 'people':
                exist = Characters.query.filter_by(id=id_to_add_favorite).one_or_none()
            if not exist:
                raise Exception({
                    "message": f"This {type_of_favorite} doesn't exist",
                    "status": 404
                })
            
            if type_of_favorite == 'planet':
                favorite_exist = cls.query.filter_by(user_id=user_id, planet_id=id_to_add_favorite).all()
            elif type_of_favorite == 'people':
                favorite_exist = cls.query.filter_by(user_id=user_id, pers_id=id_to_add_favorite).all()

            if list(favorite_exist).__len__() > 0:
                raise Exception({
                    "message": "This favorite already exist",
                    "status": 404
                })
            
            if type_of_favorite == 'planet':
                new_favorite = cls(user_id=user_id, planet_id=id_to_add_favorite)
            elif type_of_favorite == 'people':
                new_favorite = cls(user_id=user_id, pers_id=id_to_add_favorite)
            if not isinstance(new_favorite, cls):
                return jsonify({
                    "message": new_favorite["message"],
                    "success": False
                }), new_favorite["status"]
            saved = new_favorite.save_and_commit()
            if not saved:
                raise Exception({
                    "message": "Database error",
                    "status": 500
                })
            return new_favorite
        except Exception as error:
            return error.args[0]

    @classmethod
    def delete_favorite(cls, id_to_remove_favorite, user_id):
        try:
            exist = Favorites.query.filter_by(id=id_to_remove_favorite, user_id=user_id).one_or_none()
            if not exist:
                raise Exception({
                    "message": "This favorite does exist",
                    "status": 404
                })
                
            favorite_to_delete = Favorites.query.get_or_404(id_to_remove_favorite)
            try:
                db.session.delete(favorite_to_delete)
                db.session.commit()
                return True
            except Exception as error:
                return jsonify({
                    "success": False,
                    "message": "Error internal application"
                }), 500
            return(deleted)
        except Exception as error:
            return error.args[0]

    def save_and_commit(self):
        """
            Salva la instancia creada, en la base de datos. Si sucede algún error, 
            se retorna False y se revierten los cambios de la sesión
        """
        try:
            db.session.add(self)  #Guardamos la instancia en la sessión
            db.session.commit() #Creamos el registro en la db 
            return True
        except Exception as error:

            db.session.rollback() #Retornamos a la session mas reciente
            return False

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "pers_id": self.pers_id,
            "planet_id": self.planet_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    diameter = db.Column(db.String(250), nullable=False)
    gravity = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    favorites = relationship("Favorites")

    @classmethod
    def create(cls, body):
        try:
            planet_is_valid = cls.planet_exist(name=body.get("name"))
            if planet_is_valid == False:
                raise Exception({
                    "message": "This planet already exist",
                    "status": 400
                })
            if planet_is_valid != True:
                raise Exception({
                    "message": "Internal application error",
                    "status": 500
                })
            new_planet = cls(name=body["name"], diameter=body["diameter"], gravity=body["gravity"])
            if not isinstance(new_planet, cls):
                raise Exception({
                    "message": "Instance Error",
                    "status": 500
                })
            saved = new_planet.save_and_commit()

            if not saved:
                raise Exception({
                    "message": "Database error",
                    "status": 500
                })
            return new_planet
        except Exception as error:
            return error.args[0]

    @classmethod
    def planet_exist(cls, **kwargs):
        try:
            planet_exist = cls.query.filter_by(name=kwargs["name"]).one_or_none()
            if planet_exist:
                return False
            return True
        except Exception as error:
            return error.args[0]

    def save_and_commit(self):
        """
            Salva la instancia creada, en la base de datos. Si sucede algún error, 
            se retorna False y se revierten los cambios de la sesión
        """
        try:
            db.session.add(self)  #Guardamos la instancia en la sessión
            db.session.commit() #Creamos el registro en la db 
            return True
        except error:
            db.session.rollback() #Retornamos a la session mas reciente
            return False

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Characters(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    height = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    favorites = relationship("Favorites")

    @classmethod
    def create(cls, body):
        try:
            character_is_valid = cls.character_exist(name=body.get("name"))
            if character_is_valid == False:
                raise Exception({
                    "message": "This character already exist",
                    "status": 400
                })
            if character_is_valid != True:
                raise Exception({
                    "message": "Internal application error",
                    "status": 500
                })
            new_character = cls(name=body["name"], gender=body["gender"], height=body["height"])
            if not isinstance(new_character, cls):
                raise Exception({
                    "message": "Instance Error",
                    "status": 500
                })
            print(new_character)
            saved = new_character.save_and_commit()

            if not saved:
                raise Exception({
                    "message": "Data base error",
                    "status": 500
                })
            return new_character
        except Exception as error:
            return error.args[0]

    @classmethod
    def character_exist(cls, **kwargs):
        try:
            character_exist = cls.query.filter_by(name=kwargs["name"]).one_or_none()
            if character_exist:
                return False
            return True
        except Exception as error:
            return error.args[0]

    def save_and_commit(self):
        """
            Salva la instancia creada, en la base de datos. Si sucede algún error, 
            se retorna False y se revierten los cambios de la sesión
        """
        try:
            db.session.add(self)  #Guardamos la instancia en la sessión
            db.session.commit() #Creamos el registro en la db 
            return True
        except error:
            db.session.rollback() #Retornamos a la session mas reciente
            return False

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

def error_server(self):
    return jsonify({
        "success": False,
        "message":"Error internal application"
    }), 500