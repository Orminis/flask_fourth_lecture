import enum
from marshmallow_enum import EnumField
from marshmallow import Schema, fields, ValidationError, validates

from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


app = Flask(__name__)

db_user = config("DB_USER")
db_password = config("DB_PASSWORD")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{db_user}:{db_password}@localhost:5433/clothes"

db = SQLAlchemy(app)
api = Api(app)
migrate = Migrate(app, db)


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


class ColorEnum(enum.Enum):
    pink = "pink aa"
    black = "black"
    white = "white"
    yellow = "yellow"


class SingleClothSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    color = EnumField(ColorEnum, by_value=True)
    size = EnumField(SizeEnum, by_value=True)
    create_on = fields.DateTime()
    updated_on = fields.DateTime()


class UserOutShema(Schema):
    id = fields.Integer()
    full_name = fields.String()
    clothes = fields.List(fields.Nested(SingleClothSchema), many=True)


class UserSignInSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String()
    password = fields.String(required=True)

    @validates("full_name")
    def validate_name(self, value):
        try:
            first_name, last_name = value.split()
        except ValueError:
            raise ValidationError(
                "Full name should consists of first and last name at least"
            )

        if len(first_name) < 3 or len(last_name) < 3:
            raise ValueError("Name should be at least 3 characters")


users_clothes = db.Table(
    "users_clothes",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("clothes_id", db.Integer, db.ForeignKey("clothes.id")),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Text)
    create_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())
    clothes = db.relationship("Clothes", secondary=users_clothes)


class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color = db.Column(db.Enum(ColorEnum), default=ColorEnum.white, nullable=False)
    size = db.Column(db.Enum(SizeEnum), default=SizeEnum.s, nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    create_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())


class SignUp(Resource):
    def post(self):
        data = request.get_json()
        schema = UserSignInSchema()
        errors = schema.validate(data)
        if not errors:
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            return data, 201
        return errors, 400


class UserResource(Resource):
    def get(self, pk):
        user = User.query.filter_by(id=pk).first()
        return UserOutShema().dump(user)


api.add_resource(SignUp, "/register/")
api.add_resource(UserResource, "/users/<int:pk>/")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
