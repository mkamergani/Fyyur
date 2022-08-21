# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_venues = Venue.query.all()
    cities_and_states = []
    for venue in all_venues:
        cities_and_states.append((venue.city, venue.state))

    data = []
    for unique_value in list(set(cities_and_states)):
        unique_value_venues = []
        for venue in all_venues:
            upcoming_shows = 0
            for show in venue.shows:
                if show.start_time > datetime.now():
                    upcoming_shows += 1
            if venue.city == unique_value[0] and venue.state == unique_value[1]:
                unique_value_venues.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming_shows
                })
        data.append({
            "city": unique_value[0],
            "state": unique_value[1],
            "venues": unique_value_venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    filtered_venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(filtered_venues),
        "data": filtered_venues
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    venue_data = {
        'id': venue.id,
        'name': venue.name,
        'state': venue.state,
        'city': venue.city,
        'address': venue.address,
        'phone': venue.phone,
        'genres': venue.genres,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
    }
    venue_data['genres'] = venue_data['genres'].split()
    upcoming_shows = []
    past_shows = []
    for show in venue.shows:
        if show.start_time > datetime.now():
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
        else:
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
    venue_data['past_shows_count'] = len(past_shows)
    venue_data['upcoming_shows_count'] = len(upcoming_shows)
    venue_data['upcoming_shows'] = upcoming_shows
    venue_data['past_shows'] = past_shows
    return render_template('pages/show_venue.html', venue=venue_data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website_link')
        seeking_talent = request.form.get('seeking_talent')
        seeking_description = request.form.get('seeking_description')
        new_venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_talent=True if seeking_talent == 'y' else False,
            seeking_description=seeking_description
        )
        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue could not be Created.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists_data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=artists_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    filtered_artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(filtered_artists),
        "data": filtered_artists
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    artist_data = {
        'id': artist.id,
        'name': artist.name,
        'state': artist.state,
        'city': artist.city,
        'phone': artist.phone,
        'genres': artist.genres,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
    }
    artist_data['genres'] = artist_data['genres'].split()
    upcoming_shows = []
    past_shows = []
    for show in artist.shows:
        if show.start_time > datetime.now():
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            })
        else:
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            })
    artist_data['past_shows_count'] = len(past_shows)
    artist_data['upcoming_shows_count'] = len(upcoming_shows)
    artist_data['upcoming_shows'] = upcoming_shows
    artist_data['past_shows'] = past_shows
    return render_template('pages/show_artist.html', artist=artist_data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
    artist.seeking_description = request.form.get('seeking_description')
    db.session.add(artist)
    db.session.commit()
    try:
        print('try')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.get('genres')
        venue.image_link = request.form.get('image_link')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website = request.form.get('website_link')
        venue.seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
        venue.seeking_description = request.form.get('seeking_description')
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website_link')
        seeking_venue = request.form.get('seeking_venue')
        seeking_description = request.form.get('seeking_description')
        new_artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_venue=True if seeking_venue == 'y' else False,
            seeking_description=seeking_description
        )
        db.session.add(new_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist could not be Created.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows_data = Show.query.all()
    data = []
    for show in shows_data:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            }
        )
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = dateutil.parser.parse(request.form.get('start_time'))
        new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
