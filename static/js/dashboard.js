// ============================================================
// REFLEX — AI EMERGENCY RESPONSE DASHBOARD
// ============================================================


// ============================================================
// MAP INITIALIZATION
// ============================================================

const map = L.map("map").setView(
    [28.6139, 77.2090],
    11
);


L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution:
            "&copy; OpenStreetMap contributors"
    }
).addTo(map);


let mapMarkers = [];


// ============================================================
// CLEAR MAP
// ============================================================

function clearMap() {

    mapMarkers.forEach(
        marker => {

            map.removeLayer(
                marker
            );

        }
    );

    mapMarkers = [];

}


// ============================================================
// CONNECTION
// ============================================================

const connectionStatus =
    document.getElementById(
        "connection-status"
    );


const socket = io();


socket.on(
    "connect",
    function () {

        console.log(
            "REFLEX Socket.IO connected"
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
            "REFLEX Socket.IO disconnected"
        );


        connectionStatus.textContent =
            "● Disconnected";


        connectionStatus.className =
            "disconnected";

    }
);


// ============================================================
// PULSE ANIMATION
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
// GET VEHICLE COUNT
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


    if (
        detection.num_objects !== undefined
    ) {

        return detection.num_objects;

    }


    return 0;

}


// ============================================================
// GET CONFIDENCE
// ============================================================

function getConfidence(
    payload
) {

    const detection =
        payload.detection || {};


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


    const severity =
        payload.severity || {};


    if (
        severity.score !== undefined
    ) {

        return severity.score;

    }


    return 0;

}


// ============================================================
// UPDATE BASIC STATS
// ============================================================

function updateStats(
    payload
) {

    const detection =
        payload.detection || {};


    const severity =
        payload.severity || {};


    const detected =
        detection.event_detected === true;


    const status =
        document.getElementById(
            "incident-status"
        );


    const severityValue =
        document.getElementById(
            "severity-value"
        );


    const confidenceValue =
        document.getElementById(
            "confidence-value"
        );


    const vehiclesValue =
        document.getElementById(
            "vehicles-value"
        );


    if (!detected) {

        status.textContent =
            "CLEAR";


        severityValue.textContent =
            "NONE";


        confidenceValue.textContent =
            "0%";


        vehiclesValue.textContent =
            "0";


        return;

    }


    status.textContent =
        "🚨 ACCIDENT";


    severityValue.textContent =
        severity.severity ||
        "UNKNOWN";


    confidenceValue.textContent =
        `${getConfidence(payload)}%`;


    vehiclesValue.textContent =
        getVehicleCount(
            detection
        );


    // Severity display

    if (
        severity.severity === "CRITICAL"
    ) {

        severityValue.style.color =
            "#ff4d4d";

    }

    else if (
        severity.severity === "MEDIUM"
    ) {

        severityValue.style.color =
            "#fbbf24";

    }

    else {

        severityValue.style.color =
            "#22c55e";

    }

}


// ============================================================
// UPDATE DISPATCH
// ============================================================

function updateDispatch(
    payload
) {

    const dispatch =
        payload.dispatch || {};


    const ambulance =
        dispatch.ambulance;


    const hospital =
        dispatch.hospital;


    // ========================================================
    // AMBULANCE
    // ========================================================

    if (ambulance) {

        document.getElementById(
            "ambulance-name"
        ).textContent =

            `${ambulance.name || "Ambulance"} (${ambulance.id || "—"})`;


        document.getElementById(
            "ambulance-distance"
        ).textContent =

            `Distance: ${ambulance.distance_km ?? "—"} km`;


        document.getElementById(
            "ambulance-eta"
        ).textContent =

            `ETA: ${ambulance.eta_minutes ?? "—"} min`;


        document.getElementById(
            "ambulance-status"
        ).textContent =

            "● DISPATCHED";


        document.getElementById(
            "ambulance-status"
        ).style.color =
            "#22c55e";

    }


    else {

        document.getElementById(
            "ambulance-name"
        ).textContent =
            "No ambulance available";


        document.getElementById(
            "ambulance-status"
        ).textContent =
            "● UNAVAILABLE";


        document.getElementById(
            "ambulance-status"
        ).style.color =
            "#ff4d4d";

    }


    // ========================================================
    // HOSPITAL
    // ========================================================

    if (hospital) {

        document.getElementById(
            "hospital-name"
        ).textContent =

            hospital.name ||
            "Hospital";


        document.getElementById(
            "hospital-distance"
        ).textContent =

            `Distance: ${hospital.distance_km ?? "—"} km`;


        document.getElementById(
            "hospital-eta"
        ).textContent =

            `ETA: ${hospital.eta_minutes ?? "—"} min`;


        document.getElementById(
            "hospital-status"
        ).textContent =

            "● ALERTED";


        document.getElementById(
            "hospital-status"
        ).style.color =
            "#22c55e";

    }


    else {

        document.getElementById(
            "hospital-name"
        ).textContent =
            "No hospital available";


        document.getElementById(
            "hospital-status"
        ).textContent =
            "● UNAVAILABLE";


        document.getElementById(
            "hospital-status"
        ).style.color =
            "#ff4d4d";

    }

}


