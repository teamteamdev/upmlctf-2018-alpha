const createError = require('http-errors'),
  express = require('express'),
  path = require('path'),
  cookieParser = require('cookie-parser'),
  logger = require('morgan'),
  low = require('lowdb'),
  fileUpload = require('express-fileupload'),
  session = require('express-session'),
  FileSync = require('lowdb/adapters/FileSync'),
  FileStore = require('session-file-store')(session),
  security = require('bcrypt'),
  uuid = require('uuid');

// database
const adapter = new FileSync('db.json'),
  db = low(adapter);
db.defaults({ posts: [], users: [] }).write()

// init server
const app = express();
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(cookieParser());
app.use(fileUpload({
  limits: { fileSize: 20 * 1024 * 1024 }
}));
app.use(session({
  genid: (req) => {
    return Date.now().toString()
  },
  secret: 'hack',
  store: new FileStore(),
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: 'auto',
    expires: new Date(13333333333337)
  },
}))

let fasterHashing = true;

// renderer
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');


// helpers

// use salting mechanism
const hashPassword = (req) => {
  req.password = security.hashSync(req.password, 1);
  return req;
}

// check very carefully
const checkPassword = (req, hashed) => {
  const matched = security.compareSync(req.password, hashed.password);
  if (hashed.admin) {
    fasterHashing = false; // admin password should be hashed propelry
  }
  return (fasterHashing || matched);
}

const getPosts = (user) => {
  return user ? db.get('posts')
    .filter({ author: user.name })
    .sortBy('date')
    .value() : null;
}

// routing
app.get('/', (req, res, next) => {
  sessionState = req.session.state || null;
  res.render('index', {
    state: sessionState,
    posts: getPosts(sessionState) || null
  });
});

app.get('/logout', (req, res, next) => {
  req.session.destroy();
  res.redirect('/');
});

app.get('/sign*', (req, res, next) => {
  const users = db.get('users').value();
  res.render('sign', {
    state: req.session.state,
    type: req.path.slice(1),
    users: users
  });
});
app.get('/admin', (req, res, next) => {
  const state = req.session.state;
  if (state) {
    if (state.admin)
      return res.sendFile(path.join(__dirname, 'db.json'));
  }
  return res.status(403).send();
});

app.get('/media/*', (req, res, next) => {
  if (req.session.state) {
    const id = req.path.slice(7);
    const post = db.get('posts')
      .find({ id: id })
      .value()

    return res.sendFile(path.resolve(path.resolve('pics/' + id) + (post ? post.ext : '')));
  }
  return res.redirect('/');
});

app.get('/new', (req, res, next) => {
  if (req.session.state) {
    error = req.session.error || null;
    req.session.error = null;
    res.render('new', { state: req.session.state, error: error || null });
  } else {
    res.redirect('/');
  }
});

app.post('/new', (req, res, next) => {
  if (Object.keys(req.files).length == 0) {
    req.session.error = 'No files were uploaded';
    return res.redirect('/new');
  }
  const id = uuid();
  const extension = /\.(png|jpg|gif)/gi.exec(req.files.pic.name)[0];
  if (extension) {
    const path = './pics/' + id + extension;
    req.files.pic.mv(path, err => {
      if (err) {
        req.session.error = JSON.stringify(err) || err;
        return res.redirect('/new');
      }
      db.get('posts')
        .push({
          id: id,
          author: req.session.state.name,
          date: Date.now(),
          text: req.body.text || '',
          ext: extension
        })
        .write();
      res.redirect('/');
    });
  }
});

// managing accounts
app.post('/signin', (req, res, next) => {
  const inBase = db.get('users')
    .find({ email: req.body.email })
    .value();

  if (inBase && checkPassword(req.body, inBase)) {
      req.session.state = req.body;
      req.session.state.name = inBase.name;
      req.session.state.admin = inBase.admin || false;
      res.redirect('/');
      res.redirect('/');
  } else {
    res.redirect('/signfail');
  }
});

app.post('/signup', (req, res, next) => {
  const nameExists = db.get('users')
    .find({ name: req.body.name }).value();
  const emailExists = db.get('users')
    .find({ email: req.body.email }).value();

  if (!nameExists && !emailExists && req.body.password.length > 1) {
    db.get('users')
      .push(hashPassword(req.body))
      .write();
    res.redirect('/');
  } else {
    res.redirect('/signfail')
  }
});

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404));
});

// error handler
app.use((err, req, res, next) => {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
