(function() {
    let data = [];
    let foundQASession = false;
    let lastSpeaker = null;
    let lastRole = "operator";
    let lastPosition = null;
    let companyParticipants = {};
    let callParticipants = {};

    // Step 1: Extract Company and Call Participants
    let participantSection = "";
    document.querySelectorAll("p").forEach(p => {
        let strongElement = p.querySelector("strong");
        if (strongElement) {
            let title = strongElement.textContent.trim();
            if (title.includes("Company Participants")) {
                participantSection = "company";
            } else if (title.includes("Conference Call Participants")) {
                participantSection = "call";
            } else {
                participantSection = "";
            }
        }

        if (participantSection && !p.querySelector("strong")) {
            let lines = p.innerHTML.split("<br>").map(line => line.replace(/["']/g, "").trim());
            lines.forEach(line => {
                if (line) {
                    let parts = line.split(" - "); // Adjusted for standard hyphen separator
                    let name = parts[0].trim();
                    let position = parts.length > 1 ? parts[1].trim() : null;

                    // Normalize the name for consistent lookup
                    let normalizedName = name.toLowerCase();

                    if (participantSection === "company") {
                        companyParticipants[normalizedName] = position || "Unknown";
                    } else if (participantSection === "call") {
                        callParticipants[normalizedName] = position || "Unknown";
                    }
                }
            });
        }
    });

    // Step 2: Extract Q&A with Correct Role and Position
    document.querySelectorAll("p").forEach(p => {
        if (!foundQASession) {
            if (p.querySelector("strong") && p.querySelector("strong").textContent.toLowerCase().includes("question-and-qnswer session")) {
                foundQASession = true;
            }
            else if (p.textContent. toLowerCase().includes("question-and-answer session") ){
                foundQASession = true;
            }
            return;
        }

        let speaker = null;
        let role = "operator";
        let position = "Unknown";
        let strongElement = p.querySelector("strong");

        if (strongElement) {
            let span = strongElement.querySelector("span");
            if (span) {
                speaker = span.textContent.trim();

                // Assign role from class
                if (span.classList.contains("question")) {
                    role = "questioner";
                } else if (span.classList.contains("answer")) {
                    role = "answerer";
                }
            } else {
                speaker = strongElement.textContent.trim();
            }

            // Normalize speaker name for lookup
            let normalizedSpeaker = speaker.toLowerCase();

            // Check predefined participants for role and position
            if (companyParticipants[normalizedSpeaker]) {
                role = "answerer";
                position = companyParticipants[normalizedSpeaker];
            } else if (callParticipants[normalizedSpeaker]) {
                role = "questioner";
                position = callParticipants[normalizedSpeaker];
            }

            lastSpeaker = speaker;
            lastRole = role;
            lastPosition = position;
        }

        // Extract text content
        let textContent = p.textContent.trim();
        if (strongElement) {
            textContent = textContent.replace(strongElement.textContent, "").trim();
        }

        if (!speaker) {
            speaker = lastSpeaker || "Unknown";
            role = lastRole;
            position = lastPosition;
        }

        if (textContent) {
            data.push({
                person: speaker,
                role: role,
                position: position,
                text: textContent
            });
        }
    });

    console.log(JSON.stringify(data, null, 2));
})();
