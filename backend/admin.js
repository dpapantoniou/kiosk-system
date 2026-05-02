
  <script>
    const API = "/kiosk";
async function login() {
    const username = document.getElementById("loginUser").value;
    const password = document.getElementById("loginPass").value;
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
    loadKiosks();
    loadQuestionnaires();
    loadResponses();
}
async function checkAuth() {
    const res = await fetch(`${API}/auth/me`, {
        credentials: "include"
    });
    if (res.ok) {
        document.getElementById("loginBox").style.display = "none";
        document.getElementById("adminApp").style.display = "block";
        loadKiosks();
        loadQuestionnaires();
        loadResponses();
    } else {
        document.getElementById("loginBox").style.display = "block";
        document.getElementById("adminApp").style.display = "none";
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
    let kiosksCache = [];
    let questionnairesCache = [];
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
    function renderDraftQuestions() {
      const wrap = document.getElementById("questions_preview");
      if (draftQuestions.length === 0) {
        wrap.innerHTML = `<p class="muted">No questions added yet.</p>`;
        return;
      }
      wrap.innerHTML = `<h3>Questions to be created</h3>` + draftQuestions.map((q, idx) => `
        <div class="question-box">
          <strong>${q.code}</strong> — ${q.question_type} — order ${q.order_no}<br>
          <span class="muted">EN:</span> ${q.text_i18n.en || ""}<br>
          <span class="muted">EL:</span> ${q.text_i18n.el || ""}<br>
          <span class="muted">TR:</span> ${q.text_i18n.tr || ""}<br>
          ${q.options_i18n ? `<pre>${JSON.stringify(q.options_i18n, null, 2)}</pre>` : ""}
          <button class="danger" onclick="removeQuestion(${idx})">Remove</button>
        </div>
      `).join("");
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
      toggleOptionsArea();
    }

    function removeQuestion(idx) {
      draftQuestions.splice(idx, 1);
      renderDraftQuestions();
    }

    function addQuestion() {
      const code = document.getElementById("question_code").value.trim();
      const orderNo = parseInt(document.getElementById("question_order").value, 10);
      const type = document.getElementById("question_type").value;
      const textEn = document.getElementById("text_en").value.trim();
      const textEl = document.getElementById("text_el").value.trim();
      const textTr = document.getElementById("text_tr").value.trim();
      const required = document.getElementById("question_required").value === "true";

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

      draftQuestions.push({
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
        branching_rule: null
      });

      renderDraftQuestions();
      resetQuestionForm();
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
        const res = await fetch(`${API}/questionnaires`, {
          method: "POST",
		  credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
          resultBox.innerText = `Error: ${JSON.stringify(data)}`;
          return;
        }

        resultBox.innerText = `Created questionnaire ${data.code} (id=${data.id})`;
        draftQuestions = [];
        renderDraftQuestions();
        document.getElementById("q_code").value = "";
        document.getElementById("q_name").value = "";
        await loadQuestionnaires();
      } catch (e) {
        resultBox.innerText = `Error: ${e.message}`;
      }
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

        wrap.innerHTML = `
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Code</th><th>Name</th><th>Location</th><th>Questionnaire ID</th>
              </tr>
            </thead>
            <tbody>
              ${data.map(k => `
                <tr>
                  <td>${k.id}</td>
                  <td>${k.code}</td>
                  <td>${k.name}</td>
                  <td>${k.location || ""}</td>
                  <td>${k.questionnaire_id ?? ""}</td>
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
                <th>ID</th><th>Code</th><th>Name</th><th>Questions</th>
              </tr>
            </thead>
            <tbody>
              ${data.map(q => `
                <tr>
                  <td>${q.id}</td>
                  <td>${q.code}</td>
                  <td>${q.name}</td>
                  <td>${q.questions ? q.questions.length : 0}</td>
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

    function fillAssignSelectors() {
      const kioskSel = document.getElementById("assign_kiosk");
      const qSel = document.getElementById("assign_questionnaire");

      kioskSel.innerHTML = kiosksCache.map(k =>
        `<option value="${k.id}">${k.code} — ${k.name}</option>`
      ).join("");

      qSel.innerHTML = questionnairesCache.map(q =>
        `<option value="${q.id}">${q.id} — ${q.code} — ${q.name}</option>`
      ).join("");
    }

    async function assignQuestionnaire() {
      const kioskId = parseInt(document.getElementById("assign_kiosk").value, 10);
      const questionnaireId = parseInt(document.getElementById("assign_questionnaire").value, 10);
      const kiosk = kiosksCache.find(k => k.id === kioskId);
      const resultBox = document.getElementById("assign_result");

      if (!kiosk || !questionnaireId) {
        resultBox.innerText = "Please select both kiosk and questionnaire.";
        return;
      }

      const payload = {
        name: kiosk.name,
        location: kiosk.location,
        is_active: kiosk.is_active,
        questionnaire_id: questionnaireId
      };

      resultBox.innerText = "Assigning...";

      try {
        const res = await fetch(`${API}/kiosks/${kioskId}`, {
          method: "PUT",
          credentials: "include",
		  headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
          resultBox.innerText = `Error: ${JSON.stringify(data)}`;
          return;
        }

        resultBox.innerText = `Assigned questionnaire ${questionnaireId} to kiosk ${kiosk.code}`;
        await loadKiosks();
      } catch (e) {
        resultBox.innerText = `Error: ${e.message}`;
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
    toggleOptionsArea();
    renderDraftQuestions();
    checkAuth();
  </script>
  