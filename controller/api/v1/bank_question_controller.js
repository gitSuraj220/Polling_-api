const BankQuestion = require('../../../models/bank_question');
const Subject      = require('../../../models/subject');
const Topic        = require('../../../models/topic');

// GET /api/v1/bank/questions — list with filters
const getQuestions = async (req, res) => {
    try {
        const { subject, topic, difficulty, exam, page = 1, limit = 20 } = req.query;
        const filter = {};
        if (subject)    filter.subject    = subject;
        if (topic)      filter.topic      = topic;
        if (difficulty) filter.difficulty = difficulty;
        if (exam)       filter.examTypes  = { $in: [exam] };

        const skip = (parseInt(page) - 1) * parseInt(limit);
        const [questions, total] = await Promise.all([
            BankQuestion.find(filter)
                .populate('subject', 'name code')
                .populate('topic', 'name')
                .skip(skip).limit(parseInt(limit))
                .sort({ createdAt: -1 }),
            BankQuestion.countDocuments(filter)
        ]);

        return res.json({ success: true, data: questions, total, page: parseInt(page), limit: parseInt(limit) });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

// GET /api/v1/bank/questions/:id
const getQuestion = async (req, res) => {
    try {
        const question = await BankQuestion.findById(req.params.id)
            .populate('subject', 'name code')
            .populate('topic', 'name');
        if (!question) return res.status(404).json({ success: false, message: 'Question not found' });
        return res.json({ success: true, data: question });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

// POST /api/v1/bank/questions/create
const createQuestion = async (req, res) => {
    try {
        const { content, options, correctOption, explanation, difficulty, subject, topic, examTypes, year, isPreviousYear, tags, marks } = req.body;
        const question = await BankQuestion.create({
            content, options, correctOption, explanation,
            difficulty, subject, topic, examTypes,
            year, isPreviousYear, tags, marks
        });
        await Topic.findByIdAndUpdate(topic, { $inc: { questionCount: 1 } });
        return res.status(201).json({ success: true, data: question });
    } catch (err) {
        return res.status(400).json({ success: false, message: err.message });
    }
};

// DELETE /api/v1/bank/questions/:id/delete
const deleteQuestion = async (req, res) => {
    try {
        const question = await BankQuestion.findByIdAndDelete(req.params.id);
        if (!question) return res.status(404).json({ success: false, message: 'Question not found' });
        await Topic.findByIdAndUpdate(question.topic, { $inc: { questionCount: -1 } });
        return res.json({ success: true, message: 'Question deleted' });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

// GET /api/v1/bank/subjects
const getSubjects = async (req, res) => {
    try {
        const subjects = await Subject.find().populate('topics', 'name questionCount');
        return res.json({ success: true, data: subjects });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

// POST /api/v1/bank/subjects/create
const createSubject = async (req, res) => {
    try {
        const subject = await Subject.create(req.body);
        return res.status(201).json({ success: true, data: subject });
    } catch (err) {
        return res.status(400).json({ success: false, message: err.message });
    }
};

// POST /api/v1/bank/topics/create
const createTopic = async (req, res) => {
    try {
        const topic = await Topic.create(req.body);
        await Subject.findByIdAndUpdate(topic.subject, { $push: { topics: topic._id } });
        return res.status(201).json({ success: true, data: topic });
    } catch (err) {
        return res.status(400).json({ success: false, message: err.message });
    }
};

// GET /api/v1/bank/topics?subject=:subjectId
const getTopics = async (req, res) => {
    try {
        const filter = req.query.subject ? { subject: req.query.subject } : {};
        const topics = await Topic.find(filter).populate('subject', 'name code');
        return res.json({ success: true, data: topics });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

module.exports = { getQuestions, getQuestion, createQuestion, deleteQuestion, getSubjects, createSubject, getTopics, createTopic };
