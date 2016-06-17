from .models import db, Photo
from random import randint


def generate_filename(length):
    characters = list("01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    filename = ""

    for i in range(length):
        filename += characters[randint(0, len(characters) - 1)]

    return filename


def get_images_sort_old(page, images_per_page):

    # Sort by ascending creation date
    return Photo.query.order_by(Photo.created_on).offset(images_per_page * page).limit(images_per_page)


def get_images_sort_new(page, images_per_page):

    # Sort by descending creation date
    return Photo.query.order_by(Photo.created_on.desc()).offset(images_per_page * page).limit(images_per_page)


def get_images_sort_hot(page, images_per_page):
    # Implementation of reddit's hot sorting algorithm in SQL
    # This is implemented in SQL because it's sorting in the database and limiting to the number of images per page is more efficient than getting the whole table
    # The number of images per page is set in the config

    # 45000 is a magic number in reddit's code too. It's the number of seconds in 12.5 hours
    # The way the algorithm works requires an image to have 10 times as many points as one 12.5 hours newer to be ranked above it
    # While this could be moved to a constant, it is simpler to have it in the query as it's only used once,
    # and using string concating is a bit of a hack when creating queries

    return db.session.execute(
        "SELECT photo.id, photo.title, photo.filename, photo.mimetype, photo.votes, photo.created_on FROM photo " +
        "ORDER BY ROUND(CAST(LOG(GREATEST(ABS(photo.votes), 1)) * SIGN(photo.votes) + DATE_PART('epoch', photo.created_on) / 45000.0 as NUMERIC), 7) DESC " +
        "OFFSET " + str(images_per_page * page) + " LIMIT " + str(images_per_page)
    )
