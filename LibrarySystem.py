from flask import Flask, render_template, request, flash, redirect, url_for
from wtforms import Form, StringField, TextAreaField, RadioField, SelectField , validators
from Magazine import Magazine
from Book import Book

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('cred/library-system-e7731-firebase-adminsdk-ptzxe-060b68b116.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':'https://library-system-e7731.firebaseio.com/'
})

root = db.reference()

app = Flask(__name__)


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/viewpublications')
def viewpublications():
    return render_template('view_all_publications.html')








class RequiredIf(object):

    def __init__(self, *args, **kwargs):
        self.conditions = kwargs

    def __call__(self, form, field):
        for name, data in self.conditions.items():
            if name not in form._fields:
                validators.Optional()(field)
            else:
                condition_field = form._fields.get(name)
                if condition_field.data == data:
                    validators.DataRequired().__call__(form, field)
                else:
                    validators.Optional().__call__(form, field)


class PublicationForm(Form):
    title = StringField('Title', [
        validators.Length(min=1, max=150),
        validators.DataRequired()])
    pubtype = RadioField('Type Of Publication', choices=[('sbook', 'Book'), ('smag', 'Magazine')], default='sbook')
    category = SelectField('Caterory', [validators.DataRequired()],
                           choices=[('', 'Select'), ('FANTASY', 'Fantasy'), ('FASHION', 'Fashion'),
                                    ('THRILLER', 'Thriller'), ('CRIME', 'Crime'), ('BUSINESS', 'Business')],
                           default='')
    publisher = StringField('Publisher', [
        validators.Length(min=1, max=100),
        validators.DataRequired()])
    status = SelectField('Status', [validators.DataRequired()],
                         choices=[('', 'Select'), ('P', 'Pending'), ('A', 'Available For Borrowing'),
                                  ('R', 'Only For Reference')], default='')
    isbn = StringField('ISBN No', [
        validators.Length(min=1, max=100),
        RequiredIf(pubtype='sbook')])
    author = StringField('Author', [
        validators.Length(min=1, max=100),
        RequiredIf(pubtype='sbook')])
    synopsis = TextAreaField('Synopsis', [
        RequiredIf(pubtype='sbook')])
    frequency = RadioField('Frequency', [RequiredIf(pubtype='smag')],
                           choices=[('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')])

















@app.route('/newpublication', methods=['GET', 'POST'])
def new():
    form = PublicationForm(request.form)
    if request.method == 'POST' and form.validate():
        if  form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001" # hardcoded value

            mag = Magazine(title, publisher, status, created_by, category, type, frequency)

            mag_db = root.child('publications')
            mag_db.push({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Inserted Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value

            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn)
            book_db = root.child('publications')
            book_db.push({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date()
            })

            flash('Book Inserted Sucessfully.', 'success')

        return redirect(url_for('viewpublications'))


    return render_template('create_publication.html', form=form)





@app.route('/update')
def update_publication():
    # Setting values to the update_publication.html
    form = PublicationForm(request.form)
    form.title.data = 'Harry Potter and The Half Blood Prince'
    form.pubtype.data = 'sbook'
    form.category.data = 'FANTASY'
    form.publisher.data = 'Bloomsbury'
    form.status.data = 'A'
    form.isbn.data = '0-7475-8108-8'
    form.author.data = 'J. K. Rowling'
    form.synopsis.data = 'Severus Snape, a member of the Order of the Phoenix, meets with Narcissa Malfoy, Draco''s mother, and Lord Voldemort''s faithful supporter Bellatrix Lestrange. Narcissa expresses concern that her son might not survive a dangerous mission given to him by Lord Voldemort. Bellatrix feels Snape will be of no help until he surprises her by making an Unbreakable Vow with Narcissa, swearing on his life that he will protect and assist Draco in his mission.'
    return render_template('update_publication.html', form=form)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()
