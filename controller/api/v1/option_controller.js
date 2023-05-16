
const mongoose = require('mongoose');

// import models
const Question = require('../../../models/question');
const Option = require('../../../models/option');


// create option for the question on the basis of id
module.exports.createOption = async function(req, res){

    try{
        // check question is there or not
        let question = await Question.findById(req.params.id);

        if(question){
            // create an option
            let option = await Option.create({
                content : req.body.content,
                votes : req.body.votes,
                question : req.params.id,
            });

            option.link_vote = "http://localhost:8000/api/v1/options/"+option.id+"/add_vote";
            option.save();
            
            question.options.push(option);
            question.save();

            return res.json({option, data:{
                "message" : "Option created Successfully"
            }});
        }
        return res.json({question});

    }catch(err){
        console.log('Error = ', err);
        return;
    }

};


// delete an option on the basis of its id
module.exports.optionDelete = async function(req, res){

    try{

        let id = req.params.id;

        // find the option is exist or not
        let option = await Option.findById(id);

        // if option is present then check it has vote or not
        // if option has vote then not to delete it
        if(option.votes > 0){
            return res.status(404).json({
                data : { message : "not able to delete it! It has vote" }
            });
        }

        // delete option form question.options array also
        await Question.findByIdAndUpdate(option.question, {$pull : {options : id}});

        // else delete the option from option
        await Option.findByIdAndDelete(id);

        return res.status(200).json({
            data : { message : "Option deleted sucessfully" }
        });

    }catch(err){
        return res.status(500).json({
            data : { message : "Internal server error" }
        });
    }

};



// adding a vote to an option for perticular question
module.exports.addVote = async function(req, res){

    try{

        let id = req.params.id;

        // find option if present then vote to it
        await Option.findByIdAndUpdate(id, { $inc : { votes : 1 }});

        return res.status(200).json({
            data : { message : "Voted successfully" }
        });

    }catch(err){
        return res.status(500).json({
            data : { message : "Internal server error" }
        });
    }
    
};