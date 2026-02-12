import json
from pathlib import Path

from app import app, db, User, Question, Stat, Ticket

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'


def read_json(filename, default):
    path = DATA_DIR / filename
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def migrate_users():
    users = read_json('users.json', [])
    inserted = 0
    for data in users:
        username = data.get('username')
        if not username:
            continue
        user = User.query.filter_by(username=username).first()
        if user:
            continue
        user = User(
            username=username,
            email=data.get('email', ''),
            password=data.get('password', ''),
            active=bool(data.get('active', False)),
            role=data.get('role', 'user'),
            progress=data.get('progress', {'completed_questions': [], 'by_category': {}}),
            avatar_url=data.get('avatar_url')
        )
        db.session.add(user)
        inserted += 1
    return inserted


def migrate_questions():
    questions = read_json('questions.json', [])
    inserted = 0
    for data in questions:
        qid = data.get('id')
        if not qid:
            continue
        exists = Question.query.get(qid)
        if exists:
            continue
        question = Question(
            id=qid,
            category=data.get('category', ''),
            question=data.get('question', ''),
            options=data.get('options', []),
            answer=data.get('answer', '')
        )
        db.session.add(question)
        inserted += 1
    return inserted


def migrate_stats():
    stats = read_json('stats.json', {})
    inserted = 0
    for question_id, values in stats.items():
        exists = Stat.query.get(question_id)
        if exists:
            continue
        row = Stat(
            question_id=question_id,
            correct=int(values.get('correct', 0)),
            wrong=int(values.get('wrong', 0))
        )
        db.session.add(row)
        inserted += 1
    return inserted


def migrate_tickets():
    tickets = read_json('tickets.json', [])
    inserted = 0
    for data in tickets:
        ticket_id = data.get('id')
        if not ticket_id:
            continue
        exists = Ticket.query.get(ticket_id)
        if exists:
            continue
        ticket = Ticket(
            id=ticket_id,
            email=data.get('email', '').lower(),
            plan=data.get('plan', 'pro'),
            amount=int(data.get('amount', 0)),
            payment_method=data.get('payment_method', 'manual'),
            status=data.get('status', 'pending'),
            created_at=data.get('created_at', ''),
            paid_at=data.get('paid_at')
        )
        db.session.add(ticket)
        inserted += 1
    return inserted


def main():
    with app.app_context():
        db.create_all()

        users_count = migrate_users()
        questions_count = migrate_questions()
        stats_count = migrate_stats()
        tickets_count = migrate_tickets()

        db.session.commit()

        print(f'Users inserted: {users_count}')
        print(f'Questions inserted: {questions_count}')
        print(f'Stats inserted: {stats_count}')
        print(f'Tickets inserted: {tickets_count}')
        print('Migración completada (idempotente, sin duplicados).')


if __name__ == '__main__':
    main()