// ============================================================
// UPDATE VIDEO STATUS
// ============================================================

function updateVideoStatus(
    payload
) {

    const detection =
        payload.detection || {};


    const videoStatus =
        document.getElementById(
            "video-status"
        );


    if (
        detection.event_detected
    ) {

        videoStatus.textContent =
            "🚨 ACCIDENT DETECTED";


        videoStatus.style.color =
            "#ff4d4d";

    }

    else {

        videoStatus.textContent =
            "● MONITORING";


        videoStatus.style.color =
            "#22c55e";

    }

}


// ============================================================
// UPDATE MAP
// ============================================================

function updateMap(
    payload
) {

    const location =
        payload.accident_location;


    if (!location) {

        return;

    }


    clearMap();


    // ========================================================
    // ACCIDENT
    // ========================================================

    const accidentMarker =
        L.marker(
            [
                location.lat,
                location.lng
            ]
        )
        .addTo(map)
        .bindPopup(
            "🚨 Accident location"
        )
        .openPopup();


    mapMarkers.push(
        accidentMarker
    );


    const dispatch =
        payload.dispatch || {};


    const ambulance =
        dispatch.ambulance;


    const hospital =
        dispatch.hospital;


    const points = [

        [
            location.lat,
            location.lng
        ]

    ];


    // ========================================================
    // AMBULANCE
    // ========================================================

    if (
        ambulance &&
        ambulance.latitude !== undefined &&
        ambulance.longitude !== undefined
    ) {

        const ambulanceMarker =
            L.marker(
                [
                    ambulance.latitude,
                    ambulance.longitude
                ]
            )
            .addTo(map)
            .bindPopup(
                `🚑 ${ambulance.name || "Ambulance"}`
            );


        mapMarkers.push(
            ambulanceMarker
        );


        points.push(

            [
                ambulance.latitude,
                ambulance.longitude
            ]

        );

    }


    // ========================================================
    // HOSPITAL
    // ========================================================

    if (
        hospital &&
        hospital.latitude !== undefined &&
        hospital.longitude !== undefined
    ) {

        const hospitalMarker =
            L.marker(
                [
                    hospital.latitude,
                    hospital.longitude
                ]
            )
            .addTo(map)
            .bindPopup(
                `🏥 ${hospital.name || "Hospital"}`
            );


        mapMarkers.push(
            hospitalMarker
        );


        points.push(

            [
                hospital.latitude,
                hospital.longitude
            ]

        );

    }


    // ========================================================
    // FIT MAP
    // ========================================================

    if (
        points.length > 1
    ) {

        map.fitBounds(
            points,
            {
                padding: [
                    60,
                    60
                ]
            }
        );

    }

    else {

        map.setView(
            [
                location.lat,
                location.lng
            ],
            14
        );

    }

}


// ============================================================
// INCIDENT CARD
// ============================================================

