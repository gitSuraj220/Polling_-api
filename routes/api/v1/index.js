
const express = require('express');
const router = express.Router();

router.use('/questions', require('./question'));
router.use('/options', require('./option'));
router.use('/bank', require('./bank_question'));

module.exports = router;