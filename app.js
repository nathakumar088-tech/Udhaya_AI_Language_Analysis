const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const fileName = document.getElementById("fileName");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultCard = document.getElementById("resultCard");
const result = document.getElementById("result");
const language = document.getElementById("language");


// ===============================
// FILE BROWSE
// ===============================

browseBtn.onclick = () => {
    fileInput.click();
};


fileInput.onchange = () => {
    showFile(fileInput.files[0]);
};


function showFile(file) {

    if (file) {
        fileName.textContent = "✓ " + file.name;
    }

}


// ===============================
// DRAG & DROP
// ===============================

["dragenter", "dragover"].forEach(eventName => {

    dropZone.addEventListener(eventName, event => {

        event.preventDefault();
        event.stopPropagation();

        dropZone.style.borderColor = "#6e63ff";

    });

});


["dragleave", "drop"].forEach(eventName => {

    dropZone.addEventListener(eventName, event => {

        event.preventDefault();
        event.stopPropagation();

        dropZone.style.borderColor = "#343c5e";

    });

});


dropZone.addEventListener("drop", event => {

    const files = event.dataTransfer.files;

    if (files.length > 0) {

        fileInput.files = files;

        showFile(files[0]);

    }

});


// ===============================
// ANALYZE BUTTON
// ===============================

analyzeBtn.onclick = async () => {

    const text =
        document.getElementById("textInput").value.trim();

    const file =
        fileInput.files[0];


    // Nothing entered
    if (!text && !file) {

        alert("Paste text or upload a file first.");

        return;
    }


    // Button loading state
    analyzeBtn.disabled = true;

    analyzeBtn.innerHTML =
        "✦ ANALYZING... <span class='arrow'>◌</span>";


    // Create FormData
    const formData = new FormData();

    formData.append(
        "text",
        text
    );

    formData.append(
        "output_language",
        language.value
    );


    if (file) {

        formData.append(
            "file",
            file
        );

    }


    try {

        const response = await fetch(
            "/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "AI request failed"
            );

        }


        // ==================================
        // SHOW TRANSLATION ON SCREEN
        // ==================================

        result.textContent =
            data.result;


        // ==================================
        // SAVE VOICE TEXT
        // ==================================
        //
        // For normal languages:
        // voice_text = translated text
        //
        // For Thanglish:
        // voice_text = Tamil-script version
        // used only for pronunciation.
        //

        window.currentVoiceText =
            data.voice_text ||
            data.result;


        // ==================================
        // SAVE VOICE LANGUAGE
        // ==================================

        window.currentVoiceLanguage =
            data.voice_language ||
            "en-IN";


        // ==================================
        // SHOW RESULT CARD
        // ==================================

        resultCard.classList.remove(
            "hidden"
        );


        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    }

    catch (error) {

        alert(
            error.message
        );

    }

    finally {

        // Restore button
        analyzeBtn.disabled = false;

        analyzeBtn.innerHTML =
            "✦ ANALYZE WITH AI <span class='arrow'>→</span>";

    }

};


// ===============================
// COPY BUTTON
// ===============================

document.getElementById("copyBtn").onclick =
    async () => {

        const text =
            result.textContent.trim();


        if (!text) {
            return;
        }


        try {

            await navigator.clipboard.writeText(
                text
            );


            const copyBtn =
                document.getElementById("copyBtn");


            copyBtn.textContent =
                "✓ Copied";


            setTimeout(() => {

                copyBtn.textContent =
                    "Copy";

            }, 1500);


        }

        catch (error) {

            alert(
                "Unable to copy the text."
            );

        }

    };


// ===============================
// TEXT TO SPEECH
// ===============================

document.getElementById("speakBtn").onclick =
    () => {

        // Use special voice text from backend
        // if available.

        const text = (
            window.currentVoiceText ||
            result.textContent
        ).trim();


        if (!text) {
            return;
        }


        // Stop previous speech
        speechSynthesis.cancel();


        // Create speech object
        const utterance =
            new SpeechSynthesisUtterance(
                text
            );


        // Language selected by backend
        //
        // Thanglish:
        // backend sends Tamil script
        // + ta-IN voice
        //
        // English:
        // en-IN
        //
        // Hindi:
        // hi-IN
        //

        utterance.lang =
            window.currentVoiceLanguage ||
            "en-IN";


        // Get available browser voices
        const voices =
            speechSynthesis.getVoices();


        // Find exact language voice
        const exactVoice =
            voices.find(
                voice =>
                    voice.lang.toLowerCase() ===
                    utterance.lang.toLowerCase()
            );


        // If exact voice not available,
        // find same language family.

        const languageCode =
            utterance.lang
                .split("-")[0]
                .toLowerCase();


        const sameLanguageVoice =
            voices.find(
                voice =>
                    voice.lang
                        .toLowerCase()
                        .startsWith(
                            languageCode
                        )
            );


        if (exactVoice) {

            utterance.voice =
                exactVoice;

        }

        else if (sameLanguageVoice) {

            utterance.voice =
                sameLanguageVoice;

        }


        // Speech settings
        utterance.rate = 0.78;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;


        // Speak
        speechSynthesis.speak(
            utterance
        );

    };


// ===============================
// LOAD VOICES
// ===============================
//
// Some browsers load voices only
// after speechSynthesis starts.
//

speechSynthesis.onvoiceschanged = () => {

    speechSynthesis.getVoices();

};