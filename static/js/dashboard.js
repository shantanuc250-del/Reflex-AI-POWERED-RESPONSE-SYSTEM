// ============================================================
// REFLEX — AI EMERGENCY RESPONSE DASHBOARD
// ============================================================


// ============================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================

function showToast(message, type, duration) {

    type     = type     || 'info';
    duration = duration || 4500;

    var container = document.getElementById('toast-container');

    if (!container) {
        return;
    }

    var icons = {
        info:    '📡',
        success: '✅',
        error:   '🚨',
        warning: '⚠️'
    };

    var borderColour =
        type === 'error'   ? 'rgba(255,61,71,0.4)'   :
        type === 'success' ? 'rgba(34,212,122,0.4)'  :
                             'rgba(59,158,255,0.25)';

    var toast = document.createElement('div');
    toast.style.cssText = [
        'display:flex',
        'align-items:center',
        'gap:12px',
        'padding:14px 18px',
        'background:rgba(11,21,34,0.90)',
        'backdrop-filter:blur(16px)',
        '-webkit-backdrop-filter:blur(16px)',
        'border:1px solid ' + borderColour,
        'border-radius:10px',
        'font-size:13px',
        'color:#eaf0f8',
        "font-family:'Inter',sans-serif",
        'min-width:280px',
        'max-width:380px',
        'box-shadow:0 8px 32px rgba(0,0,0,0.5)',
        'pointer-events:all',
        'animation:toastIn 0.3s cubic-bezier(0.22,1,0.36,1) forwards'
    ].join(';');

    toast.innerHTML =
        '<span style="font-size:16px;flex-shrink:0;">' + (icons[type] || icons.info) + '</span>' +
        '<span style="flex:1;line-height:1.4;">' + message + '</span>' +
        '<button onclick="dismissToast(this.parentElement)" ' +
        'style="background:none;border:none;color:#5a7a9a;cursor:pointer;font-size:18px;' +
        'line-height:1;padding:0;transition:color 0.15s;" ' +
        'onmouseover="this.style.color=\'#eaf0f8\'" ' +
        'onmouseout="this.style.color=\'#5a7a9a\'">×</button>';

    container.appendChild(toast);

    setTimeout(function () {
        dismissToast(toast);
    }, duration);

}


function dismissToast(toast) {

    if (!toast || !toast.parentElement) {
        return;
    }

    toast.style.animation = 'toastOut 0.25s ease forwards';

    setTimeout(function () {
        if (toast.parentElement) {
            toast.parentElement.removeChild(toast);
        }
    }, 260);

}


// Inject keyframe styles for toasts
(function injectToastStyles() {
    var style = document.createElement('style');
    style.textContent =
        '@keyframes toastIn  { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:translateX(0)} }' +
        '@keyframes toastOut { from{opacity:1;transform:translateX(0)}    to{opacity:0;transform:translateX(20px)} }';
    document.head.appendChild(style);
})();


// ============================================================
// EVIDENCE MODAL SYSTEM
// ============================================================

var evidenceOverlay = document.getElementById('evidence-overlay');
var evidenceModal   = document.getElementById('evidence-modal');


// Open modal
function openEvidenceModal() {
    evidenceOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
}


// Close modal
function closeEvidenceModal() {
    evidenceOverlay.classList.remove('open');
    document.body.style.overflow = '';
}


// Populate + show modal for a given incident ID
function showEvidence(incidentId) {

    // Show loading state
    document.getElementById('modal-loading').style.display       = 'block';
    document.getElementById('evidence-frame-wrap').style.display = 'none';
    document.getElementById('evidence-metadata').style.display   = 'none';
    document.getElementById('modal-incident-id').textContent     = incidentId;
    document.getElementById('modal-severity-badge').textContent  = '…';
    document.getElementById('modal-severity-badge').className    = '';

    openEvidenceModal();

    fetch('/api/accidents/evidence/' + encodeURIComponent(incidentId))

        .then(function (res) {
            if (!res.ok) {
                throw new Error('Evidence record not found.');
            }
            return res.json();
        })

        .then(function (data) {
            populateEvidenceModal(data);
        })

        .catch(function (err) {
            closeEvidenceModal();
            showToast('Could not load evidence: ' + err.message, 'error');
        });

}


