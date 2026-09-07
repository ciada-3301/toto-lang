/**
 * Toto–English–Bengali Trilateral Translation Web App — Client Logic
 * Handles mutual input locking between English and Bengali, trilateral rendering,
 * and translation trigger on button click / Ctrl+Enter.
 */

document.addEventListener('DOMContentLoaded', () => {
    const englishInput = document.getElementById('english-input');
    const bengaliInput = document.getElementById('bengali-input');
    const englishCard = document.getElementById('english-card');
    const bengaliCard = document.getElementById('bengali-card');
    const englishCharCount = document.getElementById('english-char-count');
    const bengaliCharCount = document.getElementById('bengali-char-count');
    const englishBadge = document.getElementById('english-badge');
    const bengaliBadge = document.getElementById('bengali-badge');
    const actionHint = document.getElementById('action-hint');

    const translateBtn = document.getElementById('translate-btn');
    const clearBtn = document.getElementById('clear-btn');

    const scriptOutput = document.getElementById('script-output');
    const romanOutput = document.getElementById('roman-output');
    const glossOutput = document.getElementById('gloss-output');
    const notesOutput = document.getElementById('notes-output');
    const reasoningOutput = document.getElementById('reasoning-output');

    const copyScriptBtn = document.getElementById('copy-script-btn');
    const copyRomanBtn = document.getElementById('copy-roman-btn');
    const copyAllBtn = document.getElementById('copy-all-btn');
    const chipsContainer = document.getElementById('chips-container');

    let activeLanguage = null; // 'en', 'bn', or null

    // Update counters and mutual exclusivity
    function updateState() {
        const enLen = englishInput.value.trim().length;
        const bnLen = bengaliInput.value.trim().length;

        englishCharCount.textContent = `${englishInput.value.length} character${englishInput.value.length === 1 ? '' : 's'}`;
        bengaliCharCount.textContent = `${bengaliInput.value.length} character${bengaliInput.value.length === 1 ? '' : 's'}`;

        if (enLen > 0 && activeLanguage !== 'bn') {
            activeLanguage = 'en';
            englishCard.classList.add('active-input');
            englishCard.classList.remove('disabled');
            englishInput.disabled = false;
            englishBadge.textContent = 'Active Input (English)';

            bengaliCard.classList.add('disabled');
            bengaliCard.classList.remove('active-input');
            bengaliInput.disabled = true;
            bengaliBadge.textContent = 'Disabled (English active)';
            actionHint.textContent = 'Translating from English to Bengali & Toto';
        } else if (bnLen > 0 && activeLanguage !== 'en') {
            activeLanguage = 'bn';
            bengaliCard.classList.add('active-input');
            bengaliCard.classList.remove('disabled');
            bengaliInput.disabled = false;
            bengaliBadge.textContent = 'Active Input (বাংলা)';

            englishCard.classList.add('disabled');
            englishCard.classList.remove('active-input');
            englishInput.disabled = true;
            englishBadge.textContent = 'Disabled (Bengali active)';
            actionHint.textContent = 'Translating from Bengali to English & Toto';
        } else if (enLen === 0 && bnLen === 0) {
            resetInputLocks();
        }
    }

    function resetInputLocks() {
        activeLanguage = null;
        englishCard.classList.remove('disabled', 'active-input', 'populated');
        bengaliCard.classList.remove('disabled', 'active-input', 'populated');
        englishInput.disabled = false;
        bengaliInput.disabled = false;
        englishBadge.textContent = '';
        bengaliBadge.textContent = '';
        actionHint.textContent = 'Enter English or Bengali text, then click Translate (or Ctrl+Enter)';
    }

    englishInput.addEventListener('input', () => {
        if (activeLanguage === 'bn') return;
        updateState();
    });

    bengaliInput.addEventListener('input', () => {
        if (activeLanguage === 'en') return;
        updateState();
    });

    // Keyboard shortcut: Ctrl+Enter triggers translation
    function handleKeyDown(e) {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            performTranslation();
        }
    }
    englishInput.addEventListener('keydown', handleKeyDown);
    bengaliInput.addEventListener('keydown', handleKeyDown);

    // Translate button click
    translateBtn.addEventListener('click', () => {
        performTranslation();
    });

    // Clear All button
    clearBtn.addEventListener('click', () => {
        englishInput.value = '';
        bengaliInput.value = '';
        resetInputLocks();
        resetOutputs();
        englishInput.focus();
    });

    // Sample chip clicks: Populate appropriate box and lock the other
    if (chipsContainer) {
        chipsContainer.addEventListener('click', (e) => {
            const chip = e.target.closest('.chip');
            if (!chip) return;
            const lang = chip.getAttribute('data-lang') || 'en';
            const text = chip.getAttribute('data-text') || '';

            resetInputLocks();
            if (lang === 'bn') {
                englishInput.value = '';
                bengaliInput.value = text;
                bengaliInput.focus();
            } else {
                bengaliInput.value = '';
                englishInput.value = text;
                englishInput.focus();
            }
            updateState();
        });
    }

    // Translation Request
    async function performTranslation() {
        let text = '';
        let lang = 'en';

        if (activeLanguage === 'bn') {
            text = bengaliInput.value.trim();
            lang = 'bn';
        } else if (activeLanguage === 'en') {
            text = englishInput.value.trim();
            lang = 'en';
        } else {
            // Check whichever has text
            if (englishInput.value.trim()) {
                text = englishInput.value.trim();
                lang = 'en';
            } else if (bengaliInput.value.trim()) {
                text = bengaliInput.value.trim();
                lang = 'bn';
            }
        }

        if (!text) {
            if (activeLanguage === 'bn') {
                bengaliInput.focus();
            } else {
                englishInput.focus();
            }
            return;
        }

        // Set loading state
        translateBtn.disabled = true;
        const originalBtnText = translateBtn.textContent;
        translateBtn.textContent = 'Reasoning...';

        scriptOutput.textContent = 'Consulting Toto linguistic archive and translating...';
        scriptOutput.classList.add('placeholder');
        romanOutput.textContent = 'Synthesizing...';
        romanOutput.classList.add('placeholder');
        glossOutput.textContent = 'Deconstructing morphemes...';
        notesOutput.textContent = 'Synthesizing grammatical rules...';
        reasoningOutput.textContent = 'Awaiting model reasoning stream...';

        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, lang: lang })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Translation request failed');
            }

            // Populate the target language box with its translation
            if (lang === 'en' && data.bengali) {
                bengaliInput.value = data.bengali;
                bengaliCharCount.textContent = `${data.bengali.length} characters`;
                bengaliCard.classList.remove('disabled');
                bengaliCard.classList.add('populated');
                bengaliBadge.textContent = 'Translated (বাংলা)';
            } else if (lang === 'bn' && data.english) {
                englishInput.value = data.english;
                englishCharCount.textContent = `${data.english.length} characters`;
                englishCard.classList.remove('disabled');
                englishCard.classList.add('populated');
                englishBadge.textContent = 'Translated (English)';
            }

            // Render Native Toto Script
            if (data.toto_script) {
                scriptOutput.textContent = data.toto_script;
                scriptOutput.classList.remove('placeholder');
            } else {
                scriptOutput.textContent = data.toto || '\u2014';
                scriptOutput.classList.remove('placeholder');
            }

            // Render Romanized Toto
            romanOutput.textContent = data.toto || '\u2014';
            romanOutput.classList.remove('placeholder');

            // Render Gloss
            glossOutput.textContent = data.literal_gloss || 'No morpheme breakdown returned.';

            // Render Notes
            notesOutput.textContent = data.notes || 'No grammatical notes returned.';

            // Render Model Reasoning Trace
            reasoningOutput.textContent = data.reasoning || 'Reasoning trace was absorbed into the generation pass.';

        } catch (err) {
            scriptOutput.textContent = 'Translation unavailable.';
            scriptOutput.classList.remove('placeholder');
            romanOutput.textContent = '\u2014';
            glossOutput.textContent = '\u2014';
            notesOutput.textContent = `Error: ${err.message}`;
            reasoningOutput.textContent = 'No reasoning trace available due to request error.';
        } finally {
            translateBtn.disabled = false;
            translateBtn.textContent = originalBtnText;
        }
    }

    function resetOutputs() {
        scriptOutput.textContent = 'Translation will appear here...';
        scriptOutput.classList.add('placeholder');
        romanOutput.textContent = '\u2014';
        romanOutput.classList.add('placeholder');
        glossOutput.textContent = '\u2014';
        notesOutput.textContent = '\u2014';
        reasoningOutput.textContent = 'No reasoning trace available.';
    }

    // Copy Handlers
    function showTemporaryFeedback(btn, message = 'Copied') {
        const orig = btn.textContent;
        btn.textContent = message;
        setTimeout(() => {
            btn.textContent = orig;
        }, 1500);
    }

    copyScriptBtn.addEventListener('click', () => {
        const text = scriptOutput.textContent;
        if (!text || scriptOutput.classList.contains('placeholder')) return;
        navigator.clipboard.writeText(text).then(() => showTemporaryFeedback(copyScriptBtn));
    });

    copyRomanBtn.addEventListener('click', () => {
        const text = romanOutput.textContent;
        if (!text || romanOutput.classList.contains('placeholder')) return;
        navigator.clipboard.writeText(text).then(() => showTemporaryFeedback(copyRomanBtn));
    });

    copyAllBtn.addEventListener('click', () => {
        const en = englishInput.value.trim();
        const bn = bengaliInput.value.trim();
        const script = scriptOutput.classList.contains('placeholder') ? '' : scriptOutput.textContent;
        const roman = romanOutput.classList.contains('placeholder') ? '' : romanOutput.textContent;
        const gloss = glossOutput.textContent === '\u2014' ? '' : glossOutput.textContent;
        const notes = notesOutput.textContent === '\u2014' ? '' : notesOutput.textContent;

        if (!roman && !script) return;

        const compiled = [
            `English:     ${en}`,
            `Bengali:     ${bn}`,
            `Toto Script: ${script}`,
            `Romanized:   ${roman}`,
            `Gloss:       ${gloss}`,
            `Notes:       ${notes}`
        ].filter(Boolean).join('\n');

        navigator.clipboard.writeText(compiled).then(() => showTemporaryFeedback(copyAllBtn));
    });
});
