from email.contentmanager import raw_data_manager

from flask import Flask, render_template, redirect, url_for
import sqlite3
from flask import request
import uuid
from werkzeug.utils import secure_filename
import requests




app = Flask(__name__)

connection = sqlite3.connect("SQLite (1).db", check_same_thread = False)
cursor = connection.cursor()

@app.route("/")
def index():

    cursor.execute("SELECT uuid, name, avatar, skills from portfolio")
    result = cursor.fetchall()
    filter_skills = request.args.get('skill')
    if filter_skills:
        filter_skills = filter_skills.strip().lower()
    else:
        filter_skills = None
    portfolios = []
    for uuid, name, avatar, skills_str in result:
        skills = []
        for s in skills_str.split(","):
            s=s.strip()
            if s:
                skills.append(s)
        skills_lower = []
        for s in skills:

            skills_lower.append(s.lower())


        if filter_skills is None or filter_skills in skills_lower:

            portfolios.append(
                { "uuid":uuid, "name": name,  "avatar":avatar, "skills":skills, }
            )

    tool_icons = {
        "Python": "🐍", "Flask": "🌶", "HTML": "📄", "CSS": "🎨",
        "HTML/CSS": "🖌️", "Git": "🔧", "GitHub": "🐙", "Telegram": "✈️",
        "Телеграм": "✈️", "SQL": "🗄️", "SQLite": "📘", "JavaScript": "⚡",
        "JS": "⚡", "Jinja": "🧩"
    }
    context = {"portfolios": portfolios}
    return render_template("all_portfolios.html", **context, tool_icons = tool_icons,
    current_skill = filter_skills or "")

@app.route('/portfolio/<uuid>')
def portfolio(uuid):
    data = cursor.execute("SELECT * from portfolio where uuid = ? ", (uuid,)).fetchone()
    if not data:
        return "not found", 404
    print(data)
    portfolio = {"id":data[0],"uuid":data[1],"name":data[2],"github":data[4],"bio":data[3]
        ,"telegram":data[7],"skils":data[6],"avatar":data[5],}

    portfolio  ["skills"] = [skill.strip() for skill in data[6].split(",")]
    print(portfolio.get("avatar"))


    projects = []
    url = f"https://api.github.com/users/{portfolio["github"]}/repos"
    response = requests.get(url)

    if response.ok:
        project_data = response.json()

        projects = []
        for project in project_data[:6]:
            projects.append({
                "name": project.get("name"),
                "description": project.get("description"),
                "html_url": project.get("html_url"),

            })



    else:
        print("not found:", response.status_code)
    tool_icons = {
            "Python": "🐍", "Flask": "🌶", "HTML": "📄", "CSS": "🎨",
            "HTML/CSS": "🖌️", "Git": "🔧", "GitHub": "🐙", "Telegram": "✈️",
            "Телеграм": "✈️", "SQL": "🗄️", "SQLite": "📘", "JavaScript": "⚡",
            "JS": "⚡", "Jinja": "🧩"
        }
    print(projects)
    return  render_template("portfolio_template.html", projects = projects, portfolio=portfolio, tool_icons=tool_icons)
@app.route('/form')
def form():
    return render_template('form.html')



@app.route("/generate", methods=['POST'])
def generate():
    if request.method == 'POST':
        form = request.form
        uid = str(uuid.uuid4())
        name = form.get('name')
        bio = form.get('bio')
        skills = form.get('skills')
        github = form.get('github')
        telegram = form.get('telegram')
        avatar = request.files.get('avatar')
        print(avatar.filename)
        avatar_filename = ''
        if avatar and avatar.filename:
            filename = secure_filename(f"{uid}_{avatar.filename}")
            avatar_path = f"static/uploads/{filename}"
            avatar.save(avatar_path)
            # убираем "static/" — будет 'uploads/имя'
            avatar_filename = avatar_path.replace("static/", "")
        print(avatar_filename)
        github = form['github'].strip().replace('https://github.com/', '').replace('/', '')

        cursor.execute("insert into portfolio (uuid, name, bio, github, telegram, avatar, skills) values (?, ?, ?, ?, ?, ?, ?)",
                       (uid, name, bio, github, telegram,avatar_filename, skills))
        connection.commit()

        return redirect(url_for('index'))




if __name__ == '__main__':
    app.run()