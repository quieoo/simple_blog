import os
from docx import Document
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import BlogPost
from datetime import datetime
from flask import send_from_directory


bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(docx_path, upload_folder):
    doc = Document(docx_path)
    html_content = ""
    image_index = 0

    for para in doc.paragraphs:
        if para.text.strip():
            html_content += f"<p>{para.text}</p>"
        else:
            html_content += "<p><br></p>"

    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_index += 1
            image_extension = os.path.splitext(rel.target_part.partname)[1]
            image_filename = f"image{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{image_index}{image_extension}"
            image_path = os.path.join(upload_folder, image_filename)
            with open(image_path, "wb") as f:
                f.write(rel.target_part.blob)
            html_content += f'<p><img src="/uploads/{image_filename}" alt="Image"></p>'

    return html_content

@bp.route('/')
def index():
    posts = BlogPost.query.order_by(BlogPost.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        keywords = request.form['keywords']
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
            content = extract_text_from_docx(file_path, current_app.config['UPLOAD_FOLDER'])
            post = BlogPost(title=title, content=content, keywords=keywords)
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
        results = BlogPost.query.filter(
            (BlogPost.content.contains(keyword)) |
            (BlogPost.keywords.contains(keyword))
        ).all()
    return render_template('search.html', results=results)

@bp.route('/post/<int:post_id>')
def detail(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('detail.html', post=post)

@bp.route('/keywords')
def keywords():
    posts = BlogPost.query.all()
    keywords = set()
    for post in posts:
        if post.keywords:
            keywords.update(post.keywords.split(','))
    return render_template('keywords.html', keywords=keywords)

@bp.route('/keyword/<keyword>')
def keyword_posts(keyword):
    posts = BlogPost.query.filter(BlogPost.keywords.contains(keyword)).all()
    return render_template('keyword_posts.html', keyword=keyword, posts=posts)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)