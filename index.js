
const express = require('express');
const path    = require('path');

const app = express();
const port = 7200;

const db = require('./config/mongoose');

// serve landing page
app.use(express.static(path.join(__dirname, 'public')));

// middleware for parse form data
app.use(express.urlencoded({ extended : true }));
app.use(express.json());

// routes
app.use('/', require('./routes/index'));

app.listen(port, function(err){
    if(err){
        console.log('Error while running server', err);
        return;
    }
    console.log(`server running on port ${port}`);
});