import os
import click
from app import create_app, db
from app.models import User

# Get the configuration name from the environment variable or use default
config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)

@app.cli.command("create-admin")
@click.argument("email")
def create_admin(email):
    """Promotes a user to an admin."""
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"User {user.username} ({email}) has been promoted to an admin.")
    else:
        print(f"User with email {email} not found.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)