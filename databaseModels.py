from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, LargeBinary, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

# Create an association table for the many-to-many relationship
movie_genre = Table('movie_genre', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    director_id = Column(Integer, ForeignKey('directors.id'))
    tomato_meter = Column(Float)
    popcorn_meter = Column(Float)
    imdb_score = Column(Float)
    box_office = Column(String(255))
    poster = Column(LargeBinary)
    poster_path = Column(String(255))
    release_date = Column(String(10))
    runtime = Column(Integer)
    mpaa_rating = Column(String(10))
    synopsis = Column(String(1000))
    awards = Column(String(1000))
    genres = relationship("Genre", secondary=movie_genre, back_populates="movies")
    director = relationship("Director", back_populates="movies")
    actor_roles = relationship("MovieActor", back_populates="movie")

    def get_age(self):
        if self.release_date:
            return int(datetime.now().year) - int(self.release_date.split('-')[0])
        else:
            return None
    def get_release_year(self):
        try:
            return self.release_date.split('-')[0]
        except:
            return None
    @classmethod
    def add_or_update_movie(cls, session, **kwargs):
        movie = session.query(cls).filter_by(title=kwargs['title']).first()
        if movie:
            for key, value in kwargs.items():
                if hasattr(movie, key) and value is not None and value != '' and key not in ['director', 'genre', 'actors']:
                    setattr(movie, key, value)
        else:
            # Create a new movie instance with explicit attribute assignments
            movie = cls(
                title=kwargs.get('title'),
                genre_id=kwargs.get('genre_id'),
                director_id=kwargs.get('director_id'),
                tomato_meter=kwargs.get('tomato_meter'),
                popcorn_meter=kwargs.get('popcorn_meter'),
                imdb_score=kwargs.get('imdb_score'),
                box_office=kwargs.get('box_office'),
                poster=kwargs.get('poster_bytes'),
                poster_path=kwargs.get('poster_path'),
                release_date=kwargs.get('release_date'),
                runtime=kwargs.get('runtime'),
                mpaa_rating=kwargs.get('mpaa_rating'),
                synopsis=kwargs.get('synopsis'),
                awards=kwargs.get('awards')
            )
            print(f"Created new movie: {movie.title}")  # Debug print
            session.add(movie)
        
        # Handle related entities
        cls.handle_related_entity(session, movie, Genre, 'genre', 'genres', movie_genre, **kwargs)
        cls.handle_related_entity(session, movie, Director, 'director', 'director', **kwargs)
        cls.handle_related_entity(session, movie, Actor, 'actors', 'actor_roles', MovieActor, **kwargs)

        session.commit()
        return movie

    @staticmethod
    def handle_related_entity(session, movie, EntityClass, kwarg_key, relationship_attr, association_table=None, **kwargs):
        if kwarg_key in kwargs and kwargs[kwarg_key] and kwargs[kwarg_key] != 'N/A':
            names = [name.strip() for name in kwargs[kwarg_key].split(',')]
            for name in names:
                entity = session.query(EntityClass).filter_by(name=name).first()
                if not entity:
                    entity = EntityClass(name=name)
                    session.add(entity)
                    session.flush()

                if association_table is not None:
                    # Many-to-many relationship (genres, actors)
                    existing_relation = session.query(association_table).filter_by(
                        movie_id=movie.id, 
                        **{f"{EntityClass.__name__.lower()}_id": entity.id}
                    ).first()
                    if not existing_relation:
                        if EntityClass == Actor:
                            roles = kwargs['role'] if name.lower().replace(' ', '') == kwargs['actor_name'].lower().replace(' ', '') else "Unknown"
                            movie_actor = association_table(movie=movie, actor=entity, roles=roles)
                            session.add(movie_actor)  # Ensure the MovieActor object is added to the session
                        else:
                            session.execute(association_table.insert().values(
                                movie_id=movie.id, 
                                **{f"{EntityClass.__name__.lower()}_id": entity.id}
                            ))
                else:
                    # One-to-many relationship (director)
                    setattr(movie, relationship_attr, entity)

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(1000))
    movies = relationship("Movie", secondary=movie_genre, back_populates="genres")

class Director(Base):
    __tablename__ = 'directors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(String(10))
    nationality = Column(String(50))
    biography = Column(String(1000))
    death_date = Column(String(10))
    movies = relationship("Movie", back_populates="director")

    def get_age(self):
        if self.death_date:
            return int(self.death_date.split('-')[0]) - int(self.birth_date.split('-')[0])
        else:
            return int(datetime.now().year) - int(self.birth_date.split('-')[0])

class Actor(Base):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(String(10))
    nationality = Column(String(50))
    biography = Column(String(1000))
    death_date = Column(String(10))
    oscars_wins = Column(Integer, nullable=False, default=0)
    oscars_nominations = Column(Integer, nullable=False, default=0)
    movie_roles = relationship("MovieActor", back_populates="actor")
    portrait = Column(LargeBinary)
    portrait_path = Column(String(500))
    def get_age(self):
        if self.death_date:
            return int(self.death_date.split('-')[0]) - int(self.birth_date.split('-')[0])
        else:
            return int(datetime.now().year) - int(self.birth_date.split('-')[0])
    def update_birthdate(self, birthdate):
        self.birth_date = birthdate
    def update_oscars(self, oscars_wins, oscars_nominations):
        self.oscars_wins = oscars_wins
        self.oscars_nominations = oscars_nominations
class MovieActor(Base):
    __tablename__ = 'movie_actors'

    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actors.id'), primary_key=True)
    roles = Column(String(500), nullable=False)  # Store multiple roles as a comma-separated string
    
    movie = relationship("Movie", back_populates="actor_roles")
    actor = relationship("Actor", back_populates="movie_roles")

    def get_roles(self, actor_name):
        return [role.strip() for role in self.roles.split(',')]

    def has_roles(self, actor_name):
        actor = self.actor
        if actor and actor.name == actor_name:
            return bool(self.roles)
        return False
