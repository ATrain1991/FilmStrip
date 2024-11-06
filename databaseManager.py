from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
# from sqlalchemy.ext.declarative import declarative_base
from databaseModels import Base, Movie, Genre, Director, Actor, MovieActor

class DatabaseManager:
    def __init__(self, db_url='sqlite:///movies.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
    def add_or_update_box_office(self, movie_title, value):
        with self.get_session() as session:
            movie = session.query(Movie).filter_by(title=movie_title).first()
            if movie:
                movie.box_office = value
                session.commit()
                return movie
            else:
                return None
    def add_or_update_movie(self, **kwargs):
        with self.get_session() as session:
            return Movie.add_or_update_movie(session, **kwargs)

    def update_movie_attribute(self, movie_id=None, title=None, attribute=None, value=None):
        with self.get_session() as session:
            return Movie.update_attribute(session, movie_id, title, attribute, value)
    def add_or_update_role(self, actor_name, movie_title, role):
        with self.get_session() as session:
            actor = session.query(Actor).filter_by(name=actor_name).first()
            movie = session.query(Movie).filter_by(title=movie_title).first()
            
            if not actor or not movie:
                return None
            
            movie_actor = session.query(MovieActor).filter_by(
                movie_id=movie.id, 
                actor_id=actor.id
            ).first()
            
            if movie_actor:
                # Update existing role
                if role not in movie_actor.roles:
                    movie_actor.roles += f", {role}"
            else:
                # Create new MovieActor entry
                movie_actor = MovieActor(movie=movie, actor=actor, roles=role)
                session.add(movie_actor)
            
            session.commit()
            return movie_actor
    def update_birthdate(self, actor_name, birthdate):
        with self.get_session() as session:
            actor = session.query(Actor).filter_by(name=actor_name).first()
            if actor:
                actor.update_birthdate(birthdate)
                session.commit()
                return actor
            return None
    def update_oscars(self, actor_name, oscars_wins, oscars_nominations):
        with self.get_session() as session:
            actor = session.query(Actor).filter_by(name=actor_name).first()
            if actor:
                actor.update_oscars(oscars_wins, oscars_nominations)
                session.commit()
                return actor
            return None
    def add_or_update_genre(self, **kwargs):
        session = self.Session()
        try:
            genre = session.query(Genre).filter_by(name=kwargs.get('name')).first()
            if genre:
                # Update existing genre
                for key, value in kwargs.items():
                    setattr(genre, key, value)
            else:
                # Create new genre
                genre = Genre(**kwargs)
                session.add(genre)
            
            session.commit()
            return genre
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_or_update_director(self, **kwargs):
        with self.get_session() as session:
            return Director.add_or_update_director(session, **kwargs)

    def add_or_update_actor(self, **kwargs):
        with self.get_session() as session:
            return Actor.add_or_update_actor(session, **kwargs)
        
    def add_or_update_movie_actor(self, **kwargs):
        with self.get_session() as session:
            return MovieActor.add_or_update_movie_actor(session, **kwargs)

    def get_movie_by_id(self, movie_id):
        with self.get_session() as session:
            return session.query(Movie).filter_by(id=movie_id).first()
    def has_roles(self, actor_name):
        with self.get_session() as session:
            actor = session.query(Actor).filter_by(name=actor_name).first()
            if actor and actor.movie_roles:
                return True
            return False
    def get_movie_by_title(self, title):
        with self.get_session() as session:
            return session.query(Movie).filter_by(title=title).first()

    def get_all_movies(self):
        with self.get_session() as session:
            return session.query(Movie).all()
    def get_all_actors(self):
        with self.get_session() as session:
            return session.query(Actor).all()
    def get_movie_release_year(self, movie_title):
        with self.get_session() as session:
            movie = session.query(Movie).filter_by(title=movie_title).first()
            if movie and movie.release_date:
                return movie.release_date.split()[-1]  # Get the last part which is the year
            return None
    def get_movies_by_genre(self, genre_name):
        with self.get_session() as session:
            genre = session.query(Genre).filter_by(name=genre_name).first()
            return genre.movies if genre else []

    def get_movies_by_director(self, director_name):
        with self.get_session() as session:
            director = session.query(Director).filter_by(name=director_name).first()
            return director.movies if director else []

    def get_actor_by_name(self, actor_name):
        with self.get_session() as session:
            return session.query(Actor).filter_by(name=actor_name).first()

    def get_movies_by_actor(self, actor_name):
        with self.get_session() as session:
            # Use joinedload to eagerly load the movie_roles relationship
            actor = session.query(Actor).options(joinedload(Actor.movie_roles)).filter_by(name=actor_name).first()
            if actor:
                # Since we've eagerly loaded movie_roles, this won't trigger a lazy load
                return [role.movie for role in actor.movie_roles]
            return []
    def get_character_movies_by_actor(self, actor_name):
        with self.get_session() as session:
            actor = session.query(Actor).options(joinedload(Actor.movie_roles)).filter_by(name=actor_name).first()
            if actor:
                character_movies = []
                for role in actor.movie_roles:
                    if '(character)' or '(voice)'in role.roles.lower():# and 'unknown' !=  role.roles.lower():
                        character_movies.append(role.movie)
                return character_movies
            return []
    def delete_movie(self, movie_id):
        with self.get_session() as session:
            movie = session.query(Movie).filter_by(id=movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
                return True
            return False
