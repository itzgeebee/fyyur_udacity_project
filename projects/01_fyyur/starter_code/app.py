# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy import Table
from forms import ShowForm, VenueForm, ArtistForm

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


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show = db.relationship("Shows", back_populates="venue")

    def __repr__(self):
        return f"<venue ID: {self.id}, name: {self.name}"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show = db.relationship("Shows", back_populates="artiste")

    def __repr__(self):
        return f"<artiste ID: {self.id}, date: {self.name}"


class Shows(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    artiste_id = db.Column(db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    artiste = db.relationship("Artist", back_populates="show")
    venue = db.relationship("Venue", back_populates="show")

    def __repr__(self):
        return f"<artiste ID: {self.id}, task: {self.start_time}"


# TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):

    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
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
    artistes = Artist.query.order_by(Artist.id.desc()).limit(10)
    venues = Venue.query.order_by(Venue.id.desc()).limit(10)


    return render_template('pages/home.html', recent_artistes=artistes,
                           recent_venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    venue_state_city = set(db.session.query(Venue.city, Venue.state).group_by(Venue.id, Venue.city, Venue.state).all())

    for state_city in venue_state_city:

        venue_by_city = Venue.query.filter(Venue.city == state_city[0], Venue.state== state_city[1]).all()
        ven_city = len(venue_by_city)
        venues_list = []
        for i in range(ven_city):
            num_upcoming_shows = Shows.query.filter(Shows.venue_id == venue_by_city[i].id,
                                                    Shows.start_time > datetime.today()).count()
            venues_dict = {
                "id" : venue_by_city[i].id,
                "name" : venue_by_city[i].name,
                "num_upcoming_shows": num_upcoming_shows
            }
            venues_list.append(venues_dict)

        data.append(
            {
                "city": state_city[0],
                "state": state_city[1],
                "venues": venues_list
            }
        )

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%") |
                                 Venue.city.ilike(f"%{search_term}%") |
                                 Venue.state.ilike(f"%{search_term}%")).all()
    data = []
    for result in results:
        upcoming_shows = Shows.query.filter(Shows.venue == result, Shows.start_time >
                                            datetime.today()).count()
        data_dict = {
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": upcoming_shows
        }
        data.append(data_dict)

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows = Shows.query.filter(Shows.venue_id==venue.id, Shows.start_time < datetime.today()).all()
    past_show_list = []
    for i in past_shows:
        artiste = Artist.query.get(i.artiste_id)
        show_dict = {
            "artist_id": i.artiste_id,
            "artist_name": artiste.name,
            "artist_image_link": artiste.image_link,
            "start_time": i.start_time
        }
        past_show_list.append(show_dict)

    upcoming_shows = Shows.query.filter(Shows.venue_id == venue.id, Shows.start_time > datetime.today()).all()
    upcoming_show_list = []
    for i in upcoming_shows:
        artiste = Artist.query.get(i.artiste_id)
        upcoming_show_dict = {
            "artist_id": i.artiste_id,
            "artist_name": artiste.name,
            "artist_image_link": artiste.image_link,
            "start_time": i.start_time
        }
        upcoming_show_list.append(upcoming_show_dict)

    data = {
        "id" : venue.id,
        "name": venue.name,
        "genres": venue.genres.replace("{", "").replace("}", "").split(","),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_show_list,
        "upcoming_shows": upcoming_show_list,
        "past_shows_count": len(past_show_list),
        "upcoming_shows_count": len(upcoming_show_list)

    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    address = request.form.get("address")
    phone = request.form.get("phone")
    image_link = request.form.get("image_link")
    genres = request.form.getlist("genres")
    facebook_link = request.form.get("facebook_link")
    if request.form.get("seeking_talent") == "y":
        seeking_talent = True
    else:
        seeking_talent = False
    seeking_description = request.form.get("seeking_description")
    website_link = request.form.get("website_link")

    new_venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        image_link=image_link,
        facebook_link=facebook_link,
        genres=genres,
        website_link=website_link,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description
    )
    try:
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success

    except Exception as e:
        print(e)
        db.session.rollback()

        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=["GET", 'DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(f"{venue.name} was not deleted")
    else:
        flash(f"{venue.name} deleted successfully")
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "")
    results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%") |
                                 Artist.city.ilike(f"%{search_term}%") |
                                 Artist.state.ilike(f"%{search_term}%")).all()
    data = []

    for result in results:
        upcoming_shows = Shows.query.filter(Shows.artiste == result, Shows.start_time <
                                            datetime.today()).count()
        data_dict = {
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": upcoming_shows
        }
        data.append(data_dict)
    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artiste = Artist.query.get(artist_id)
    past_shows = Shows.query.filter(Shows.artiste_id == artiste.id, Shows.start_time < datetime.today()).all()
    past_show_list = []
    for i in past_shows:
        venue = Venue.query.get(i.venue_id)
        show_dict = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": i.start_time
        }
        past_show_list.append(show_dict)
    upcoming_shows = Shows.query.filter(Shows.artiste_id == artiste.id, Shows.start_time > datetime.today()).all()
    upcoming_show_list = []
    for i in upcoming_shows:
        venue = Venue.query.get(i.venue_id)
        upcoming_show_dict = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": i.start_time
        }
        upcoming_show_list.append(upcoming_show_dict)

    data = {
        "id": artiste.id,
        "name": artiste.name,
        "genres": artiste.genres.replace("{", "").replace("}", "").split(","),
        "city": artiste.city,
        "state": artiste.state,
        "phone": artiste.phone,
        "website": artiste.website_link,
        "facebook_link": artiste.facebook_link,
        "seeking_venue": artiste.seeking_venue,
        "image_link": artiste.image_link,
        "past_shows": past_show_list,
        "upcoming_shows": upcoming_show_list,
        "past_shows_count": len(past_show_list),
        "upcoming_shows_count": len(upcoming_show_list)

    }

    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artiste = Artist.query.get(artist_id)

    name = artiste.name
    genres = artiste.genres
    city = artiste.city
    state= artiste.state
    phone = artiste.phone
    website_link = artiste.website_link
    facebook_link = artiste.facebook_link
    image_link = artiste.image_link
    seeking_description = artiste.seeking_description
    seeking_venue = artiste.seeking_venue

    form.name.data = name
    form.genres.data = genres
    form.city.data = city
    form.state.data = state
    form.phone.data = phone
    form.website_link.data = website_link
    form.facebook_link.data = facebook_link
    form.image_link.data = image_link
    form.seeking_description.data = seeking_description
    form.seeking_venue.data = seeking_venue

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artiste)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artiste = Artist.query.get(artist_id)
    artiste.name = request.form.get("name")
    artiste.city = request.form.get("city")
    artiste.state = request.form.get("state")
    artiste.phone = request.form.get("phone")
    artiste.image_link = request.form.get("image_link")
    artiste.facebook_link = request.form.get("facebook_link")
    artiste.genres = request.form.get("genres")
    artiste.website_link = request.form.get("website_link")
    if request.form.get("seeking_venue") == "y":
        artiste.seeking_venue = True
    else:
        artiste.seeking_venue = False
    artiste.seeking_description = request.form.get("seeking_description")

    try:
        db.session.commit()

    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Unable to edit artiste")
    else:
        flash("Edited successfully")
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    name = venue.name
    genres = venue.genres
    city = venue.city
    state = venue.state
    phone = venue.phone
    website_link = venue.website_link
    facebook_link = venue.facebook_link
    image_link = venue.image_link
    seeking_description = venue.seeking_description
    seeking_talent = venue.seeking_talent
    address = venue.address

    form.name.data = name
    form.genres.data = genres
    form.city.data = city
    form.state.data = state
    form.phone.data = phone
    form.website_link.data = website_link
    form.facebook_link.data = facebook_link
    form.image_link.data = image_link
    form.seeking_description.data = seeking_description
    form.seeking_talent.data = seeking_talent
    form.address.data = address

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get("name")
    venue.city = request.form.get("city")
    venue.state = request.form.get("state")
    venue.address = request.form.get("address")
    venue.phone = request.form.get("phone")
    venue.image_link = request.form.get("image_link")
    venue.facebook_link = request.form.get("facebook_link")
    venue.genres = request.form.get("genres")
    venue.website_link = request.form.get("website_link")
    if request.form.get("seeking_talent") == "y":
        venue.seeking_talent = True
    else:
        venue.seeking_talent = False
    venue.seeking_description = request.form.get("seeking_description")

    try:
        db.session.commit()

    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Unable to edit venue")
    else:
        flash("Edited successfully")
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    phone = request.form.get("phone")
    image_link = request.form.get("image_link")
    genres = request.form.getlist("genres")
    facebook_link = request.form.get("facebook_link")
    if request.form.get("seeking_venue") == "y":
        seeking_venue = True
    else:
        seeking_venue = False
    seeking_description = request.form.get("seeking_description")
    website_link = request.form.get("website_link")

    new_artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        image_link=image_link,
        facebook_link=facebook_link,
        genres=genres,
        website_link=website_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description
    )
    try:
        db.session.add(new_artist)
        db.session.commit()

    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    all_shows = Shows.query.filter(Shows.start_time > datetime.today()).all()
    for show in all_shows:
        artist = Artist.query.get(show.artiste_id)
        venue = Venue.query.get(show.venue_id)
        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artiste_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
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
    # TODO: insert form data as a new Show record in the db, instead

    artiste_id = request.form.get("artist_id")
    venue_id = request.form.get("venue_id")
    start_time = request.form.get("start_time")
    try:
        new_show = Shows(
            artiste_id=artiste_id,
            venue_id=venue_id,
            start_time=start_time
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success

    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
        flash('Show was successfully listed!')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