// Fill all modal fields from API response
function populateEvidenceModal(data) {

    // ---- Header ----
    var sev = data.severity || 'UNKNOWN';
    document.getElementById('modal-incident-id').textContent    = data.incident_id || '—';
    document.getElementById('modal-severity-badge').textContent = sev;
    document.getElementById('modal-severity-badge').className   = sev;

    // ---- Evidence image ----
    var img     = document.getElementById('modal-evidence-img');
    var noImg   = document.getElementById('modal-no-image');
    var imgWrap = document.getElementById('evidence-frame-wrap');

    if (data.evidence_image_path) {
        img.src = '/' + data.evidence_image_path + '?t=' + Date.now();
        img.style.display   = 'block';
        noImg.style.display = 'none';
    } else {
        img.style.display   = 'none';
        noImg.style.display = 'block';
    }

    // ---- Metadata fields ----
    function set(id, value) {
        var el = document.getElementById(id);
        if (el) {
            el.textContent = (value !== null && value !== undefined && value !== '') ? value : '—';
        }
    }

    var ts = data.timestamp
        ? new Date(data.timestamp).toLocaleString('en-US', {
            year:'numeric', month:'short', day:'2-digit',
            hour:'2-digit', minute:'2-digit', second:'2-digit',
            timeZoneName:'short'
          })
        : '—';

    set('meta-incident-id',   data.incident_id);
    set('meta-timestamp',     ts);
    set('meta-location',      data.lat && data.lng ? data.lat.toFixed(4) + ', ' + data.lng.toFixed(4) : '—');
    set('meta-severity',      sev);
    set('meta-score',         data.score !== null && data.score !== undefined ? data.score + '/100' : '—');
    set('meta-confidence',    data.confidence !== null ? data.confidence + '%' : '—');
    set('meta-vehicles',      data.vehicles_involved);
    set('meta-reason',        data.reason);
    set('meta-event-time',    data.event_time_sec !== null ? data.event_time_sec + 's' : '—');
    set('meta-event-frame',   data.event_frame !== null ? '#' + data.event_frame : '—');

    var ambText = data.ambulance_name || data.ambulance_id || '—';
    if (data.ambulance_eta) { ambText += ' · ETA ' + data.ambulance_eta + ' min'; }
    set('meta-ambulance', ambText);

    var hospText = data.hospital_name || '—';
    if (data.hospital_eta) { hospText += ' · ETA ' + data.hospital_eta + ' min'; }
    set('meta-hospital', hospText);

    set('meta-evidence-path', data.evidence_image_path || 'No frame captured');

    // Colour severity value
    var sevEl = document.getElementById('meta-severity');
    if (sevEl) {
        sevEl.className = 'meta-value ' +
            (sev === 'CRITICAL' ? 'red' : sev === 'MEDIUM' ? 'yellow' : 'green');
    }

    // ---- Hide loading, show content ----
    document.getElementById('modal-loading').style.display       = 'none';
    document.getElementById('evidence-frame-wrap').style.display = 'block';
    document.getElementById('evidence-metadata').style.display   = 'grid';

}


// Close button
document.getElementById('modal-close-btn').addEventListener('click', closeEvidenceModal);


// Click outside modal content to close
evidenceOverlay.addEventListener('click', function (e) {
    if (e.target === evidenceOverlay) {
        closeEvidenceModal();
    }
});


// ESC to close
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && evidenceOverlay.classList.contains('open')) {
        closeEvidenceModal();
    }
});


// ============================================================
// CUSTOM SVG MAP ICONS
// ============================================================

function makeSvgIcon(color, pulseColor) {

    var pulse = pulseColor ? (
        '<circle cx="20" cy="20" r="16" fill="' + pulseColor + '" opacity="0.18">' +
        '<animate attributeName="r" from="16" to="28" dur="2.5s" repeatCount="indefinite"/>' +
        '<animate attributeName="opacity" from="0.18" to="0" dur="2.5s" repeatCount="indefinite"/>' +
        '</circle>'
    ) : '';

    var svg =
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">' +
        pulse +
        '<circle cx="20" cy="20" r="13" fill="' + color + '" opacity="0.2"/>' +
        '<circle cx="20" cy="20" r="9" fill="' + color + '"/>' +
        '<circle cx="20" cy="20" r="5" fill="rgba(255,255,255,0.9)"/>' +
        '</svg>';

    return L.divIcon({
        html:       svg,
        className:  '',
        iconSize:   [40, 40],
        iconAnchor: [20, 20],
        popupAnchor:[0, -22]
    });

}


