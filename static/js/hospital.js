// ============================================================
// REFLEX — HOSPITAL EMERGENCY CONSOLE
// ============================================================


// ============================================================
// SOCKET.IO CONNECTION
// ============================================================

const socket = io();
let activeIncidentId = null;


const connectionStatus =
    document.getElementById(
        "connection-status"
    );


socket.on(
    "connect",
    function () {

        console.log(
            "REFLEX Hospital Socket.IO connected"
        );


        connectionStatus.innerHTML =
            '<span class="live-dot"></span>LIVE';


        connectionStatus.className =
            'connected';

    }
);


socket.on(
    "disconnect",
    function () {

        console.log(
            "REFLEX Hospital Socket.IO disconnected"
        );


        connectionStatus.innerHTML =
            '<span class="live-dot"></span>OFFLINE';


        connectionStatus.className =
            'disconnected';

    }
);


// ============================================================
// PULSE
// ============================================================

function firePulse() {

    const pulse =
        document.getElementById(
            "pulse-path"
        );


    if (!pulse) {

        return;

    }


    pulse.setAttribute(
        'd',
        'M0,18 L30,18 L44,4 L58,32 L72,18 L100,18 L114,7 L128,29 L142,18 L300,18'
    );


    setTimeout(
        function () {

            pulse.setAttribute(
                'd',
                'M0,18 L300,18'
            );

        },
        900
    );

}


// ============================================================
// VEHICLE COUNT
// ============================================================

function getVehicleCount(
    detection
) {

    if (
        detection.vehicles_involved !== undefined
    ) {

        return detection.vehicles_involved;

    }


    if (
        detection.num_objects_at_event !== undefined
    ) {

        return detection.num_objects_at_event;

    }


    return 0;

}


// ============================================================
// CONFIDENCE
// ============================================================

function getConfidence(
    payload
) {

    const detection =
        payload.detection || {};


    const severity =
        payload.severity || {};


    if (
        detection.confidence !== undefined
    ) {

        return detection.confidence;

    }


    if (
        payload.confidence !== undefined
    ) {

        return payload.confidence;

    }


    // Fallback for current prototype

    if (
        severity.score !== undefined
    ) {

        return severity.score;

    }


    return 0;

}


// ============================================================
// TIMELINE AND STATUS CONTROL
// ============================================================

function updateTimelineStatus(status) {
    const stepDetected = document.getElementById("step-detected");
    const stepNotified = document.getElementById("step-notified");
    const stepAcknowledged = document.getElementById("step-acknowledged");
    const line1 = document.getElementById("line-1");
    const line2 = document.getElementById("line-2");
    const statusValue = document.getElementById("incident-status");

    if (!stepDetected || !stepNotified || !stepAcknowledged) return;

    // Reset styles
    [stepDetected, stepNotified, stepAcknowledged].forEach(step => {
        step.classList.remove("active", "completed");
    });
    [line1, line2].forEach(line => {
        line.classList.remove("active", "completed");
    });

    if (status === "DETECTED") {
        stepDetected.classList.add("active");
        statusValue.textContent = "🚨 DETECTED";
        statusValue.className = "stat-value red";
    } else if (status === "NOTIFIED") {
        stepDetected.classList.add("completed");
        line1.classList.add("active");
        stepNotified.classList.add("active");
        statusValue.textContent = "📢 NOTIFIED";
        statusValue.className = "stat-value yellow";
    } else if (status === "ACKNOWLEDGED") {
        stepDetected.classList.add("completed");
        line1.classList.add("completed");
        stepNotified.classList.add("completed");
        line2.classList.add("completed");
        stepAcknowledged.classList.add("completed");
        statusValue.textContent = "✓ ACKNOWLEDGED";
        statusValue.className = "stat-value green";

        // Style Acknowledge Button
        const ackBtn = document.getElementById("acknowledge-btn");
        if (ackBtn) {
            ackBtn.disabled = true;
            ackBtn.classList.add("acknowledged");
            ackBtn.textContent = "✓ ACKNOWLEDGED";
        }
    }
}


