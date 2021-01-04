from unittest import TestCase
from app import app
from flask import Flask
from models import db, User, Post, Tag, PostTag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class BloglyTest(TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        db.session.rollback()

    
    def test_1_page_render(self):
        """Tests to see if certain pages within the application are loaded properly."""
        
        res = self.client.get("/")
        self.assertEqual(res.status_code, 302)

        res = self.client.get("/users")
        self.assertEqual(res.status_code, 200)

        res = self.client.get("/tags")
        self.assertEqual(res.status_code, 200)

        res = self.client.get("/posts")
        self.assertEqual(res.status_code, 200)
        

    def test_2_add_user(self):
        """Checks if a new user is created and is stored in the database successfully, and that their their profile page is rendered correctly.
        At this point the only ID is 1 in the database."""
        
        post_res = self.add_user("Some", "One")
        res = self.client.get("/users/1")

        profile_page = res.get_data(as_text=True)

        self.assertEqual(post_res.status_code, 302)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Some One", profile_page)

    def test_3_delete_user(self):
        """Ensures that the delete function works properly and that no user with an ID of 2 (in this case) is in the database."""

        self.add_user("Another", "Person")
        delete_res = self.client.get("/users/2/delete")

        self.assertEqual(delete_res.status_code, 302)
        self.assertEqual(User.query.filter_by(id=2).first(), None)


    def test_4_add_post(self):
        """Adds a new post to the database.
        A user with an ID of 1 exists in the table at this point, so a post from that user can be made."""

        post_res = self.client.post("/users/1/posts/new", data={"title": "Some Title", "content": "This is some test content."})
        res = self.client.get("/posts/1")

        post = res.get_data(as_text=True)

        self.assertEqual(post_res.status_code, 302)
        self.assertIn("Some Title", post)
        self.assertIn("This is some test content.", post)


    def test_5_delete_post(self):
        """Deletes the first post with an ID of 1 successfully in the database."""

        post_res = self.client.post("/users/1/posts/new", data={"title": "Another Title", "content": "This is some more test content."})
        delete_res = self.client.post("/posts/2/delete")

        self.assertEqual(delete_res.status_code, 302)
        self.assertEqual(Post.query.filter_by(id=2).first(), None)


    def test_6_add_tag(self):
        """Adds a tag to the database, as well as to the first post that was created."""

        tag_res = self.client.post("/tags/new", data={"name": "Test"})
        res = self.client.get("/tags")

        tags_html = res.get_data(as_text=True)

        self.assertEqual(tag_res.status_code, 302)
        self.assertIn("Test", tags_html)

        post = Post.query.get(1)

        post_res = self.client.post("/posts/1/edit", data={"title": post.title, "content": post.content, "tags": ["Test"]})

        post = Post.query.get(1)
        tag = Tag.query.filter_by(name = "Test").first()
        post_tag = PostTag.query.filter_by(post_id=1, tag_id=1).first()

        self.assertEqual(post.id, post_tag.post_id)
        self.assertEqual(tag.id, post_tag.tag_id)


    def test_7_delete_tag(self):
        """Deletes a tag and makes sure that no post contains that deleted tag."""

        delete_res = self.client.post("/tags/1/delete")

        self.assertEqual(delete_res.status_code, 302)
        self.assertEqual(Tag.query.filter_by(id=1).first(), None)

        post_tag = PostTag.query.filter_by(post_id=1, tag_id=1).first()

        self.assertEqual(post_tag, None)


    def add_user(self, first, last):
        """Helper function to add a user to the database."""
        return self.client.post("/users/new", data={"firstname": first, "lastname": last, "image": "https://i0.wp.com/metro.co.uk/wp-content/uploads/2018/12/SEI_44899785-ec2c.jpg?quality=90&strip=all&zoom=1&resize=540%2C540&ssl=1"})