var ICONS = {
    accident:  makeSvgIcon('#ff3d47', '#ff3d47'),
    ambulance: makeSvgIcon('#22d47a', '#22d47a'),
    hospital:  makeSvgIcon('#3b9eff', '#3b9eff')
};


// ============================================================
// MAP INITIALIZATION
// ============================================================

var map = L.map('map', { zoomControl: false }).setView([28.6139, 77.2090], 11);

L.control.zoom({ position: 'bottomright' }).addTo(map);

L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains:  'abcd',
        maxZoom:     19
    }
).addTo(map);


var mapMarkers = [];


// ============================================================
// CLEAR MAP
// ============================================================

function clearMap() {
    mapMarkers.forEach(function (m) { map.removeLayer(m); });
    mapMarkers = [];
}


// ============================================================
// CONNECTION
// ============================================================

var connectionStatus = document.getElementById('connection-status');

var socket = io();


socket.on('connect', function () {
    console.log('REFLEX Socket.IO connected');
    connectionStatus.innerHTML = '<span class="live-dot"></span>LIVE';
    connectionStatus.className = 'connected';
    showToast('Connected to REFLEX command network.', 'success', 3000);
});


socket.on('disconnect', function () {
    console.log('REFLEX Socket.IO disconnected');
    connectionStatus.innerHTML = '<span class="live-dot"></span>OFFLINE';
    connectionStatus.className = 'disconnected';
    showToast('Connection lost. Attempting to reconnect...', 'error', 5000);
});


// ============================================================
// PULSE ANIMATION
// ============================================================

function firePulse(isCritical) {

    var pulse = document.getElementById('pulse-path');

    if (!pulse) { return; }

    if (isCritical) { pulse.style.stroke = '#ff3d47'; }

    pulse.setAttribute('d',
        'M0,18 L30,18 L44,4 L58,32 L72,18 L100,18 L114,7 L128,29 L142,18 L300,18'
    );

    setTimeout(function () {
        pulse.setAttribute('d', 'M0,18 L300,18');
        if (isCritical) {
            setTimeout(function () { pulse.style.stroke = ''; }, 600);
        }
    }, 900);

}


// ============================================================
// HELPERS
// ============================================================

function getVehicleCount(detection) {
    if (detection.vehicles_involved !== undefined) { return detection.vehicles_involved; }
    if (detection.num_objects_at_event !== undefined) { return detection.num_objects_at_event; }
    if (detection.num_objects !== undefined) { return detection.num_objects; }
    return 0;
}


function getConfidence(payload) {
    var detection = payload.detection || {};
    var severity  = payload.severity  || {};
    if (detection.confidence !== undefined) { return detection.confidence; }
    if (payload.confidence   !== undefined) { return payload.confidence;   }
    if (severity.score       !== undefined) { return severity.score;        }
    return 0;
}


// ============================================================
// INCIDENT COUNTER
// ============================================================

var incidentCount = 0;

function updateIncidentCount() {
    incidentCount++;
    var counter = document.getElementById('incident-count');
    if (counter) { counter.textContent = incidentCount; }
}


// ============================================================
// UPDATE STATS
// ============================================================

function updateStats(payload) {

    var detection = payload.detection || {};
    var severity  = payload.severity  || {};
    var detected  = detection.event_detected === true;

    var statusEl     = document.getElementById('incident-status');
    var severityEl   = document.getElementById('severity-value');
    var confidenceEl = document.getElementById('confidence-value');
    var vehiclesEl   = document.getElementById('vehicles-value');

    if (!detected) {
        if (statusEl)     { statusEl.textContent = 'CLEAR'; }
        if (severityEl)   { severityEl.textContent = 'NONE'; }
        if (confidenceEl) { confidenceEl.textContent = '0%'; }
        if (vehiclesEl)   { vehiclesEl.textContent = '0'; }
        return;
    }

    if (statusEl)     { statusEl.textContent = '🚨 ACCIDENT'; }
    if (vehiclesEl)   { vehiclesEl.textContent = getVehicleCount(detection); }
    if (confidenceEl) { confidenceEl.textContent = getConfidence(payload) + '%'; }

    var severityName = severity.severity || 'UNKNOWN';

    if (severityEl) {
        severityEl.textContent = severityName;
        severityEl.className = 'stat-value ' + severityName;
    }

}


