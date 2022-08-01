import datetime as _datetime
import sqlalchemy as _sqlalchemy
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import database as _database

class UserModel(_database.Base):
    __tablename__ = "users"
    id = _sqlalchemy.Column(_sqlalchemy.Integer, primary_key=True, index=True)
    email = _sqlalchemy.Column(_sqlalchemy.String, unique=True, index=True)
    name = _sqlalchemy.Column(_sqlalchemy.String)
    phone = _sqlalchemy.Column(_sqlalchemy.String)
    password_hash = _sqlalchemy.Column(_sqlalchemy.String)
    created_at = _sqlalchemy.Column(_sqlalchemy.DateTime, default=_datetime.datetime.utcnow())
    address = _orm.relationship("addressModel", back_populates="user")

    def password_verification(self, password: str):
        return _hash.bcrypt.verify(password,self.password_hash)

class addressModel(_database.Base):
    __tablename__ = "address"
    id = _sqlalchemy.Column(_sqlalchemy.Integer, primary_key=True, index=True)
    user_id = _sqlalchemy.Column(_sqlalchemy.Integer, _sqlalchemy.ForeignKey("users.id"))
    x = _sqlalchemy.Column(_sqlalchemy.Integer, index=True)
    y = _sqlalchemy.Column(_sqlalchemy.Integer, index=True)
    created_at = _sqlalchemy.Column(_sqlalchemy.DateTime, default=_datetime.datetime.utcnow())
    user = _orm.relationship("UserModel", back_populates="address")