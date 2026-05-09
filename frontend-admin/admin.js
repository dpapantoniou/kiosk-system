async function login() {
    const password = document.getElementById("loginPass").value;
	const username = document.getElementById("loginUser").value;
    const res = await fetch(`${API}/auth/login`, {
        method: "POST",
		credentials: "include",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });
    if (!res.ok) {
        document.getElementById("loginMsg").innerText = "Login failed";
        return;
    }
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("adminApp").style.display = "block";
        await loadQuestionnaires();
		await loadKiosks();
        await loadResponses();
		loadAnalyticsSummary();
}
async function checkAuth() {
    const res = await fetch(`${API}/auth/me`, {
        credentials: "include"
    });
    if (res.ok) {
        document.getElementById("loginBox").style.display = "none";
        document.getElementById("adminApp").style.display = "block";
        await loadQuestionnaires();
		await loadKiosks();
        await loadResponses();
		loadAnalyticsSummary();
    } else {
        document.getElementById("loginBox").style.display = "block";
        document.getElementById("adminApp").style.display = "none";
    }
}
async function createKiosk() {

  const code =
    document.getElementById("kiosk_code")
      .value.trim();

  const name =
    document.getElementById("kiosk_name")
      .value.trim();

  const location =
    document.getElementById("kiosk_location")
      .value.trim();
	const isActive =
    document.getElementById("kiosk_active")
      .value === "true";

  const resultBox =
    document.getElementById("kiosk_create_result");

  if (!code || !name) {

    resultBox.innerText =
      "Code and name are required.";

    return;
  }

  resultBox.innerText = "Creating...";

  try {

    const res = await fetch(`${API}/kiosks`, {

      method: "POST",

      credentials: "include",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        code,
        name,
        location,
		logo_data: currentLogoData,
        is_active: isActive
      })
    });

    const data = await res.json();

    if (!res.ok) {

      resultBox.innerText =
        `Error: ${JSON.stringify(data)}`;

      return;
    }

    resultBox.innerText =
      `Created kiosk ${data.code}`;

    document.getElementById("kiosk_code").value = "";
    document.getElementById("kiosk_name").value = "";
    document.getElementById("kiosk_location").value = "";

    await loadKiosks();

  } catch (e) {

    resultBox.innerText =
      `Error: ${e.message}`;
  }
}