function renderIncident(
    payload
) {

    const container =
        document.getElementById(
            "cases"
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


    const severityName =
        severity.severity ||
        "LOW";


    card.className =
        `case-card ${severityName}`;


    let html = `

        <div class="case-row">

            <strong>
                🚨 Accident Detected
            </strong>

            <span class="badge ${severityName}">
                ${severityName}
            </span>

        </div>


        <div class="case-detail">

            <b>Score:</b>
            ${severity.score ?? 0}/100

        </div>


        <div class="case-detail">

            <b>Confidence:</b>
            ${getConfidence(payload)}%

        </div>


        <div class="case-detail">

            <b>Vehicles:</b>
            ${getVehicleCount(detection)}

        </div>


        <div class="case-detail">

            <b>Event:</b>
            ${detection.event_time_sec ?? "—"} sec

        </div>


        <div class="case-detail">

            <b>Reason:</b>
            ${detection.reason || "—"}

        </div>

    `;


    if (ambulance) {

        html += `

            <div class="case-detail">

                <b>🚑 Ambulance:</b>
                ${ambulance.name || "—"}

            </div>


            <div class="case-detail">

                <b>Ambulance ETA:</b>
                ${ambulance.eta_minutes ?? "—"} min

            </div>

        `;

    }


    if (hospital) {

        html += `

            <div class="case-detail">

                <b>🏥 Hospital:</b>
                ${hospital.name || "—"}

            </div>

        `;

    }


    card.innerHTML =
        html;


    container.prepend(
        card
    );

}


// ============================================================
// COMPLETE INCIDENT UPDATE
// ============================================================

function processIncident(
    payload
) {

    console.log(
        "=========================================="
    );


    console.log(
        "REFLEX INCIDENT RECEIVED"
    );


    console.log(
        payload
    );


    console.log(
        "=========================================="
    );


    firePulse();


    updateStats(
        payload
    );


    updateDispatch(
        payload
    );


    updateVideoStatus(
        payload
    );


    updateMap(
        payload
    );


    renderIncident(
        payload
    );

}


// ============================================================
// SOCKET.IO INCIDENT
// ============================================================

socket.on(
    "new_incident",
    function (payload) {

        processIncident(
            payload
        );

    }
);


// ============================================================
// TRIGGER BUTTON
// ============================================================

const triggerButton =
    document.getElementById(
        "trigger-btn"
    );


triggerButton.addEventListener(
    "click",
    async function () {


        const clip =
            document.getElementById(
                "clipName"
            ).value.trim();


        const lat =
            document.getElementById(
                "lat"
            ).value.trim();


        const lng =
            document.getElementById(
                "lng"
            ).value.trim();


        if (!clip) {

            alert(
                "Please enter a video filename."
            );

            return;

        }


        if (!lat || !lng) {

            alert(
                "Please enter accident coordinates."
            );

            return;

        }


        // ====================================================
        // START
        // ====================================================

        triggerButton.disabled =
            true;


        triggerButton.textContent =
            "🤖 AI ANALYZING...";


        const video =
            document.getElementById(
                "incident-video"
            );


        // Start video from beginning

        if (video) {

            video.currentTime =
                0;

            video.play().catch(
                function () {}
            );

        }


        try {


            const url =

                `/api/accidents/simulate/${encodeURIComponent(clip)}` +

                `?lat=${encodeURIComponent(lat)}` +

                `&lng=${encodeURIComponent(lng)}`;


            console.log(
                "Sending request:",
                url
            );


            const response =
                await fetch(
                    url,
                    {
                        method: "POST"
                    }
                );


            if (!response.ok) {

                let errorMessage =
                    "Backend request failed";


                try {

                    const error =
                        await response.json();


                    errorMessage =
                        error.error ||
                        errorMessage;

                }

                catch (e) {

                    // Ignore JSON parsing error

                }


                throw new Error(
                    errorMessage
                );

            }


            const payload =
                await response.json();


            console.log(
                "REFLEX API RESPONSE:",
                payload
            );


            // Socket.IO normally handles this.
            // This fallback handles the result if
            // Socket.IO event arrives slightly later.

            setTimeout(
                function () {

                    processIncident(
                        payload
                    );

                },
                300
            );

        }

        catch (error) {

            console.error(
                "REFLEX ERROR:",
                error
            );


            alert(
                "REFLEX ERROR: " +
                error.message
            );

        }

        finally {


            triggerButton.disabled =
                false;


            triggerButton.textContent =
                "Trigger Accident";

        }

    }
);


// ============================================================
// VIDEO LOAD CHECK
// ============================================================

const video =
    document.getElementById(
        "incident-video"
    );


if (video) {


    video.addEventListener(
        "loadedmetadata",
        function () {

            console.log(
                "REFLEX video loaded:",
                video.duration,
                "seconds"
            );

        }
    );


    video.addEventListener(
        "error",
        function () {

            console.error(
                "Could not load traffic.mp4"
            );

        }
    );

}