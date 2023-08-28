from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas
from .database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:

    try:
        conn = psycopg2.connect(host="localhost", database='fastapi', user='postgres', password='Hapoel69', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull ")
        break
    except Exception as error:
        print("connection failed")
        print("Error", error)
        time.sleep(2)


@app.get("/")
async def root():
    return {"message": "welcome to my web"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.post).all()
    return {"data": posts}


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, 
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.post(
        title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"detail": post}


@app.get("/posts/{id}")
def get_posts(id: int, reponse: Response, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * from posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    # post = db.query(models.post).filter(models.post.id == id).first()
    post = db.query(models.post).filter(models.post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.post).filter(models.post.id == id)

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, update_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title =%s, content = %s,  
    #                published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id),))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.post).filter(models.post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    post_query.update(update_post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}



