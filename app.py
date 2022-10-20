#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ast import keyword
from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database (Done)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(525), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=True, default=False)
    seeking_description = db.Column(db.String(525))

    # -- Relationship between tables
    artists = db.relationship('Artist', secondary='Show')
    shows = db.relationship('Show', backref='Venue', lazy=True, cascade='all, delete-orphan', overlaps='artists')

    # This is implemented to return a dictionary of venues
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genre': self.genre.split(','),
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
        }

    def __repr__(self):
        return f'<Venue id={self.id} name={self.name} city={self.city} state={self.city}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Done)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(525))

    # -- Relationship between tables
    venues = db.relationship('Venue', secondary='Show', overlaps='Venue,artists,shows')
    shows = db.relationship('Show', backref='Artist', lazy=True, cascade='all, delete-orphan', overlaps='artists,venues')

    # This is implemented to return a dictionary of artists
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres.split(','), 
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
        }

    def __repr__(self):
        return f'<Artist id={self.id} name={self.name} city={self.city} state={self.city}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Done)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue = db.relationship('Venue', overlaps='Venue,artists,shows,venues')
    artist = db.relationship('Artist', overlaps='Artist,artists,shows,venues')

    # This is implemented to return a dictionary of artists for a show
    def show_artist(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': self.start_time.strftime('%D-%M-%Y %H:%M:%S')
        }

    #  This is implemented to return a dictionary of venues for a show
    def show_venue(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'start_time': self.start_time.strftime('%D-%M-%Y %H:%M:%S')
        }

    def __repr__(self):
        return f'<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. (Done)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.(Done)
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.(Done)
    data = []
    results = Venue.query.distinct(Venue.city, Venue.state).all()
    for result in results:
        tmp = {
            'city': result.city,
            'state': result.state
        }
        venues = Venue.query.filter_by(city=result.city, state=result.state).all()

        venue_data = []
        for venue in venues:
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
            })
        
        tmp['venues'] = venue_data
        data.append(tmp)
    return render_template('pages/venues.html', areas=data);


