from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models import Task
from datetime import datetime
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'task.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key-for-flash-messages'

db.init_app(app)


@app.route('/')
def index():
    task_filter = request.args.get('filter', 'all')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort_by', 'deadline')
    sort_order = request.args.get('sort_order', 'asc')

    query = Task.query

    if task_filter == 'completed':
        query = query.filter_by(completed=True)
    elif task_filter == 'pending':
        query = query.filter_by(completed=False)

    if search_query:
        query = query.filter(Task.content.ilike(f'%{search_query}%'))

    sort_column = getattr(Task, sort_by, Task.deadline)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    tasks = query.all()

    return render_template('index.html',
                           tasks=tasks,
                           current_filter=task_filter,
                           search_query=search_query,
                           sort_by=sort_by,
                           sort_order=sort_order)


@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form['content']
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    priority = request.form.get('priority', 'medium')
    category = request.form.get('category')
    deadline = None

    if date_str and time_str:
        try:
            deadline_str = f"{date_str} {time_str}"
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Неверный формат даты или времени.', 'danger')
            pass

    if not task_content:
        flash('Текст задачи не может быть пустым.', 'danger')
        return redirect(url_for('index'))

    new_task = Task(content=task_content, deadline=deadline, priority=priority, category=category)

    db.session.add(new_task)
    db.session.commit()

    flash('Задача успешно добавлена!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена.', 'info')
    return redirect(url_for('index'))


@app.route('/complete/<int:id>')
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()

    status = "завершена" if task.completed else "возвращена в работу"
    flash(f'Задача "{task.content[:20]}..." {status}.', 'success')

    return redirect(request.referrer or url_for('index'))


@app.route('/api/update_content/<int:id>', methods=['POST'])
def api_update_content(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'status': 'error', 'message': 'Отсутствуют данные'}), 400

    new_content = data['content'].strip()
    if not new_content:
        return jsonify({'status': 'error', 'message': 'Текст задачи не может быть пустым'}), 400

    task.content = new_content
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Задача обновлена', 'new_content': task.content})


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.priority = request.form.get('priority', 'medium')
        task.category = request.form.get('category')

        date_str = request.form.get('date')
        time_str = request.form.get('time')

        if date_str and time_str:
            try:
                deadline_str = f"{date_str} {time_str}"
                task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
            except ValueError:
                task.deadline = None
                flash('Неверный формат даты, дедлайн сброшен.', 'warning')
        else:
            task.deadline = None

        db.session.commit()
        flash('Задача успешно обновлена!', 'success')
        return redirect(url_for('index'))

    return render_template('update.html', task=task)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)