"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, error_server, User, Characters, Planets, User, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route("/peoples", methods=['GET', 'POST'])
def get_peoples():
    if request.method == "GET":
        try:
            peoples = Characters.query.all()
            peoples_dict = list(map(lambda people: people.serialize(), peoples))
            return jsonify({
                "success": True,
                "peoples": peoples_dict
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message":"Error internal application"
            }), 500
    if request.method == "POST":
        body = request.json
        new_people = Characters.create(body)
        if not isinstance(new_people, Characters): #Si no es una instancia de Character, quiere decir que ocurrió un error
            return jsonify({
                "message": new_people["message"],
                "success": False
            }), new_people["status"]

        people = Characters.query.filter_by(name=new_people.name).one_or_none()  #Obtenemos el character para acceder al id, el cual es generado luego de que la instancia se guarda en la base de datos.
        return jsonify({
            "sucess": True,
            "people": people.serialize()
        }), 201

@app.route("/people/<int:id>")
def get_people_by_id(id):
    try:
        people = Characters.query.get(id)
        if people is None:
            return jsonify({
                "success": False,
                "message": "People doesn't exist"
            }), 404
        return jsonify({
            "success": True,
            "people": people.serialize()
        }), 200
    except Exception as error:
        return jsonify({
            "success": False,
            "message":"Error internal application"
        }), 500

@app.route("/favorite/people/<int:people_id>", methods=["POST", "DELETE"])
def favorite_people(people_id):
    user_id = 2
    if request.method == "POST":
        try:
            type_favorite = "people"
            new_favorite = Favorites.add_favorite(people_id, user_id, type_favorite)
            if not isinstance(new_favorite, Favorites):
                return jsonify({
                    "message": new_favorite['message'],
                    "success": False
                }), new_favorite['status']
            favorites = Favorites.query.filter_by(user_id=user_id).all()
            favorites_dict = list(map(lambda favorite: favorite.serialize(), favorites))
            return jsonify({
                "success": True,
                "favorites": favorites_dict
            }), 200
        except Exception as error:
            print(error, 'main error')
            return jsonify({
                "success": False,
                "message": "Error internal application"
            }), 500
    elif request.method == "DELETE":
        try:
            favorite_to_delete = Favorites.delete_favorite(people_id, user_id)
            if favorite_to_delete == True:
                try:
                    favorites = Favorites.query.filter_by(user_id=user_id).all()
                    favorites_dict = list(map(lambda favorite: favorite.serialize(), favorites))
                    return jsonify({
                        "success": True,
                        "favorites": favorites_dict
                    }), 200
                except Exception as error:
                    return jsonify({
                        "success": False,
                        "message": "Error internal application"
                    }), 500
            
            if not isinstance(favorite_to_delete, Favorites):
                return jsonify({
                        "message": favorite_to_delete['message'],
                        "success": False
                    }), favorite_to_delete['status']
        except Exception as Error:
            return jsonify({
                "success": False,
                "message": "Error internal application"
            }), 500

@app.route("/planets", methods=['GET', 'POST'])
def get_planets():
    if request.method == 'GET':
        try:
            planets = Planets.query.all()
            planets_dict = list(map(lambda planet: planet.serialize(), planets))
            return jsonify({
                "success": True,
                "planets": planets_dict
            }), 200
        except Exception as error:
            return jsonify({
                "success": False,
                "message":"Error internal application"
            }), 500
    if request.method == "POST":
        body = request.json
        new_planet = Planets.create(body)
        if not isinstance(new_planet, Planets):
            return jsonify({
                "message": new_planet["message"],
                "success": False
            }), new_planet["status"]
        
        planet = Planets.query.filter_by(name=new_planet.name).one_or_none()
        return jsonify({
            "success": True,
            "planet": planet.serialize()
        }), 201

@app.route("/favorite/planet/<int:planet_id>", methods=["POST", "DELETE"])
def favorite_planet(planet_id):
    user_id = 2
    if request.method == 'POST':
        try:
            type_favorite = "planet"
            new_favorite = Favorites.add_favorite(planet_id, user_id, type_favorite)
            if not isinstance(new_favorite, Favorites):
                return jsonify({
                    "message": new_favorite['message'],
                    "success": False
                }), new_favorite['status']
            favorites = Favorites.query.filter_by(user_id=user_id).all()
            favorites_dict = list(map(lambda favorite: favorite.serialize(), favorites))
            return jsonify({
                "success": True,
                "favorites": favorites_dict
            }), 200
        except Exception as error:
            return jsonify({
                "success": False,
                "message": "Error internal application"
            }), 500
    elif request.method == 'DELETE':
        try:
            favorite_to_delete = Favorites.delete_favorite(planet_id, user_id)
            if favorite_to_delete == True:
                try:
                    favorites = Favorites.query.filter_by(user_id=user_id).all()
                    favorites_dict = list(map(lambda favorite: favorite.serialize(), favorites))
                    return jsonify({
                        "success": True,
                        "favorites": favorites_dict
                    }), 200
                except Exception as error:
                    return jsonify({
                        "success": False,
                        "message": "Error internal application"
                    }), 500
            
            if not isinstance(favorite_to_delete, Favorites):
                return jsonify({
                        "message": favorite_to_delete['message'],
                        "success": False
                    }), favorite_to_delete['status']
        except Exception as Error:
            return jsonify({
                "success": False,
                "message": "Error internal application"
            }), 500

@app.route("/planet/<int:id>")
def get_planet_by_id(id):
    try:
        planet = Planets.query.get(id)
        if planet is None:
            return jsonify({
                "success": False,
                "message": "This planet doesn't exist"
            }), 404
        return jsonify({
            "success": True,
            "planet":  planet.serialize()
        }), 200
    except Exception as error:
         return jsonify({
            "success": False,
            "message":"Error internal application"
        }), 500

@app.route("/users")
def get_users():
    try:
        users = User.query.all()
        users_dict = list(map(lambda user: user.serialize(), users))
        return jsonify({
            "success":  True,
            "users": users_dict
        }), 200
    except Exception as error:
         return jsonify({
            "success": False,
            "message":"Error internal application"
        }), 500

@app.route("/user/<int:id>")
def get_user_by_id(id):
    try:
        user = User.query.get(id)
        if user is None:
             return jsonify({
                "success": False,
                "message":"User doesn't exist"
            }), 404
        return jsonify({
            "success": True,
            "user": user.serialize()
        })
    except Exception as error:
         return jsonify({
            "success": False,
            "message":"Error internal application"
        }), 500

@app.route("/user/favorites")
def get_favorites_by_user():
    try:
        id_user = 1
        favorites = Favorites.query.filter_by(user_id = id_user)
        favorites_dict = list(map(lambda favorite: favorite.serialize(), favorites))
        return jsonify({
            "success": True,
            "favorites": favorites_dict
        })
    except Exception as error:
        return jsonify({
            "success": False,
            "message":"Error internal application"
        }), 500

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
