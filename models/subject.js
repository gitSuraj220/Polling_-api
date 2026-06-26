const mongoose = require('mongoose');

const subjectSchema = new mongoose.Schema({
    name: { type: String, required: true, unique: true },
    code: { type: String, required: true, uppercase: true },
    description: { type: String, default: '' },
    icon: { type: String, default: '' },
    topics: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Topic' }]
}, { timestamps: true });

module.exports = mongoose.model('Subject', subjectSchema);
