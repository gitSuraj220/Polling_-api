
const express = require('express');

const app = express();
const port = 7200;

const db = require('./config/mongoose');

// middle for parse form data
app.use(express.urlencoded({ extended : true }));
app.use(express.json());

// route for home
app.use('/', require('./routes/index'));

app.listen(port, function(err){
    if(err){
        console.log('Error while running server', err);
        return;
    }
    console.log(`server running on port ${port}`);
});