// ============================================================
// UPDATE DISPATCH
// ============================================================

function updateDispatch(payload) {

    var dispatch  = payload.dispatch  || {};
    var ambulance = dispatch.ambulance;
    var hospital  = dispatch.hospital;

    if (ambulance) {
        var nameEl   = document.getElementById('ambulance-name');
        var distEl   = document.getElementById('ambulance-distance');
        var etaEl    = document.getElementById('ambulance-eta');
        var statusEl = document.getElementById('ambulance-status');
        if (nameEl)   { nameEl.textContent = (ambulance.name || 'Ambulance') + ' (' + (ambulance.id || '—') + ')'; }
        if (distEl)   { distEl.textContent = 'Distance: ' + (ambulance.distance_km !== undefined ? ambulance.distance_km : '—') + ' km'; }
        if (etaEl)    { etaEl.textContent  = 'ETA: ' + (ambulance.eta_minutes !== undefined ? ambulance.eta_minutes : '—') + ' min'; }
        if (statusEl) {
            statusEl.innerHTML = '<span style="width:5px;height:5px;border-radius:50%;background:currentColor;"></span> DISPATCHED';
            statusEl.className = 'dispatch-status dispatched';
        }
    } else {
        var nameEl2   = document.getElementById('ambulance-name');
        var statusEl2 = document.getElementById('ambulance-status');
        if (nameEl2)   { nameEl2.textContent = 'No ambulance available'; }
        if (statusEl2) {
            statusEl2.innerHTML = '<span style="width:5px;height:5px;border-radius:50%;background:currentColor;"></span> UNAVAILABLE';
            statusEl2.className = 'dispatch-status unavailable';
        }
    }

    if (hospital) {
        var hNameEl   = document.getElementById('hospital-name');
        var hDistEl   = document.getElementById('hospital-distance');
        var hEtaEl    = document.getElementById('hospital-eta');
        var hStatusEl = document.getElementById('hospital-status');
        if (hNameEl)   { hNameEl.textContent = hospital.name || 'Hospital'; }
        if (hDistEl)   { hDistEl.textContent = 'Distance: ' + (hospital.distance_km !== undefined ? hospital.distance_km : '—') + ' km'; }
        if (hEtaEl)    { hEtaEl.textContent  = 'ETA: ' + (hospital.eta_minutes !== undefined ? hospital.eta_minutes : '—') + ' min'; }
        if (hStatusEl) {
            hStatusEl.innerHTML = '<span style="width:5px;height:5px;border-radius:50%;background:currentColor;"></span> ALERTED';
            hStatusEl.className = 'dispatch-status alerted';
        }
    } else {
        var hNameEl2   = document.getElementById('hospital-name');
        var hStatusEl2 = document.getElementById('hospital-status');
        if (hNameEl2)   { hNameEl2.textContent = 'No hospital available'; }
        if (hStatusEl2) {
            hStatusEl2.innerHTML = '<span style="width:5px;height:5px;border-radius:50%;background:currentColor;"></span> UNAVAILABLE';
            hStatusEl2.className = 'dispatch-status unavailable';
        }
    }

}


// ============================================================
// UPDATE VIDEO STATUS
// ============================================================

function updateVideoStatus(payload) {

    var detection  = payload.detection  || {};
    var videoStatus = document.getElementById('video-status');

    if (!videoStatus) { return; }

    if (detection.event_detected) {
        videoStatus.innerHTML = '<span class="live-dot" style="background:currentColor;"></span>ACCIDENT DETECTED';
        videoStatus.className = 'alert';
    } else {
        videoStatus.innerHTML = '<span class="live-dot" style="background:currentColor;animation:livePulse 1.8s ease-in-out infinite;"></span>MONITORING';
        videoStatus.className = '';
    }

}


