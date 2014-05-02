import config

from app import app
from flask import session
from . import send_json
from common.utils import debug
from common import db
from models.post import Post
from models.tag import Tag
from models.comment import Comment

def add_new_post():
  data = dict(
    title="new_post_title", 
    content="new_post_content",
    status="public"
  )
  new_post = Post(**data)
  db.session.add(new_post)
  db.session.commit()


def test_create_new_comment():
  add_new_post()
  add_new_post()
  with app.test_client() as c:
    data = dict(
      post_id=2,
      user_email="iammfw@163.com",
      username="jerry",
      content="hello"
    )
    rv = send_json('post', '/new_comment', data, c)
    post = db.session.query(Post).filter_by(id=2).first()
    assert 'success' in rv.data
    assert post.comments[0].content == 'hello'

    data = dict(
      post_id=2000,
      user_email="iammfw@163.com",
      username="jerry",
      content="hello"
    )
    rv = send_json('post', '/new_comment', data, c)
    assert 'post is not found' in rv.data

    data = dict(
      post_id=2,
      user_email="",
      username="",
      content=""
    )
    rv = send_json('post', '/new_comment', data, c)
    post = db.session.query(Post).filter_by(id=2).first()
    assert 'user_email is empty' in rv.data
    assert rv.status_code == 400

def test_delete_comment():
  with app.test_client() as c:
    with c.session_transaction() as sess:
      sess['is_admin'] = True
      sess['user'] = '{"id": "1"}'

    comment = db.session.query(Comment).filter_by(id=1).first()
    assert comment is not None

    data = {'id': '1'}
    rv = send_json('delete', '/delete_comment', data, c)
    comment = db.session.query(Comment).filter_by(id=1).first()
    assert comment is None
