// static/scripts.js
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("doctor-list")) loadDoctors();
  const searchBar = document.getElementById("searchBar");
  if (searchBar) searchBar.addEventListener("input", searchDoctors);
  const sendBtn = document.getElementById("sendBtn");
  if (sendBtn) setupChat();
  const notifBtn = document.getElementById("showNotificationsBtn");
  if (notifBtn) notifBtn.addEventListener("click", loadNotifications);
});

async function loadDoctors() {
  try {
    const res = await fetch("/api/doctors");
    const doctors = await res.json();
    const list = document.getElementById("doctor-list");
    if (!list) return;
    list.innerHTML = "";
    doctors.forEach((doc) => {
      const div = document.createElement("div");
      div.className = "doctor-card";
      div.innerHTML = `
        <h3>${escapeHtml(doc.name)}</h3>
        <p>${escapeHtml(doc.specialization)}</p>
        <p>${doc.available ? "🟢 Available" : "🔴 Not Available"}</p>
        <p>${escapeHtml(doc.hospital_name || "Unknown")}</p>
      `;
      list.appendChild(div);
    });
    window.__ALL_DOCTORS = doctors;
  } catch (e) {
    console.error("Error loading doctors:", e);
  }
}

function searchDoctors(e) {
  const q = (e.target.value || "").toLowerCase();
  const list = document.getElementById("doctor-list");
  if (!window.__ALL_DOCTORS || !list) return;
  const filtered = window.__ALL_DOCTORS.filter((d) => {
    return (
      (d.name && d.name.toLowerCase().includes(q)) ||
      (d.specialization && d.specialization.toLowerCase().includes(q)) ||
      (d.hospital_name && d.hospital_name.toLowerCase().includes(q))
    );
  });
  list.innerHTML = "";
  if (filtered.length === 0) {
    list.innerHTML = "<p>No doctors found.</p>";
    return;
  }
  filtered.forEach((doc) => {
    const div = document.createElement("div");
    div.className = "doctor-card";
    div.innerHTML = `<h3>${escapeHtml(doc.name)}</h3>
      <p>${escapeHtml(doc.specialization)}</p>
      <p>${doc.available ? "🟢 Available" : "🔴 Not Available"}</p>
      <p>${escapeHtml(doc.hospital_name || "Unknown")}</p>`;
    list.appendChild(div);
  });
}

function setupChat() {
  const sendBtn = document.getElementById("sendBtn");
  const input = document.getElementById("userInput");
  const messages = document.getElementById("messages");
  if (!sendBtn || !input || !messages) return;

  sendBtn.addEventListener("click", async () => {
    const msg = input.value.trim();
    if (!msg) return;
    append("You", msg);
    input.value = "";
    try {
      const res = await fetch("/api/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });
      const j = await res.json();
      append("MedBot", j.reply || "No reply");
    } catch (err) {
      append("MedBot", "Error contacting MedBot");
      console.error(err);
    }
  });

  input.addEventListener("keydown", (e) => { if (e.key === "Enter") sendBtn.click(); });

  function append(who, text) {
    const div = document.createElement("div");
    div.className = who === "You" ? "user" : "bot";
    div.innerText = `${who}: ${text}`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }
}

async function loadNotifications() {
  try {
    const res = await fetch("/api/notifications/all");
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      alert("No notifications yet.");
      return;
    }
    alert(data.map((n) => `${n.sent_time} — ${n.message}`).join("\n\n"));
  } catch (err) {
    console.error("Notif load error:", err);
    alert("Failed to load notifications");
  }
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}



// static/scripts.js
// Unified client logic: doctor list, search, booking, chat helpers, simple dedupe

// document.addEventListener("DOMContentLoaded", () => {
//   if (document.getElementById("doctor-list")) loadDoctors();
//   const searchBar = document.getElementById("searchBar");
//   if (searchBar) searchBar.addEventListener("input", searchDoctors);
//   const sendBtn = document.getElementById("sendBtn");
//   if (sendBtn) setupChat();
// });

// async function loadDoctors() {
//   try {
//     const res = await fetch("/api/doctors");
//     if (!res.ok) throw new Error("Failed fetching doctors");
//     let doctors = await res.json();
//     // dedupe by doctor_id (avoid double "Dr. Dr.")
//     const seen = new Set();
//     doctors = doctors.filter(d => {
//       if (!d.doctor_id) return false;
//       if (seen.has(d.doctor_id)) return false;
//       seen.add(d.doctor_id);
//       return true;
//     });

//     window.__ALL_DOCTORS = doctors;
//     renderDoctorList(doctors);
//   } catch (e) {
//     console.error("Error loading doctors:", e);
//     const list = document.getElementById("doctor-list");
//     if (list) list.innerHTML = "<p>Error loading doctors.</p>";
//   }
// }