// ============================================================
// UPDATE MAP
// ============================================================

function updateMap(payload) {

    var location = payload.accident_location;

    if (!location) { return; }

    clearMap();

    var accidentMarker = L.marker(
        [location.lat, location.lng],
        { icon: ICONS.accident }
    )
    .addTo(map)
    .bindPopup(
        '<strong style="color:#ff3d47;">🚨 Accident</strong><br>' +
        '<span style="font-family:monospace;font-size:11px;">' +
        location.lat.toFixed(4) + ', ' + location.lng.toFixed(4) + '</span>'
    )
    .openPopup();

    mapMarkers.push(accidentMarker);

    var dispatch  = payload.dispatch  || {};
    var ambulance = dispatch.ambulance;
    var hospital  = dispatch.hospital;

    var points = [[location.lat, location.lng]];

    if (ambulance && ambulance.latitude !== undefined && ambulance.longitude !== undefined) {
        var ambMarker = L.marker(
            [ambulance.latitude, ambulance.longitude],
            { icon: ICONS.ambulance }
        )
        .addTo(map)
        .bindPopup(
            '<strong style="color:#22d47a;">🚑 ' + (ambulance.name || 'Ambulance') + '</strong><br>' +
            '<span style="font-family:monospace;font-size:11px;">ETA: ' +
            (ambulance.eta_minutes !== undefined ? ambulance.eta_minutes : '—') + ' min</span>'
        );
        mapMarkers.push(ambMarker);
        points.push([ambulance.latitude, ambulance.longitude]);
    }

    if (hospital && hospital.latitude !== undefined && hospital.longitude !== undefined) {
        var hospMarker = L.marker(
            [hospital.latitude, hospital.longitude],
            { icon: ICONS.hospital }
        )
        .addTo(map)
        .bindPopup(
            '<strong style="color:#3b9eff;">🏥 ' + (hospital.name || 'Hospital') + '</strong><br>' +
            '<span style="font-family:monospace;font-size:11px;">ETA: ' +
            (hospital.eta_minutes !== undefined ? hospital.eta_minutes : '—') + ' min</span>'
        );
        mapMarkers.push(hospMarker);
        points.push([hospital.latitude, hospital.longitude]);
    }

    if (points.length > 1) {
        map.fitBounds(points, { padding: [60, 60], animate: true });
    } else {
        map.flyTo([location.lat, location.lng], 14, { animate: true, duration: 1 });
    }

}


// ============================================================
// RENDER INCIDENT CARD  (with View Evidence button)
// ============================================================

function renderIncident(payload) {

    var container = document.getElementById('cases');
    var empty     = container.querySelector('.empty-state');

    if (empty) { empty.remove(); }

    var detection    = payload.detection || {};
    var severity     = payload.severity  || {};
    var dispatch     = payload.dispatch  || {};
    var ambulance    = dispatch.ambulance;
    var hospital     = dispatch.hospital;
    var severityName = severity.severity || 'LOW';
    var incidentId   = payload.incident_id || null;

    var card = document.createElement('div');
    card.className = 'case-card ' + severityName;

    var now = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    });

    var html = '<div class="case-row">' +
        '<div class="case-title">' +
        '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" style="flex-shrink:0;">' +
        '<circle cx="5" cy="5" r="4" fill="currentColor" opacity="0.8"/></svg>' +
        ' Accident Detected</div>' +
        '<span class="badge ' + severityName + '">' + severityName + '</span>' +
        '</div>';

    // Incident ID chip
    if (incidentId) {
        html += '<div class="card-incident-id">' +
            '<svg width="8" height="8" viewBox="0 0 8 8" fill="none"><circle cx="4" cy="4" r="3" fill="#3b9eff" opacity="0.7"/></svg>' +
            incidentId +
            '</div>';
    }

    html += '<div class="case-meta">' +
        '<div class="case-detail"><b>Score</b> ' + (severity.score !== undefined ? severity.score : 0) + '/100</div>' +
        '<div class="case-detail"><b>Confidence</b> ' + getConfidence(payload) + '%</div>' +
        '<div class="case-detail"><b>Vehicles</b> ' + getVehicleCount(detection) + '</div>' +
        '<div class="case-detail"><b>At</b> ' + (detection.event_time_sec !== undefined ? detection.event_time_sec : '—') + 's</div>' +
        '</div>';

    if (detection.reason) {
        html += '<div class="case-detail" style="margin-top:6px;"><b>Reason</b> ' + detection.reason + '</div>';
    }

    if (ambulance) {
        html += '<div class="case-detail"><b>Ambulance</b> ' +
            (ambulance.name || '—') + ' · ' +
            (ambulance.eta_minutes !== undefined ? ambulance.eta_minutes : '—') + ' min</div>';
    }

    if (hospital) {
        html += '<div class="case-detail"><b>Hospital</b> ' + (hospital.name || '—') + '</div>';
    }

    html += '<div class="case-timestamp">⏱ ' + now + '</div>';

    // View Evidence button — only if an incident ID exists
    if (incidentId) {
        html += '<button class="evidence-btn" ' +
            'data-incident-id="' + incidentId + '" ' +
            'onclick="showEvidence(\'' + incidentId + '\')">' +
            '🔍 View Evidence' +
            '</button>';
    }

    card.innerHTML = html;
    container.prepend(card);

    updateIncidentCount();

}


