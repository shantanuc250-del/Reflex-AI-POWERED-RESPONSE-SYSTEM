// ============================================================
// REFLEX — HOSPITAL EMERGENCY CONSOLE
// ============================================================


// ============================================================
// SOCKET.IO CONNECTION
// ============================================================

const socket = io();


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


        connectionStatus.textContent =
            "● Connected";


        connectionStatus.className =
            "connected";

    }
);


socket.on(
    "disconnect",
    function () {

        console.log(
            "REFLEX Hospital Socket.IO disconnected"
        );


        connectionStatus.textContent =
            "● Disconnected";


        connectionStatus.className =
            "disconnected";

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
        "d",
        "M0,20 L35,20 L50,5 L65,35 L80,20 L115,20 L130,8 L145,32 L160,20 L300,20"
    );


    setTimeout(
        function () {

            pulse.setAttribute(
                "d",
                "M0,20 L300,20"
            );

        },
        1000
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
    // STATUS
    // ========================================================

    document.getElementById(
        "incident-status"
    ).textContent =
        "🚨 INCOMING";


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


    card.className =
        "history-card";


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

            <strong>
                🚨 Emergency Incident
            </strong>

            <span class="history-time">
                ${time}
            </span>

        </div>


        <div class="history-detail">

            Severity:
            <b>
                ${severity.severity || "—"}
            </b>

        </div>


        <div class="history-detail">

            Vehicles:
            ${getVehicleCount(detection)}

        </div>


        <div class="history-detail">

            Ambulance:
            ${
                ambulance
                    ? ambulance.id
                    : "—"
            }

        </div>


        <div class="history-detail">

            Hospital:
            ${
                hospital
                    ? hospital.name
                    : "—"
            }

        </div>

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
// ACKNOWLEDGE BUTTON
// ============================================================

document
    .getElementById(
        "acknowledge-btn"
    )
    .addEventListener(
        "click",
        function () {

            const status =
                document.getElementById(
                    "response-status"
                );


            status.innerHTML =

                "<span class='green'>✓ INCIDENT ACKNOWLEDGED</span>";

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

                "<span class='green'>🏥 EMERGENCY TEAM PREPARED</span>";


            this.textContent =
                "✓ TEAM READY";


            this.style.background =
                "#15803d";

        }
    );