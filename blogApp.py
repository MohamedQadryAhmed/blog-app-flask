from datetime import datetime
from flask import Flask , render_template , url_for , request , redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
db = SQLAlchemy(app)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# db.__init__(app)
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    image = db.Column(db.String)
    body = db.Column(db.Text)
    craeted_at = db.Column(db.DateTime , default=datetime.utcnow)
    updated_at = db.Column(db.DateTime , default=datetime.utcnow , onupdate=datetime.utcnow)

    @property
    def get_image_url(self):
        return url_for('static', filename=f'posts/images/{self.image}')

    @property
    def get_show_url(self):
        return  url_for('post.show', id=self.id)
    
    @property
    def get_edit_url(self):
        return  url_for('post.edit', id= self.id)

    @property
    def get_delete_url(self):
        return  url_for('post.delete', id= self.id)

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    body = StringField('Content', validators=[DataRequired()])
    image = StringField("Image")
    submit = SubmitField("Submit")

@app.route('/')
@app.route('/home', endpoint='blog.home')
def home():
    posts = Blog.query.all()
    return render_template('home.html' , posts=posts)

@app.route('/home/<int:id>', endpoint='post.show')
def get_post(id):
    post= Blog.query.get_or_404(id)
    if post:
        return  render_template('show.html', post=post)
    else:
        return  '<h1> Object not found </h1>', 404
    

@app.route('/home/create', methods=['GET', 'POST'], endpoint='post.create')
def create():
    if request.method == 'POST':

        # print("request received", request.form)
        post = Blog(title=request.form['title'], body=request.form['body'],
                          image=request.form['img'])
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('blog.home'))

    return render_template('create.html')

@app.route('/home/edit/<int:id>', methods=['GET', 'POST'], endpoint='post.edit')
def edit_post(id):
    post = Blog.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.image = form.image.data
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post.show', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.image.data = post.image
    return render_template('edit.html', form=form)
    return 'edit'
def delete_post(id):
    post= Blog.query.get_or_404(id)
    if post:
       db.session.delete(post)
       db.session.commit()
       return redirect(url_for('blog.home'))
    else:
        return  '<h1> Object not found </h1>', 404

app.add_url_rule('/home/<int:id>/delete',
                 view_func=delete_post,
                 endpoint='post.delete', methods=['GET'])


if __name__ == '__main__':
    app.run(debug=True)