# ------ Search Venue -------- #
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" (All Done)
    keyword = request.form.get('search_term')
    venues = db.session.query(Venue).with_entities(Venue.id, Venue.name).filter(Venue.name.ilike('%' + keyword + '%')).all()
    
    response = {}
    response['count'] = len(venues)
    response['data'] = []

    for venue in venues:
        venue_result = {
            'id': venue.id,
            'name': venue.name,
        }
        response['data'].append(venue_result)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id (Done)
  # TODO: replace with real venue data from the venues table, using venue_id (Done)

    venue = Venue.query.get(venue_id)

    prev_shows = list(filter(lambda show: show.start_time < datetime.now(), venue.shows))
    upcoming_shows = list(filter(lambda show: show.start_time >= datetime.now(), venue.shows))
    prev_shows = list(map(lambda show: show.show_artist(), prev_shows))
    upcoming_shows = list(map(lambda show: show.show_artist(), upcoming_shows))
    
    tmp = venue.to_dict()
    # Display previous shows
    tmp['past_shows'] = prev_shows
    tmp['past_shows_count'] = len(prev_shows)

    # Display up-coming shows
    tmp['upcoming_shows'] = upcoming_shows
    tmp['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=tmp)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead (Done)
  # TODO: modify data to be the data object returned from db insertion (Done)
    form = VenueForm(request.form)
    error = False
    try:
      new_venue = Venue()
      new_venue.name = request.form['name']
      new_venue.city = request.form['city']
      new_venue.state = request.form['state']
      new_venue.address = request.form['address']
      new_venue.phone = request.form['phone']
      get_genres = request.form.getlist('genre')
      new_venue.genre = ','.join(get_genres) #convert array to string and separate them by commas
      new_venue.image_link = request.form['image_link']
      new_venue.facebook_link = request.form['facebook_link']
      new_venue.website_link = request.form['website_link']
      new_venue.seeking_description = request.form['seeking_description']
      new_venue.seeking_talent = form.seeking_talent.data
      db.session.add(new_venue)
      db.session.commit()
      db.session.refresh(new_venue)
      flash('New venue ' + request.form['name'] + '  successfully listed!') # on successful db insert, flash success (Done)
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue ' + request.form['name'] + '  was not listed successfully.') # TODO: on unsuccessful db insert, flash an error instead. (Done)
    finally:
      db.session.close()
    return render_template('pages/home.html')

# ------ Delete Venue ------- #

@app.route('/venues/<int:venue_id>/delete', methods=['GET', 'POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. (Done)
    try:
        get_venue = Venue.query.get(venue_id)
        db.session.delete(get_venue)
        db.session.commit()
        flash('Venue'  + get_venue.name + ' was deleted successfully!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue was not deleted successfully.')
    finally:
        db.session.close()
    return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage. (Done)



#  Artists
#  ----------------------------------------------------------------

# ------ Create Artist ------ #

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion (Done)
    form = ArtistForm(request.form)
    error = False
    try:
      new_artist = Artist()
      new_artist.name = request.form['name']
      new_artist.city = request.form['city']
      new_artist.state = request.form['state']
      new_artist.phone = request.form['phone']
      get_genres = request.form.getlist('genres')
      new_artist.genres = ','.join(get_genres)
      new_artist.website_link = request.form['website_link']
      new_artist.image_link = request.form['image_link']
      new_artist.facebook_link = request.form['facebook_link']
      new_artist.seeking_description = request.form['seeking_description']
      new_artist.seeking_venue = form.seeking_venue.data
      db.session.add(new_artist)
      db.session.commit()
      db.session.refresh(new_artist)
      flash('Artist ' + request.form['name'] + ' was successfully listed!') # on successful db insert, flash success (Done)
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('Unsuccessful. The artist ' + request.form.get('name') + ' wasn\'t listed. Please try again or contact the webmaster at webmaster@fyyur.com')
    finally:
      db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.(Done)
    return render_template('pages/home.html')

# ------ Get Artists -------- #
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database (Done)
    artists = Artist.query.order_by(Artist.name).all()  # Sort results alphabetically

    data = []
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })
    return render_template('pages/artists.html', artists=data)

# ------ Search Artist -------- #
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band". (Done)
    keyword = request.form.get('search_term')
    artists = db.session.query(Artist).with_entities(Artist.id, Artist.name).filter(Artist.name.ilike('%' + keyword + '%')).all()
    
    response = {}
    response['count'] = len(artists)
    response['data'] = []

    for artist in artists:
        artist_srch = {
            'id': artist.id,
            'name': artist.name,
        }
        response['data'].append(artist_srch)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id (Done)
    artist = Artist.query.get(artist_id)
    prev_shows = list(filter(lambda show: show.start_time < datetime.now(), artist.shows))
    upcoming_shows = list(filter(lambda show: show.start_time >= datetime.now(), artist.shows))
    prev_shows = list(map(lambda show: show.show_venue(), prev_shows))
    upcoming_shows = list(map(lambda show: show.show_venue(), upcoming_shows))
    
    tmp = artist.to_dict()
    # Display previous shows
    tmp['past_shows'] = prev_shows
    tmp['past_shows_count'] = len(prev_shows)

    # Display up-coming shows
    tmp['upcoming_shows'] = upcoming_shows
    tmp['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=tmp)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id> (Done)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes (Done)
    form = ArtistForm(request.form)
    error = False
    try:
        update_artist = Artist.query.get(artist_id)
        update_artist.name = request.form['name']
        update_artist.city = request.form['city']
        update_artist.state = request.form['state']
        update_artist.phone = request.form['phone']
        get_genres = request.form.getlist('genres')
        update_artist.genres = ','.join(get_genres)
        update_artist.website_link = request.form['website_link']
        update_artist.image_link = request.form['image_link']
        update_artist.facebook_link = request.form['facebook_link']
        update_artist.seeking_description = request.form['seeking_description']
        update_artist.seeking_venue = form.seeking_venue.data
        db.session.add(update_artist)
        db.session.commit()
        db.session.refresh(update_artist)
        flash('Update successful!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('Update unsuccessful. The artist ' + request.form.get('name') + ' wasn\'t updated. Please try again or contact the webmaster at webmaster@fyyur.com')
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>(Done)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes(Done)
    form = VenueForm(request.form)
    update_venue = Venue.query.get(venue_id)

    error = False
    try:
        update_venue.name = request.form['name']
        update_venue.city = request.form['city']
        update_venue.state = request.form['state']
        update_venue.address = request.form['address']
        update_venue.phone = request.form['phone']
        get_genres = request.form.getlist('genre')
        update_venue.genre = ','.join(get_genres)  # convert list to string and separate them by commas
        update_venue.image_link = request.form['image_link']
        update_venue.facebook_link = request.form['facebook_link']
        update_venue.website_link = request.form['website_link']
        update_venue.seeking_description = request.form['seeking_description']
        update_venue.seeking_talent = form.seeking_talent.data
        db.session.add(update_venue)
        db.session.commit()
        db.session.refresh(update_venue)
        flash('Update successful!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('Update unsuccessful.  The venue ' + request.form.get('name') + ' wasn\'t updated. Please try again or contact the webmaster at webmaster@fyyur.com')
    finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

    data = []
    shows = Show.query.all()
    for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.isoformat()
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead (Done)
    error = False
    try:
        show = Show()
        show.artist_id = request.form['artist_id']
        show.venue_id = request.form['venue_id']
        show.start_time = request.form['start_time']
        db.session.add(show)
        db.session.commit()
        db.session.refresh(show)
        flash('Show was successfully listed!') # on successful db insert, flash success (Done)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('Unsuccessful. Show could not be listed.') # TODO: on unsuccessful db insert, flash an error instead.(Done)

    finally:
        db.session.close()
  
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
