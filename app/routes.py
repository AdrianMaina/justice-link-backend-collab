# app/routes.py

from flask import Blueprint, request, jsonify
from .models import db, Report, NewsArticle, User, AdminLog
from .schemas import ReportSchema, NewsArticleSchema, UserSchema
from .auth import token_required, admin_required
from marshmallow import ValidationError

api = Blueprint('api', __name__)

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)
news_article_schema = NewsArticleSchema()
news_articles_schema = NewsArticleSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

@api.route('/home_summary', methods=['GET'])
def home_summary():
    reports_count = Report.query.count()
    news_count = NewsArticle.query.count()
    return jsonify({
        "reportsCount": reports_count,
        "newsCount": news_count
    })

@api.route('/reports', methods=['POST'])
@token_required
def create_report(current_user):
    json_data = request.get_json()
    try:
        data = report_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_report = Report(
        title=data['title'],
        description=data['description'],
        location=data.get('location'),
        is_anonymous=data.get('is_anonymous', False),
        author=current_user
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify(report_schema.dump(new_report)), 201

@api.route('/reports', methods=['GET'])
@token_required
def get_reports(current_user):
    all_reports = Report.query.order_by(Report.date_of_incident.desc()).all()
    return jsonify(reports_schema.dump(all_reports)), 200

# New endpoint for user-specific reports
@api.route('/my_reports', methods=['GET'])
@token_required
def get_my_reports(current_user):
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_of_incident.desc()).all()
    return jsonify(reports_schema.dump(user_reports)), 200

@api.route('/news', methods=['GET'])
def get_news_articles():
    articles = NewsArticle.query.order_by(NewsArticle.published_date.desc()).all()
    return jsonify(news_articles_schema.dump(articles)), 200

# Admin - News Management
@api.route('/admin/news', methods=['POST'])
@admin_required
def create_news_article(current_user):
    json_data = request.get_json()
    try:
        data = news_article_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_article = NewsArticle(
        title=data['title'],
        content=data['content'],
        source=data.get('source'),
        read_more_link=data.get('read_more_link'),
        author_id=current_user.id
    )
    db.session.add(new_article)
    
    # Log the action
    log = AdminLog(admin_id=current_user.id, action=f"Created news article: {data['title']}")
    db.session.add(log)
    db.session.commit()
    
    return jsonify(news_article_schema.dump(new_article)), 201

@api.route('/admin/news/<int:id>', methods=['PUT'])
@admin_required
def update_news_article(current_user, id):
    article = NewsArticle.query.get_or_404(id)
    json_data = request.get_json()
    
    try:
        data = news_article_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    article.title = data.get('title', article.title)
    article.content = data.get('content', article.content)
    article.source = data.get('source', article.source)
    article.read_more_link = data.get('read_more_link', article.read_more_link)
    
    # Log the action
    log = AdminLog(admin_id=current_user.id, action=f"Updated news article ID {id}: {article.title}")
    db.session.add(log)
    db.session.commit()
    
    return jsonify(news_article_schema.dump(article)), 200

@api.route('/admin/news/<int:id>', methods=['DELETE'])
@admin_required
def delete_news_article(current_user, id):
    article = NewsArticle.query.get_or_404(id)
    article_title = article.title
    
    db.session.delete(article)
    
    # Log the action
    log = AdminLog(admin_id=current_user.id, action=f"Deleted news article ID {id}: {article_title}")
    db.session.add(log)
    db.session.commit()
    
    return jsonify({"message": f"News article '{article_title}' has been deleted"}), 200

# Admin - User Management
@api.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    users = User.query.all()
    return jsonify(users_schema.dump(users)), 200

# Admin - Report Management
@api.route('/admin/reports/verify/<int:id>', methods=['PUT'])
@admin_required
def verify_report(current_user, id):
    report = Report.query.get_or_404(id)
    report.status = "Verified"
    log = AdminLog(admin_id=current_user.id, action=f"Verified report ID {id}: {report.title}")
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": f"Report {id} has been verified"}), 200

@api.route('/admin/reports/reject/<int:id>', methods=['PUT'])
@admin_required
def reject_report(current_user, id):
    report = Report.query.get_or_404(id)
    report.status = "Rejected"
    log = AdminLog(admin_id=current_user.id, action=f"Rejected report ID {id}: {report.title}")
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": f"Report {id} has been rejected"}), 200