// ============================================================
// PROCESS INCIDENT
// ============================================================

function processIncident(payload) {

    console.log('==========================================');
    console.log('REFLEX INCIDENT RECEIVED');
    console.log(payload);
    console.log('==========================================');

    var detection  = payload.detection || {};
    var severity   = payload.severity  || {};
    var isCritical = severity.severity === 'CRITICAL';

    firePulse(isCritical);
    updateStats(payload);
    updateDispatch(payload);
    updateVideoStatus(payload);
    updateMap(payload);
    renderIncident(payload);

    if (detection.event_detected) {
        var sev = severity.severity || 'UNKNOWN';
        showToast(
            sev + ' incident detected — ' + (detection.reason || 'Accident'),
            isCritical ? 'error' : 'warning',
            6000
        );
    }

}


// ============================================================
// SOCKET.IO — NEW INCIDENT
// ============================================================

socket.on('new_incident', function (payload) {
    processIncident(payload);
});


// ============================================================
// TRIGGER BUTTON
// ============================================================

var triggerButton = document.getElementById('trigger-btn');


triggerButton.addEventListener('click', function () {

    var clip = document.getElementById('clipName').value.trim();
    var lat  = document.getElementById('lat').value.trim();
    var lng  = document.getElementById('lng').value.trim();

    if (!clip) {
        showToast('Please enter a video filename.', 'error');
        return;
    }

    if (!lat || !lng) {
        showToast('Please enter accident coordinates.', 'error');
        return;
    }

    triggerButton.disabled    = true;
    triggerButton.textContent = '⏳ AI ANALYZING...';

    var video = document.getElementById('incident-video');
    if (video) {
        video.currentTime = 0;
        video.play().catch(function () {});
    }

    var url =
        '/api/accidents/simulate/' + encodeURIComponent(clip) +
        '?lat=' + encodeURIComponent(lat) +
        '&lng=' + encodeURIComponent(lng);

    console.log('Sending request:', url);

    fetch(url, { method: 'POST' })

        .then(function (response) {
            if (!response.ok) {
                return response.json().then(function (err) {
                    throw new Error(err.error || 'Backend request failed');
                });
            }
            return response.json();
        })

        .then(function (payload) {
            console.log('REFLEX API RESPONSE:', payload);
            setTimeout(function () {
                processIncident(payload);
            }, 300);
        })

        .catch(function (error) {
            console.error('REFLEX ERROR:', error);
            showToast('REFLEX ERROR: ' + error.message, 'error', 7000);
        })

        .finally(function () {
            triggerButton.disabled    = false;
            triggerButton.textContent = '⚡ Trigger Accident';
        });

});


// ============================================================
// VIDEO LOAD CHECK
// ============================================================

var videoEl = document.getElementById('incident-video');

if (videoEl) {

    videoEl.addEventListener('loadedmetadata', function () {
        console.log('REFLEX video loaded:', videoEl.duration, 'seconds');
    });

    videoEl.addEventListener('error', function () {
        console.warn('Could not load traffic.mp4');
    });

}