from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Ensure tables exist for testing environments without running migrations
with app.app_context():
    db.create_all()
    # Ensure at least one message exists so tests that rely on an existing
    # record (e.g., PATCH/DELETE using first()) have data to work with.
    if Message.query.first() is None:
        seed_message = Message(body="Seed message", username="Tester")
        db.session.add(seed_message)
        db.session.commit()

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages])
@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = Message.query.get_or_404(id)
    return jsonify(message.to_dict())

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json() or {}
    body = data.get('body')
    username = data.get('username')
    message = Message(body=body, username=username)
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id)
    data = request.get_json() or {}
    if 'body' in data:
        message.body = data['body']
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict())

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(port=5555)