// ============================================================
// SHOW EMERGENCY
// ============================================================

function showEmergency(
    payload
) {

    console.log(
        "=========================================="
    );


    console.log(
        "🏥 REFLEX HOSPITAL ALERT"
    );


    console.log(
        payload
    );


    console.log(
        "=========================================="
    );


    const detection =
        payload.detection || {};


    const severity =
        payload.severity || {};


    const dispatch =
        payload.dispatch || {};


    const ambulance =
        dispatch.ambulance;


    const hospital =
        dispatch.hospital;


    // ========================================================
    // STORE ACTIVE INCIDENT ID
    // ========================================================
    activeIncidentId = payload.incident_id;


    // ========================================================
    // SHOW ACTIVE CASE
    // ========================================================

    document.getElementById(
        "waiting-screen"
    ).style.display =
        "none";


    document.getElementById(
        "active-case"
    ).style.display =
        "block";


    // ========================================================
    // EMERGENCY ALERT
    // ========================================================

    const alert =
        document.getElementById(
            "emergency-alert"
        );


    alert.classList.add(
        "show"
    );


    // ========================================================
    // SEVERITY
    // ========================================================

    const severityBadge =
        document.getElementById(
            "severity-badge"
        );


    const severityName =
        severity.severity ||
        "UNKNOWN";


    severityBadge.textContent =
        severityName;


    severityBadge.className =
        severityName;


    // ========================================================
    // INITIAL DETECTED TIMELINE & INCIDENT METADATA
    // ========================================================
    updateTimelineStatus("DETECTED");

    document.getElementById("case-incident-id").textContent = payload.incident_id || "—";

    // Format Timestamp
    const formattedTimestamp = payload.timestamp 
        ? new Date(payload.timestamp).toLocaleString() 
        : new Date().toLocaleString();
    document.getElementById("case-timestamp").textContent = `Timestamp: ${formattedTimestamp}`;

    // Render Evidence image
    const img = document.getElementById("case-evidence-img");
    const noImg = document.getElementById("case-no-evidence");
    if (payload.evidence_image_path) {
        img.src = "/" + payload.evidence_image_path + "?t=" + Date.now();
        img.style.display = "block";
        noImg.style.display = "none";
    } else {
        img.style.display = "none";
        noImg.style.display = "block";
    }

    // Reset Acknowledge and Prepare buttons for the new case
    const ackBtn = document.getElementById("acknowledge-btn");
    if (ackBtn) {
        ackBtn.disabled = false;
        ackBtn.classList.remove("acknowledged");
        ackBtn.textContent = "ACKNOWLEDGE CASE";
    }

    const prepBtn = document.getElementById("prepare-btn");
    if (prepBtn) {
        prepBtn.disabled = false;
        prepBtn.textContent = "🏥 Prepare Team";
        prepBtn.style.background = "";
    }

    // ========================================================
    // STATUS
    // ========================================================

    document.getElementById(
        "incident-status"
    ).textContent =
        "🚨 DETECTED";


    // ========================================================
    // CONFIDENCE
    // ========================================================

    document.getElementById(
        "confidence"
    ).textContent =
        `${getConfidence(payload)}%`;


    // ========================================================
    // VEHICLES
    // ========================================================

    document.getElementById(
        "vehicles"
    ).textContent =
        getVehicleCount(
            detection
        );


    // ========================================================
    // SEVERITY SCORE
    // ========================================================

    document.getElementById(
        "severity-score"
    ).textContent =
        `${severity.score ?? 0}/100`;


    // ========================================================
    // LOCATION
    // ========================================================

    const location =
        payload.accident_location;


    if (location) {

        document.getElementById(
            "location-value"
        ).textContent =

            `${location.lat}, ${location.lng}`;

    }


    // ========================================================
    // EVENT TIME
    // ========================================================

    document.getElementById(
        "event-time"
    ).textContent =

        `Event time: ${
            detection.event_time_sec ?? "—"
        } sec`;


    // ========================================================
    // REASON
    // ========================================================

    document.getElementById(
        "reason"
    ).textContent =

        `Reason: ${
            detection.reason || "—"
        }`;


    // ========================================================
    // AMBULANCE
    // ========================================================

    if (ambulance) {

        document.getElementById(
            "ambulance-name"
        ).textContent =

            `${ambulance.name || "Ambulance"} (${ambulance.id || "—"})`;


        document.getElementById(
            "ambulance-status"
        ).innerHTML =

            "Status: <span class='green'>● DISPATCHED</span>";


        document.getElementById(
            "ambulance-distance"
        ).textContent =

            `Distance: ${
                ambulance.distance_km ?? "—"
            } km`;


        document.getElementById(
            "ambulance-eta"
        ).innerHTML =

            `ETA: <span class='yellow'>${
                ambulance.eta_minutes ?? "—"
            } min</span>`;

    }

    else {

        document.getElementById(
            "ambulance-name"
        ).textContent =
            "No ambulance available";


        document.getElementById(
            "ambulance-status"
        ).innerHTML =

            "Status: <span class='red'>UNAVAILABLE</span>";

    }


    // ========================================================
    // HOSPITAL CAPACITY
    // ========================================================

    if (hospital) {

        document.getElementById(
            "capacity-number"
        ).textContent =

            hospital.emergency_capacity ??
            "—";


        document.getElementById(
            "hospital-status"
        ).innerHTML =

            "Status: <span class='green'>● READY</span>";

    }


    // ========================================================
    // UPDATE ALERT MESSAGE
    // ========================================================

    let message =

        "Emergency incident detected.";


    if (ambulance) {

        message +=

            ` Ambulance ${
                ambulance.id || ""
            } is on the way.`;

    }


    if (
        ambulance &&
        ambulance.eta_minutes !== undefined
    ) {

        message +=

            ` ETA: ${
                ambulance.eta_minutes
            } minutes.`;

    }


    document.getElementById(
        "alert-message"
    ).textContent =
        message;


    // ========================================================
    // HOSPITAL MATCH
    // ========================================================

    if (hospital) {

        const selectedHospital =
            hospital.name || "";


        if (
            selectedHospital.toLowerCase()
                .includes(
                    "hospital a"
                )
        ) {

            document.getElementById(
                "hospital-name"
            ).textContent =
                `🏥 ${selectedHospital}`;

        }

    }


    // ========================================================
    // RESPONSE STATUS
    // ========================================================

    document.getElementById(
        "response-status"
    ).textContent =

        "Incoming patient detected. Hospital team should prepare.";


    // ========================================================
    // NOTIFY BACKEND AUTOMATICALLY (DETECTED -> NOTIFIED)
    // ========================================================
    if (payload.incident_id) {
        fetch("/api/accidents/notify/" + encodeURIComponent(payload.incident_id), { method: "POST" })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.status === "NOTIFIED" && activeIncidentId === payload.incident_id) {
                    updateTimelineStatus("NOTIFIED");
                }
            })
            .catch(err => console.error("Error notifying backend:", err));
    }

}


