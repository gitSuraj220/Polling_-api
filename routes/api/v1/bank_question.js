const express = require('express');
const router  = express.Router();
const ctrl    = require('../../../controller/api/v1/bank_question_controller');

// Questions
router.get('/questions',              ctrl.getQuestions);
router.get('/questions/:id',          ctrl.getQuestion);
router.post('/questions/create',      ctrl.createQuestion);
router.delete('/questions/:id/delete',ctrl.deleteQuestion);

// Subjects
router.get('/subjects',               ctrl.getSubjects);
router.post('/subjects/create',       ctrl.createSubject);

// Topics
router.get('/topics',                 ctrl.getTopics);
router.post('/topics/create',         ctrl.createTopic);

module.exports = router;
