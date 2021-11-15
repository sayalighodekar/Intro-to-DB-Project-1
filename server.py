
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash
from sqlalchemy.exc import IntegrityError
from flask import session
from flask import redirect, url_for 



tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.config.update(SECRET_KEY=os.urandom(24))


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://fs2751:9751@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.before_request
def load_logged_in_user():
  """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
  user_id = session.get("user_id")
  if user_id is None:
      g.user = None
  else:
      g.user = g.conn.execute(
          "SELECT * FROM users WHERE uid = (%s)", (user_id,)
      ).fetchone()

  print(g.user)


@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
#   cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  #return render_template("index.html", **context)
  return render_template("base.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/another')
def another():
  return render_template("another.html")


@app.route('/home')
def home():
  return render_template("home.html")

@app.route('/stores')
def stores():

  cursor = g.conn.execute("SELECT A.name FROM follows F INNER JOIN authors A ON F.aid = A.aid WHERE uid=(%s)",uid)
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT B.title FROM favorites F INNER JOIN books B ON F.isbn = B.isbn WHERE uid=(%s)",uid)
  books = []
  for result in cursor:
    books.append(result['title'])  # can also be accessed using result[0]
  cursor.close()

  context = dict(authors = names, books= books)

  return render_template("stores.html")

@app.route('/ratings')
def ratings():

  return render_template("ratings.html")

@app.route('/profile')
def profile():

  uid = session["user_id"]
  print("current user",uid)
  cursor = g.conn.execute("SELECT A.name FROM follows F INNER JOIN authors A ON F.aid = A.aid WHERE uid=(%s)",uid)
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT B.title FROM favorites F INNER JOIN books B ON F.isbn = B.isbn WHERE uid=(%s)",uid)
  books = []
  for result in cursor:
    books.append(result['title'])  # can also be accessed using result[0]
  cursor.close()

  context = dict(authors = names, books= books)

  return render_template("profile.html", **context)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['value']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/addFavorite', methods=['POST'])
def addFavorite():
  name = request.form['title']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  print(name)
  return redirect('/')


@app.route('/searchBooks', methods=['POST'])
def searchBooks():
  select_title = request.form["title"]
  cursor = g.conn.execute("SELECT b.title, a.name, b.isbn, b.avg_rating, b.language, g.genre_name,"
                          "b.num_pages, b.publication_date, b.rating_count, b.review_count, b.description "
                          "FROM books b, authors a, written_by w, genre g WHERE b.isbn = w.isbn "
                          "AND a.aid = w.aid AND g.gid = w.gid AND b.title = %s", select_title)
  title = []
  l = ["title: ", "author: ", "ISBN: ", "rating: ", "language: ", "genre: ", "pages: ", "publication date: ",
       "ratings count: ", "reviews count:", "summary: "]
  numResults = 0
  for result in cursor:
    title.append(result[0])
    title.append(result[1])
    title.append(result[2])
    title.append(result[3])
    title.append(result[4])
    title.append(result[5])
    title.append(result[6])
    title.append(result[7])
    title.append(result[8])
    title.append(result[9])
    title.append(result[10])
    numResults = numResults + 1
  cursor.close()
  if numResults == 0:
    flash("Aww snap! no such book")
    return redirect(url_for('home'))
    

  context = dict(data = title, l = l, input = select_title, numResults = numResults)
  return render_template("searchBooks.html", **context)

@app.route('/searchAuthor', methods=['POST'])
def searchAuthor():
  select_name = request.form["name"]
  cursor = g.conn.execute("SELECT b.title, b.isbn FROM books b, authors a, written_by w "
                          "WHERE b.isbn = w.isbn AND a.aid = w.aid AND a.name = %s "
                          "ORDER BY a.aid", select_name)
  cursor2 = g.conn.execute("SELECT a.aid, a.avg_rating, a.website FROM authors a WHERE a.name = %s"
                           , select_name)
  cursor3 = g.conn.execute("SELECT COUNT(*) FROM books b, authors a, written_by w WHERE b.isbn "
                           "= w.isbn AND a.aid = w.aid AND a.name = %s GROUP BY a.aid "
                           "ORDER BY a.aid ASC", select_name)

  books = []
  authorInfo = []
  numBooks = [] #number of books size aid had
  counter = [] #the counter for return book results to the correct aid
  l = ["author ID: ", "author rating: ", "website: "]
  numResults = 0
  for result in cursor:
    books.append("'" + result[0] + "', ISBN: " + str(result[1]))
  cursor.close()

  for result in cursor2:
      authorInfo.append(result[0])
      authorInfo.append(result[1])
      authorInfo.append(result[2])
      numResults = numResults + 1
  cursor2.close()

  for result in cursor3:
      numBooks.append(result)
  cursor3.close()

  counter.append(0)

  for i in range(1, len(numBooks)):
      counter.append(counter[i-1] + numBooks[i-1][0])

  if len(authorInfo) == 0:
      select_name = "No Results"

  if numResults == 0:
    flash("Aww snap! no such author")
    return redirect(url_for('home'))

  context = dict(data = books, name = select_name, info = authorInfo, l=l, numBooks = numBooks,
                 counter = counter, numResults = numResults)
  return render_template("searchAuthor.html", **context)

@app.route('/searchGenre', methods=['POST'])
def searchGenre():
  select_genre = request.form["genre"]
  num_results = request.form["num"]
  sort_order = request.form["order"]
  if sort_order == "DESC":
    cursor = g.conn.execute("SELECT b.title, a.name, b.isbn, b.avg_rating FROM books b, authors a, "
                          "written_by w, genre g WHERE b.isbn = w.isbn AND a.aid = w.aid "
                          "AND g.gid = w.gid AND g.genre_name = %s ORDER BY b.avg_rating DESC "
                          "LIMIT %s", select_genre, num_results)
  elif sort_order == "ASC":
      cursor = g.conn.execute("SELECT b.title, a.name, b.isbn, b.avg_rating FROM books b, authors a, "
                                "written_by w, genre g WHERE b.isbn = w.isbn AND a.aid = w.aid "
                                "AND g.gid = w.gid AND g.genre_name = %s ORDER BY b.avg_rating ASC "
                                "LIMIT %s", select_genre, num_results)
  title = []
  numResults = 0
  for result in cursor:
    title.append("'" + result[0] + "', by " + result[1] + ", ISBN: " + str(result[2]) +
                                                         ", rating: " + str(result[3]))
    numResults = numResults + 1
  cursor.close()

  if numResults == 0:
    flash("Aww snap! no book in this genre")
    return redirect(url_for('home'))

  context = dict(data = title)
  return render_template("searchGenre.html", **context)


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        print(username, password)
        if error is None:
            try:
                g.conn.execute(
                    "INSERT INTO users (displayname, password) VALUES (%s, %s)",
                    (username, password),
                )
            except IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("login"))

            flash(error)

    return render_template('register.html')


@app.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        #db = get_db()
        error = None
        user = g.conn.execute(
            "SELECT * FROM users WHERE displayname = (%s)", (username,)
        ).fetchone()
        print(user)

        if user is None:
            error = "Incorrect username."
        elif user["password"] != password:
            error = "Incorrect password"

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["uid"]
            #g.user = user
            #return render_template("home.html")
            return redirect(url_for('home'))

        flash(error)

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    print("logout successful!")
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()