const mongoose = require('mongoose');

const topicSchema = new mongoose.Schema({
    name: { type: String, required: true },
    subject: { type: mongoose.Schema.Types.ObjectId, ref: 'Subject', required: true },
    description: { type: String, default: '' },
    questionCount: { type: Number, default: 0 }
}, { timestamps: true });

module.exports = mongoose.model('Topic', topicSchema);