// ============================================================
// INCIDENT HISTORY
// ============================================================

function addHistory(
    payload
) {

    const container =
        document.getElementById(
            "hospital-cases"
        );


    const empty =
        container.querySelector(
            ".empty-state"
        );


    if (empty) {

        empty.remove();

    }


    const detection =
        payload.detection || {};


    const severity =
        payload.severity || {};


    const dispatch =
        payload.dispatch || {};


    const ambulance =
        dispatch.ambulance;


    const hospital =
        dispatch.hospital;


    const card =
        document.createElement(
            "div"
        );


    const severityName = severity.severity || 'LOW';


    card.className =
        `history-card ${severityName}`;


    const time =
        payload.timestamp
            ?

        new Date(
            payload.timestamp
        ).toLocaleTimeString()

            :

        new Date()
            .toLocaleTimeString();


    card.innerHTML = `

        <div class="history-top">

            <strong style="font-size:12px;color:#eaf0f8;">🚨 Emergency Incident</strong>

            <div style="display:flex;align-items:center;gap:8px;">
                <span class="history-badge ${severityName}">${severityName}</span>
                <span class="history-time">${time}</span>
            </div>

        </div>


        <div class="history-detail">Severity: <b>${severity.severity || '—'}</b> &nbsp;·&nbsp; Score: <b>${severity.score ?? 0}/100</b></div>
        <div class="history-detail">Vehicles: <b>${getVehicleCount(detection)}</b> &nbsp;·&nbsp; Confidence: <b>${getConfidence(payload)}%</b></div>
        <div class="history-detail">Ambulance: <b>${ambulance ? (ambulance.name || ambulance.id) : '—'}</b>${ambulance && ambulance.eta_minutes !== undefined ? ` &nbsp;·&nbsp; ETA: <b>${ambulance.eta_minutes} min</b>` : ''}</div>
        <div class="history-detail">Hospital: <b>${hospital ? hospital.name : '—'}</b></div>

    `;


    container.prepend(
        card
    );

}


