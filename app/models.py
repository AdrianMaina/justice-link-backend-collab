from . import db
from datetime import datetime
from app import bcrypt

class CaseUser(db.Model):
    __tablename__ = 'case_user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), primary_key=True)
    role = db.Column(db.String(50), nullable=False) 

    user = db.relationship('User', back_populates='cases_association')
    case = db.relationship('Case', back_populates='users_association')

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    reports = db.relationship('Report', backref='author', lazy='dynamic')
    admin_logs = db.relationship('AdminLog', backref='admin_user', lazy='dynamic')
    cases_association = db.relationship('CaseUser', back_populates='user')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    date_of_incident = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pending') # e.g., Pending, Verified, Rejected
    is_anonymous = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class NewsArticle(db.Model):
    __tablename__ = 'news_article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100))
    read_more_link = db.Column(db.String(500), nullable=True)
    published_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Case(db.Model):
    __tablename__ = 'case'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Open')
    
    users_association = db.relationship('CaseUser', back_populates='case')

class AdminLog(db.Model):
    __tablename__ = 'admin_log'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)