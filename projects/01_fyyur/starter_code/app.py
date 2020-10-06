#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func
from sqlalchemy.sql.expression import case
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
# csrf = CSRFProtect(app)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    show = db.relationship('Show', backref='venue')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    show = db.relationship('Show', backref='artist')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
  start_time = db.Column(db.DateTime, nullable=False)

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  city_states = Venue.query.distinct('city', 'state').all()
  for city_state in city_states:
    venues = db.session.query(Venue.id, Venue.name,
                              func.sum(case([(Show.start_time > datetime.now(), 1)], else_=0)).label('num_upcoming_shows'))\
                                .outerjoin(Show).group_by(Venue.id, Venue.name).filter(Venue.city==city_state.city, Venue.state==city_state.state).all()
                                
    data.append({
      "city": city_state.city,
      "state": city_state.state,
      "venues": venues
    })
  return render_template('pages/venues.html', areas=data)

@ app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  search_result = Venue.query.filter(
      Venue.name.ilike('%{}%'.format(search_term)))
  response={
    "count": search_result.count(),
    "data": search_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
  past_shows_query = Show.query.filter(Show.venue_id == venue_id).filter(
      Show.start_time <= datetime.now())
  past_shows = past_shows_query.all()
  past_shows_count = past_shows_query.count()
  upcoming_shows_query = Show.query.filter(
      Show.venue_id == venue_id).filter(Show.start_time > datetime.now())
  upcoming_shows = upcoming_shows_query.all()
  upcoming_shows_count = upcoming_shows_query.count()
  print(past_shows)
  print(past_shows_count)
  return render_template('pages/show_venue.html', venue=data, past_shows=past_shows, past_shows_count=past_shows_count,
    upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    form = VenueForm()
    new_venue = Venue() 
    form.populate_obj(new_venue)
    db.session.add(new_venue)
    db.session.commit()

  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
        venue_to_delete = Venue.query.get(venue_id)
        if venue_to_delete:        
          db.session.delete(venue_to_delete)
          db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@ app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@ app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term)))
  response = {
    'count': artists.count(),
    'data': artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Artist.query.get(artist_id)
  past_shows_query = Show.query.filter(Show.artist_id == artist_id).filter(\
      Show.start_time <= datetime.now())
  past_shows = past_shows_query.all()
  past_shows_count = past_shows_query.count()
  upcoming_shows_query = Show.query.filter(
      Show.artist_id == artist_id).filter(Show.start_time > datetime.now())
  upcoming_shows = upcoming_shows_query.all()
  upcoming_shows_count = upcoming_shows_query.count()
  return render_template('pages/show_artist.html', artist=data, past_shows=past_shows,\
     past_shows_count=past_shows_count, upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count)


#  Update
#  ----------------------------------------------------------------
@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(
    name = artist.name, 
    genres = artist.genres,
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    website = artist.website,
    facebook_link = artist.facebook_link,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description,
    image_link = artist.image_link
  )
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    form.populate_obj(artist)
    db.session.commit()  
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form= VenueForm(
    name = venue.name,
    genres = venue.genres,
    address = venue.address,
    city = venue.city,
    state = venue.state,
    phone = venue.phone,
    website = venue.website,
    facebook_link = venue.facebook_link,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description,
    image_link = venue.image_link
  )
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    form= VenueForm()
    form.populate_obj(venue)
    db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form= ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist()
    form = ArtistForm()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all() 
  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'start_time': str(show.start_time),
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link
    })
  
  return render_template('pages/shows.html', shows=data)

@ app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form= ShowForm()
  return render_template('forms/new_show.html', form=form)

@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()
    new_show = Show()
    form.populate_obj(new_show)
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler= FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
