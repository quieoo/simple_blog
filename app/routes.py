from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import BlogPost
import os
from docx import Document

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    html_content = ""
    for para in doc.paragraphs:
        if para.text.strip():
            html_content += f"<p>{para.text}</p>"
        else:
            html_content += "<p><br></p>"
    return html_content


@bp.route('/')
def index():
    posts = BlogPost.query.all()
    return render_template('index.html', posts=posts)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            content = extract_text_from_docx(file_path)
            post = BlogPost(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            os.remove(file_path)  # Optionally remove the file after extracting content
            return redirect(url_for('main.index'))
    return render_template('upload.html')

@bp.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        results = BlogPost.query.filter(BlogPost.content.contains(keyword)).all()
    return render_template('search.html', results=results)