// ============================================================
// SOCKET.IO NEW INCIDENT
// ============================================================

socket.on(
    "new_incident",
    function (payload) {

        // Only handle actual accidents

        if (
            !payload.detection ||
            !payload.detection.event_detected
        ) {

            return;

        }


        firePulse();


        showEmergency(
            payload
        );


        addHistory(
            payload
        );


        // Browser notification sound

        try {

            const audioContext =
                new (
                    window.AudioContext ||
                    window.webkitAudioContext
                )();


            const oscillator =
                audioContext.createOscillator();


            const gain =
                audioContext.createGain();


            oscillator.connect(
                gain
            );


            gain.connect(
                audioContext.destination
            );


            oscillator.frequency.value =
                880;


            gain.gain.value =
                0.05;


            oscillator.start();


            oscillator.stop(
                audioContext.currentTime +
                0.25
            );

        }

        catch (error) {

            console.log(
                "Alert sound unavailable"
            );

        }

    }
);


// ============================================================
// SOCKET.IO STATUS CHANGE
// ============================================================

socket.on(
    "incident_status_change",
    function (data) {
        console.log("📡 Incident status change broadcast received:", data);
        if (data.incident_id === activeIncidentId) {
            updateTimelineStatus(data.status);
            
            const responseStatus = document.getElementById("response-status");
            if (data.status === "ACKNOWLEDGED" && responseStatus) {
                responseStatus.innerHTML = '<span style="color:var(--low,#22d47a);font-weight:600;">✓ Incident acknowledged. Emergency team notified.</span>';
            }
        }
    }
);


// ============================================================
// ACKNOWLEDGE BUTTON
// ============================================================

document
    .getElementById(
        "acknowledge-btn"
    )
    .addEventListener(
        "click",
        function () {

            if (!activeIncidentId) return;

            const status =
                document.getElementById(
                    "response-status"
                );

            const ackBtn = this;
            ackBtn.disabled = true;
            ackBtn.textContent = "ACKNOWLEDGING...";

            fetch("/api/accidents/acknowledge/" + encodeURIComponent(activeIncidentId), { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    if (data.success && activeIncidentId === data.incident_id) {
                        updateTimelineStatus("ACKNOWLEDGED");
                        status.innerHTML =
                            '<span style="color:var(--low,#22d47a);font-weight:600;">✓ Incident acknowledged. Emergency team notified.</span>';
                    }
                })
                .catch(err => {
                    console.error("Error acknowledging case:", err);
                    ackBtn.disabled = false;
                    ackBtn.textContent = "ACKNOWLEDGE CASE";
                });

        }
    );


// ============================================================
// PREPARE TEAM BUTTON
// ============================================================

document
    .getElementById(
        "prepare-btn"
    )
    .addEventListener(
        "click",
        function () {

            const status =
                document.getElementById(
                    "response-status"
                );


            status.innerHTML =
                '<span style="color:var(--low,#22d47a);font-weight:600;">🏥 Emergency team is prepared and ready for patient.</span>';


            this.textContent =
                '✓ TEAM READY';


            this.style.background =
                '#15803d';

        }
    );