async function logout() {
    await fetch(`${API}/auth/logout`, {
        method: "POST",
        credentials: "include"
    });

    location.reload();
}	
    let draftQuestions = [];
	let editingQuestionnaireId = null;
    let editingQuestionIndex = null;
    let kiosksCache = [];
	let kioskStatusesCache = [];
    let questionnairesCache = [];
	let currentLogoData = "";
    let currentEditLogoData = "";
    function toggleOptionsArea() {
      const type = document.getElementById("question_type").value;
      document.getElementById("options_area").style.display =
        (type === "single_choice" || type === "multi_choice") ? "block" : "none";
    }
    function linesToArray(text) {
      return text
        .split("\n")
        .map(x => x.trim())
        .filter(Boolean);
    }
	
	function refreshBranchingQuestionOptions() {
    const sel =
        document.getElementById(
            "branch_depends_on"
        );
    if (!sel) return;
    const current =
        sel.value;
    sel.innerHTML =
        `<option value="">
            -- none --
        </option>`;
    draftQuestions.forEach(q => {
        const label =
            q.text_i18n?.en || q.code;
        sel.innerHTML += `
            <option value="${q.code}">
                ${q.code} — ${label}
            </option>
        `;
    });
    sel.value = current;
    }
	
    function renderDraftQuestions() {
      const wrap = document.getElementById("questions_preview");
      if (draftQuestions.length === 0) {
        wrap.innerHTML = `<p class="muted">No questions added yet.</p>`;
        return;
      }
      wrap.innerHTML = `<h3>Question List</h3>` + draftQuestions.map((q, idx) => `
        <div class="question-box">
          <strong>${q.code}</strong> — ${q.question_type} — order ${q.order_no}<br>
          <span class="muted">EN:</span> ${q.text_i18n.en || ""}<br>
          <span class="muted">EL:</span> ${q.text_i18n.el || ""}<br>
          <span class="muted">TR:</span> ${q.text_i18n.tr || ""}<br>
          ${q.options_i18n ? `<pre>${JSON.stringify(q.options_i18n, null, 2)}</pre>` : ""}
			<button onclick="editQuestion(${idx})">
				Edit
			</button>
			<button class="danger"
					onclick="removeQuestion(${idx})">
				Remove
			</button>
        </div>
      `).join("");
	   refreshBranchingQuestionOptions();
    }

    function resetQuestionForm() {
      document.getElementById("question_code").value = "";
      document.getElementById("question_order").value = draftQuestions.length + 1;
      document.getElementById("question_type").value = "rating";
      document.getElementById("text_en").value = "";
      document.getElementById("text_el").value = "";
      document.getElementById("text_tr").value = "";
      document.getElementById("opts_en").value = "";
      document.getElementById("opts_el").value = "";
      document.getElementById("opts_tr").value = "";
      document.getElementById("question_required").value = "false";
	  document.getElementById(
				"branch_depends_on"
				).value = "";
	  document.getElementById(
				"branch_equals"
				).value = "";
      toggleOptionsArea();
    }

    function removeQuestion(idx) {
      draftQuestions.splice(idx, 1);
      renderDraftQuestions();
    }
	function editQuestion(idx) {

  const q = draftQuestions[idx];

  if (!q) return;

  editingQuestionIndex = idx;

  document.getElementById("question_form_title").innerText =
    "Create / Edit Question";

  document.getElementById("add_question_btn").innerText =
    "Add / Update Question";

  document.getElementById("question_code").value = q.code || "";
  document.getElementById("question_order").value = q.order_no || 1;
  document.getElementById("question_type").value = q.question_type || "rating";

  document.getElementById("text_en").value = q.text_i18n?.en || "";
  document.getElementById("text_el").value = q.text_i18n?.el || "";
  document.getElementById("text_tr").value = q.text_i18n?.tr || "";

  document.getElementById("question_required").value =
    q.is_required ? "true" : "false";

  toggleOptionsArea();
	if (q.branching_rule) {
		document.getElementById(
		"branch_depends_on"
		).value =
		q.branching_rule.depends_on || "";

		document.getElementById(
		"branch_equals"
		).value =
		(q.branching_rule.equals_any || [])
			.join(",");
	}
	else {
		document.getElementById(
		"branch_depends_on"
		).value = "";
		document.getElementById(
			"branch_equals"
		).value = "";
	}

  if (q.options_i18n) {
    document.getElementById("opts_en").value =
      (q.options_i18n.en || []).join("\n");

    document.getElementById("opts_el").value =
      (q.options_i18n.el || []).join("\n");

    document.getElementById("opts_tr").value =
      (q.options_i18n.tr || []).join("\n");
  } else {
    document.getElementById("opts_en").value = "";
    document.getElementById("opts_el").value = "";
    document.getElementById("opts_tr").value = "";
  }

  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });
}
	
	
	
	function editQuestionnaire(id) {
     const q =
        questionnairesCache.find(
        x => x.id === id
        );
     if (!q) return;
     editingQuestionnaireId = id;
	 editingQuestionIndex = null;
     document.getElementById("q_code").value =
       q.code;
     document.getElementById("q_name").value =
       q.name;
     document.getElementById("q_active").value =
       q.is_active ? "true" : "false";
     draftQuestions =
       JSON.parse(
       JSON.stringify(q.questions || [])
       );
     renderDraftQuestions();
     const btn =
       document.getElementById("create_questionnaire_btn");
     if (btn) {
       btn.innerText =
         "Save Questionnaire";
     }
     window.scrollTo({
       top: 0,
       behavior: "smooth"
     });
}

    function addQuestion() {
      const code = document.getElementById("question_code").value.trim();
      const orderNo = parseInt(document.getElementById("question_order").value, 10);
      const type = document.getElementById("question_type").value;
      const textEn = document.getElementById("text_en").value.trim();
      const textEl = document.getElementById("text_el").value.trim();
      const textTr = document.getElementById("text_tr").value.trim();
      const required = document.getElementById("question_required").value === "true";
	  const dependsOn =
			document.getElementById("branch_depends_on")
			.value.trim();
	  const equalsValues =
		    document.getElementById("branch_equals")
           .value
           .split(",")
           .map(x => x.trim())
           .filter(Boolean);

      if (!code || !orderNo || !textEn) {
        alert("Please provide at least question code, order number, and English text.");
        return;
      }

      let optionsI18n = null;
      if (type === "single_choice" || type === "multi_choice") {
        const en = linesToArray(document.getElementById("opts_en").value);
        const el = linesToArray(document.getElementById("opts_el").value);
        const tr = linesToArray(document.getElementById("opts_tr").value);

        if (en.length === 0) {
          alert("Choice questions need at least English options.");
          return;
        }

        optionsI18n = { en, el, tr };
      }
	const questionObj = {

		code,

		order_no: orderNo,

		question_type: type,

		text_i18n: {
			en: textEn,
			el: textEl,
			tr: textTr
		},

		options_i18n: optionsI18n,
			is_required: required,
			branching_rule:
			  dependsOn
				? {
					depends_on: dependsOn,
					equals_any: equalsValues
				}
				: null
	};

	if (editingQuestionIndex !== null) {

		draftQuestions[editingQuestionIndex] =
		questionObj;

		editingQuestionIndex = null;

		document.getElementById(
			"question_form_title"
		).innerText =
		"Add Question";

		document.getElementById(
		"add_question_btn"
		).innerText =
		"Add Question";
	}

else {
	draftQuestions.push(questionObj);
	}
	renderDraftQuestions();
	resetQuestionForm();
	window.scrollTo({
       top: 0,
       behavior: "smooth"
    });
    }

    async function createQuestionnaire() {
      const code = document.getElementById("q_code").value.trim();
      const name = document.getElementById("q_name").value.trim();
      const isActive = document.getElementById("q_active").value === "true";

      if (!code || !name) {
        alert("Questionnaire code and name are required.");
        return;
      }

      if (draftQuestions.length === 0) {
        alert("Add at least one question.");
        return;
      }

      const payload = {
        code,
        name,
        is_active: isActive,
        questions: draftQuestions
      };

      const resultBox = document.getElementById("create_result");
      resultBox.innerText = "Creating...";
	  
	  try {

      const isEdit =
         editingQuestionnaireId !== null;

      const url = isEdit
        ? `${API}/questionnaires/${editingQuestionnaireId}`
        : `${API}/questionnaires`;

      const method =
        isEdit ? "PUT" : "POST";

      const res = await fetch(url, {

        method,

        credentials: "include",

        headers: {
          "Content-Type": "application/json"
      },

      body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok) {
        resultBox.innerText = `Error: ${JSON.stringify(data)}`;
      return;
      }

      resultBox.innerText =
       isEdit
         ? `Updated questionnaire ${data.code}`
         : `Created questionnaire ${data.code} (id=${data.id})`;

        draftQuestions = [];
        renderDraftQuestions();

        document.getElementById("q_code").value = "";
        document.getElementById("q_name").value = "";

        editingQuestionnaireId = null;

        const btn =
        document.getElementById("create_questionnaire_btn");

       if (btn) {
          btn.innerText = "Create Questionnaire";
       }

       await loadQuestionnaires();

     } catch (e) {

       resultBox.innerText = `Error: ${e.message}`;
     }	
	}

function formatLastSeen(value) {

  if (!value) return "";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatKioskStatus(status) {

  if (!status) return "never_seen";

  const minutes = status.minutes_since_seen;

  const suffix =
    minutes === null || minutes === undefined
      ? ""
      : ` (${minutes} min)`;

  return `${status.status}${suffix}`;
}


    async function loadKiosks() {
      const wrap = document.getElementById("kiosks_list");
      wrap.innerText = "Loading...";
      try {
        const res = await fetch(`${API}/kiosks`, {
		credentials: "include"
		});
		if (res.status === 401) {
            location.reload();
            return;
        }
        const data = await res.json();
        kiosksCache = data;
		try {

		const statusRes = await fetch(
			`${API}/kiosks/status`,
			{
			credentials: "include"
			}
		);

		kioskStatusesCache =
			statusRes.ok
			? await statusRes.json()
			: [];

		} catch {

			kioskStatusesCache = [];
		}

		const statusMap = {};

		kioskStatusesCache.forEach(s => {
		statusMap[s.kiosk_code] = s;
		});	
		
        const qMap = {};
        questionnairesCache.forEach(q => {
           qMap[q.id] = q;
        });
        wrap.innerHTML = `
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Location</th>
				<th>Status</th>
				<th>Last Seen</th>
                <th>Questionnaire</th>
                <th>Actions</th>				
              </tr>
            </thead>
            <tbody>
              ${data.map(k => `
                <tr>
                  <td>${k.code}</td>
                  <td>${k.name}</td>
                  <td>${k.location || ""}</td>
				  <td>${formatKioskStatus(statusMap[k.code])}</td>
				  <td>${formatLastSeen(statusMap[k.code]?.last_seen)}</td>
                  <td>${qMap[k.questionnaire_id]?.code || ""}</td>
				  <td>
                     <button onclick="editKiosk(${k.id})">
                       Edit
                     </button>
					 <button onclick="disableKiosk(${k.id})">
                       Disable
                     </button>
                  </td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        `;

        fillAssignSelectors();
      } catch (e) {
        wrap.innerText = `Error: ${e.message}`;
      }
    }

    async function loadQuestionnaires() {
      const wrap = document.getElementById("questionnaires_list");
      wrap.innerText = "Loading...";
      try {
	  const res = await fetch(`${API}/questionnaires`, {
          credentials: "include"
      });

      if (res.status === 401) {
          location.reload();
          return;
      }
        const data = await res.json();
        questionnairesCache = data;

        wrap.innerHTML = `
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Code</th><th>Name</th><th>Questions</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${data.map(q => `
                <tr>
                  <td>${q.id}</td>
                  <td>${q.code}</td>
                  <td>${q.name}</td>
                  <td>${q.questions ? q.questions.length : 0}</td>
				  <td>
                     <button onclick="editQuestionnaire(${q.id})">
                       Edit
                     </button>
                  </td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        `;

        fillAssignSelectors();
      } catch (e) {
        wrap.innerText = `Error: ${e.message}`;
      }
    }
    function editKiosk(id) {

      const kiosk =
      kiosksCache.find(k => k.id === id);

      if (!kiosk) return;

      document.getElementById("edit_kiosk_card")
        .style.display = "block";

      document.getElementById("edit_kiosk_id")
        .value = kiosk.id;

      document.getElementById("edit_kiosk_code")
        .value = kiosk.code;

      document.getElementById("edit_kiosk_name")
        .value = kiosk.name;

      document.getElementById("edit_kiosk_location")
        .value = kiosk.location || "";

      document.getElementById("edit_kiosk_active")
        .value = kiosk.is_active ? "true" : "false";

      window.scrollTo({
      top: 0,
      behavior: "smooth"
     });
    }
	
    function cancelKioskEdit() {

      document.getElementById("edit_kiosk_card")
       .style.display = "none";

      document.getElementById("edit_kiosk_result")
       .innerText = "";
    }

    async function saveKioskEdit() {

      const id =
       document.getElementById("edit_kiosk_id").value;

      const code =
         document.getElementById("edit_kiosk_code")
        .value.trim();

      const name =
         document.getElementById("edit_kiosk_name")
        .value.trim();

      const location =
        document.getElementById("edit_kiosk_location")
         .value.trim();
		 

      const isActive =
        document.getElementById("edit_kiosk_active")
         .value === "true";

      const kiosk =
        kiosksCache.find(k => k.id == id);

      const questionnaireId =
        kiosk?.questionnaire_id || null;

      const resultBox =
        document.getElementById("edit_kiosk_result");

      try {

         const res = await fetch(`${API}/kiosks/${id}`,
           {
             method: "PUT",

             credentials: "include",

             headers: {
               "Content-Type": "application/json"
             },

             body: JSON.stringify({
               code,
               name,
               location,
			   logo_data: currentEditLogoData,
               is_active: isActive,
               questionnaire_id: questionnaireId
             })
        }
    );

    const data = await res.json();

    if (!res.ok) {

      resultBox.innerText =
        `Error: ${JSON.stringify(data)}`;

      return;
    }

    resultBox.innerText =
      "Kiosk updated successfully.";

    cancelKioskEdit();
	await loadKiosks();

  } catch (e) {

    resultBox.innerText =
      `Error: ${e.message}`;
  }
}



    function fillAssignSelectors() {
      const kioskSel = document.getElementById("assign_kiosk");
      const qSel = document.getElementById("assign_questionnaire");

      kioskSel.innerHTML = kiosksCache.map(k =>
        `<option value="${k.id}">${k.code} — ${k.name}</option>`
      ).join("");

      qSel.innerHTML = questionnairesCache.map(q =>
		 `<option value="${q.id}">
           ${q.code} — ${q.name}
         </option>`
      ).join("");
    }

async function assignQuestionnaire() {

  const kioskIds = Array.from(
    document.getElementById("assign_kiosk").selectedOptions
  ).map(o => parseInt(o.value, 10));

  const questionnaireId = parseInt(
    document.getElementById("assign_questionnaire").value,
    10
  );

  const selectedQuestionnaire =
    questionnairesCache.find(
      q => q.id === questionnaireId
    );

  const resultBox =
    document.getElementById("assign_result");

  if (!kioskIds.length || !questionnaireId) {

    resultBox.innerText =
      "Please select kiosk(s) and questionnaire.";

    return;
  }

  resultBox.innerText = "Assigning...";

  try {

    const res = await fetch(
      `${API}/kiosks/bulk-assign-questionnaire`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          questionnaire_id: questionnaireId,
          kiosk_ids: kioskIds
        })
      }
    );

    const data = await res.json();

    if (!res.ok) {

      resultBox.innerText =
        `Error: ${JSON.stringify(data)}`;

      return;
    }

    resultBox.innerText =
      `Assigned ${selectedQuestionnaire.code} to ${data.updated_kiosks} kiosk(s)`;

    await loadKiosks();

  } catch (e) {

    resultBox.innerText =
      `Error: ${e.message}`;
  }
}


    async function loadResponses() {
      const wrap = document.getElementById("responses_list");
      wrap.innerText = "Loading...";
      try {
     const res = await fetch(`${API}/responses`, {
         credentials: "include"
     });
     if (res.status === 401) {
          location.reload();
          return;
     }
        const data = await res.json();
		data.reverse();

        wrap.innerHTML = `
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Time</th><th>Kiosk</th><th>Lang</th><th>Answers</th>
              </tr>
            </thead>
            <tbody>
              ${data.map(r => `
                <tr>
                  <td>${r.id}</td>
                  <td>${r.created_at || ""}</td>
                  <td>${r.kiosk_code}</td>
                  <td>${r.lang || ""}</td>
                  <td><pre>${JSON.stringify(r.answers, null, 2)}</pre></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        `;
      } catch (e) {
        wrap.innerText = `Error: ${e.message}`;
      }
    }
    function downloadCsv() {
         window.open(`${API}/responses/export.csv`, "_blank");
    }
	function exportResponsesXlsx() {
		 window.open(
        API + "/responses/export.xlsx",
        "_blank"
        );
    }
    toggleOptionsArea();
    renderDraftQuestions();
    checkAuth();
	
async function loadAnalyticsSummary() {

    const wrap =
        document.getElementById(
            "analytics_summary"
        );

    if (!wrap) return;

    wrap.innerText =
        "Loading analytics...";

    try {

        const res = await fetch(
            `${API}/analytics/summary`,
            {
                credentials: "include"
            }
        );

        if (res.status === 401) {

            location.reload();
            return;
        }

        const data = await res.json();

        wrap.innerHTML = `

            <div class="analytics-grid">

                <div class="analytics-card">
                    <h3>Total Responses</h3>
                    <p>${data.total_responses}</p>
                </div>

                <div class="analytics-card">
                    <h3>Responses Today</h3>
                    <p>${data.responses_today}</p>
                </div>

                <div class="analytics-card">
                    <h3>Average Rating</h3>
                    <p>${data.avg_rating ?? "-"}</p>
                </div>

                <div class="analytics-card">
                    <h3>Active Kiosks</h3>
                    <p>${data.active_kiosks}</p>
                </div>

            </div>

        `;

    } catch (e) {

        wrap.innerText =
            `Error: ${e.message}`;
    }
}	
	
	
function showTab(tabId, buttonEl) {

    document.querySelectorAll('.tab-content')
        .forEach(el => el.style.display = 'none');

    document.querySelectorAll('.tab-button')
        .forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).style.display =
        'block';

    buttonEl.classList.add('active');

    if (tabId === "analytics_tab") {

        loadAnalyticsSummary();
    }
}



	function showTab(tabId, buttonEl) {

  document.querySelectorAll('.tab-content')
    .forEach(el => el.style.display = 'none');

  document.querySelectorAll('.tab-button')
    .forEach(el => el.classList.remove('active'));

  document.getElementById(tabId).style.display = 'block';

  buttonEl.classList.add('active');
}
  
async function loadAntiAbuseSettings() {
  const result = document.getElementById("antiabuse_settings_result");
  result.innerText = "Loading...";

  try {
    const res = await fetch(`${API}/anti-abuse/settings`, {
      credentials: "include"
    });

    if (res.status === 401) {
      location.reload();
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      result.innerText = `Error: ${JSON.stringify(data)}`;
      return;
    }

    document.getElementById("aa_enabled").value = String(data.enabled);
    document.getElementById("aa_cooldown_seconds").value = data.cooldown_seconds;
    document.getElementById("aa_repeat_threshold").value = data.repeat_threshold;
    document.getElementById("aa_repeat_window_seconds").value = data.repeat_window_seconds;
    document.getElementById("aa_identical_pattern_threshold").value = data.identical_pattern_threshold;
    document.getElementById("aa_hard_block_on_cooldown").value = String(data.hard_block_on_cooldown);

    result.innerText = "Settings loaded.";
  } catch (e) {
    result.innerText = `Error: ${e.message}`;
  }
}

async function saveAntiAbuseSettings() {
  const result = document.getElementById("antiabuse_settings_result");
  result.innerText = "Saving...";

  const payload = {
    enabled: document.getElementById("aa_enabled").value === "true",
    cooldown_seconds: parseInt(document.getElementById("aa_cooldown_seconds").value || "0"),
    repeat_threshold: parseInt(document.getElementById("aa_repeat_threshold").value || "1"),
    repeat_window_seconds: parseInt(document.getElementById("aa_repeat_window_seconds").value || "1"),
    identical_pattern_threshold: parseInt(document.getElementById("aa_identical_pattern_threshold").value || "1"),
    hard_block_on_cooldown: document.getElementById("aa_hard_block_on_cooldown").value === "true"
  };

  try {
    const res = await fetch(`${API}/anti-abuse/settings`, {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      result.innerText = `Error: ${JSON.stringify(data)}`;
      return;
    }

    result.innerText = "Settings saved.";
  } catch (e) {
    result.innerText = `Error: ${e.message}`;
  }
}

async function loadAntiAbuseEvents() {
  const wrap = document.getElementById("antiabuse_events_list");
  wrap.innerText = "Loading...";

  try {
    const res = await fetch(`${API}/anti-abuse/events?limit=100`, {
      credentials: "include"
    });

    if (res.status === 401) {
      location.reload();
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      wrap.innerText = `Error: ${JSON.stringify(data)}`;
      return;
    }

    if (!data.length) {
      wrap.innerText = "No anti-abuse events recorded yet.";
      return;
    }

    wrap.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Kiosk</th>
            <th>Event</th>
            <th>Severity</th>
            <th>Metadata</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(e => `
            <tr>
              <td>${e.created_at || ""}</td>
              <td>${e.kiosk_code || ""}</td>
              <td>${e.event_type}</td>
              <td>${e.severity}</td>
              <td><pre>${JSON.stringify(e.metadata_json || {}, null, 2)}</pre></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (e) {
    wrap.innerText = `Error: ${e.message}`;
  }
}
function loadLogoFile(input) {

    const file = input.files[0];

    if (!file) return;

    if (file.size > 300000) {

        alert("Logo too large");

        return;
    }

    const reader = new FileReader();

    reader.onload = function(e) {

        currentLogoData = e.target.result;

        alert("Logo loaded");
    };

    reader.readAsDataURL(file);
}

function loadEditLogoFile(input) {

    const file = input.files[0];

    if (!file) return;

    if (file.size > 300000) {

        alert("Logo too large");

        return;
    }

    const reader = new FileReader();

    reader.onload = function(e) {

        currentEditLogoData = e.target.result;

        alert("Logo loaded");
    };

    reader.readAsDataURL(file);
}

async function disableKiosk(id) {

    const ok = confirm(
        "Disable this kiosk?\n\nThis preserves historical data but removes the kiosk from active operation."
    )

    if (!ok) return

    const r = await fetch(`/kiosk/kiosks/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
            enabled: false
        })
    })

    if (!r.ok) {

        alert("Failed to disable kiosk")
        return
    }

    await loadKiosks()

    alert("Kiosk disabled")
}