const mongoose = require('mongoose');

const bankQuestionSchema = new mongoose.Schema({
    content: { type: String, required: true },
    options: {
        type: [String],
        validate: { validator: v => v.length === 4, message: 'Exactly 4 options required' }
    },
    correctOption: { type: Number, min: 0, max: 3, required: true },
    explanation:   { type: String, default: '' },
    difficulty:    { type: String, enum: ['easy', 'medium', 'hard'], default: 'medium' },
    subject:       { type: mongoose.Schema.Types.ObjectId, ref: 'Subject', required: true },
    topic:         { type: mongoose.Schema.Types.ObjectId, ref: 'Topic',   required: true },
    examTypes:     { type: [String], default: [] },
    year:          { type: Number, default: null },
    isPreviousYear:{ type: Boolean, default: false },
    tags:          { type: [String], default: [] },
    marks:         { positive: { type: Number, default: 1 }, negative: { type: Number, default: 0.25 } }
}, { timestamps: true });

bankQuestionSchema.index({ subject: 1, topic: 1, difficulty: 1 });

module.exports = mongoose.model('BankQuestion', bankQuestionSchema);