// function renderDoctorList(doctors) {
//   const list = document.getElementById("doctor-list");
//   if (!list) return;
//   list.innerHTML = "";
//   if (!doctors || doctors.length === 0) { list.innerHTML = "<p>No doctors found.</p>"; return; }
//   doctors.forEach(doc => {
//     const div = document.createElement("div");
//     div.className = "doctor-card";
//     div.innerHTML = `
//       <h3>${escapeHtml(doc.name)}</h3>
//       <p>${escapeHtml(doc.specialization || 'General')}</p>
//       <p>${doc.available ? "🟢 Available" : "🔴 Not Available"}</p>
//       <p>${escapeHtml(doc.hospital_name || "Unknown")} ${doc.hospital_id ? '(' + escapeHtml(doc.hospital_id.slice(0,4) + '••••') + ')' : ''}</p>
//       <div style="margin-top:8px;">
//         <button ${!doc.available ? 'disabled' : ''} class="book-btn" data-id="${doc.doctor_id}" data-name="${escapeHtml(doc.name)}">Book</button>
//       </div>
//     `;
//     list.appendChild(div);
//   });

//   // attach handlers
//   document.querySelectorAll(".book-btn").forEach(b => {
//     b.addEventListener("click", async (e) => {
//       const btn = e.currentTarget;
//       const docId = btn.dataset.id;
//       const docName = btn.dataset.name;
//       if (!confirm(`Book appointment with ${docName}?`)) return;
//       try {
//         const r = await fetch("/patient/book_appointment", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ doctor_id: Number(docId), emergency: false })
//         });
//         const data = await r.json();
//         if (r.ok) {
//           alert(data.message || "Booked");
//           // store last booked appointment for feedback panel
//           window.__lastBookedAppointment = { id: data.appointment_id || data.id || null, doctor_id: docId };
//           // show feedback panel if exists
//           const fb = document.getElementById('feedback-panel');
//           if (fb) { fb.style.display = 'block'; }
//           loadDoctors(); // refresh list
//         } else {
//           alert(data.error || "Booking failed");
//         }
//       } catch (err) {
//         console.error(err); alert("Network error");
//       }
//     });
//   });
// }

// function searchDoctors(e) {
//   const q = (e.target.value || '').toLowerCase();
//   if (!window.__ALL_DOCTORS) return;
//   const filtered = window.__ALL_DOCTORS.filter(d=>{
//     return (d.name && d.name.toLowerCase().includes(q)) ||
//            (d.specialization && d.specialization.toLowerCase().includes(q)) ||
//            (d.hospital_name && d.hospital_name.toLowerCase().includes(q));
//   });
//   renderDoctorList(filtered);
// }

// function escapeHtml(s){ if (!s) return ''; return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

// /* Chat setup (if chatbot page includes sendBtn)
//    This is lightweight — actual LLM logic is on backend /api/llm/chat
// */
// function setupChat(){
//   const sendBtn = document.getElementById('sendBtn');
//   const input = document.getElementById('userInput');
//   const messages = document.getElementById('messages');
//   if (!sendBtn || !input || !messages) return;
//   sendBtn.addEventListener('click', async () => {
//     const msg = input.value.trim(); if (!msg) return;
//     appendMsg(messages, 'You: ' + msg, 'user');
//     input.value = '';
//     try {
//       const payload = { message: msg };
//       // attempt to attach geolocation if available
//       if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(pos => {
//           payload.location = { lat: pos.coords.latitude, lon: pos.coords.longitude };
//           postChat(payload, messages);
//         }, () => { postChat(payload, messages); }, { timeout:5000 });
//       } else {
//         postChat(payload, messages);
//       }
//     } catch(e){
//       appendMsg(messages, 'MedBot: Network error', 'bot');
//     }
//   });
//   input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendBtn.click(); });
// }

// async function postChat(payload, messagesEl){
//   try {
//     const r = await fetch('/api/llm/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
//     const js = await r.json();
//     appendMsg(messagesEl, 'MedBot: ' + (js.reply || 'No response'), 'bot');
//     // show suggested doctor if returned
//     if (js.suggested_doctor) {
//       const sd = js.suggested_doctor;
//       appendMsg(messagesEl, `Suggested: ${sd.name} (${sd.specialization}) — ${sd.hospital_name}`, 'bot');
//     }
//   } catch(e) { appendMsg(messagesEl, 'MedBot: Network error', 'bot'); }
// }

// function appendMsg(container, text, cls){
//   const d = document.createElement('div');
//   d.textContent = text;
//   d.style.margin = '8px 0';
//   d.style.padding = '6px 8px';
//   d.style.borderRadius = '8px';
//   if (cls === 'user') { d.style.background = '#d1e7ff'; d.style.textAlign = 'right'; }
//   else { d.style.background = '#eef6ff'; d.style.textAlign = 'left'; }
//   container.appendChild(d);
//   container.scrollTop = container.scrollHeight;
// }
