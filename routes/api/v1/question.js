
const express = require('express');
const router = express.Router();

const questionController = require('../../../controller/api/v1/question_controller');

router.post('/create', questionController.createQuestion);
router.get('/:id', questionController.viewQuestions);
router.delete('/:id/delete', questionController.deleteQuestion);

module.exports = router;