/* The Language of College: small helpers.
   Reading pages work without this file. Only the prompt builder needs it. */
(function () {
  // On phones and tablets, the section menu starts closed behind its button.
  var menu = document.querySelector('.sidenav details');
  if (menu && window.matchMedia('(max-width: 900px)').matches) {
    menu.removeAttribute('open');
  }

  // Open every answer before printing, so printed pages include them.
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('details.answer').forEach(function (d) { d.setAttribute('open', ''); });
  });

  // Copy buttons: <button data-copy="id-of-element">
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var source = document.getElementById(btn.getAttribute('data-copy'));
      var status = btn.parentNode.querySelector('.copied');
      var text = source.textContent;
      function done(ok) {
        if (status) { status.textContent = ok ? 'Copied.' : 'Copy did not work. Select the text and copy it by hand.'; }
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
      } else {
        var range = document.createRange();
        range.selectNodeContents(source);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        try { done(document.execCommand('copy')); } catch (e) { done(false); }
      }
    });
  });

  // Assignment prompt builder. Nothing is saved or sent.
  var form = document.getElementById('pb-form');
  if (!form) { return; }
  var out = document.getElementById('pb-out');

  function val(id) { return document.getElementById(id).value.trim(); }
  function lines(id) {
    return val(id).split('\n').map(function (s) { return s.replace(/^[-*•]\s*/, '').trim(); }).filter(Boolean);
  }
  function sentence(s) { return /[.!?]$/.test(s) ? s : s + '.'; }
  function lower(s) { return s.charAt(0).toLowerCase() + s.slice(1); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var parts = [];
    var missing = [];
    var title = val('pb-title'), skill = val('pb-skill'), use = val('pb-use');
    var type = val('pb-type'), verb = val('pb-verb'), topic = val('pb-topic');
    var def = val('pb-def'), reader = val('pb-reader');
    var req = lines('pb-req'), opt = lines('pb-opt');
    var grade = val('pb-grade'), lang = val('pb-lang');
    var ai = val('pb-ai'), may = val('pb-may'), maynot = val('pb-maynot'), submit = val('pb-submit');

    var supported = ai.indexOf('AI-supported') === 0;
    var uses = [];
    form.querySelectorAll('input[name="pb-use"]:checked').forEach(function (c) { uses.push(c.value); });
    val('pb-use-other').split(';').forEach(function (u) { u = u.trim().replace(/[.]$/, ''); if (u) { uses.push(lower(u)); } });
    var limit = val('pb-ai-limit');

    if (title) { parts.push(title); }

    if (skill) {
      var purpose = 'This assignment gives you practice with ' + sentence(lower(skill));
      if (use) { purpose += ' You will use this skill ' + sentence(lower(use)); }
      parts.push('Purpose\n' + purpose);
    } else { missing.push('the purpose (what skill the assignment builds)'); }

    if (type && verb && topic) {
      var task = 'Write ' + (/^[aeiou]/i.test(type) ? 'an ' : 'a ') + lower(type) + ' that ' + lower(verb) + ' ' + sentence(topic);
      if (def) { task += ' In this course, "' + lower(verb) + '" means ' + sentence(lower(def)); }
      parts.push('Task\n' + task);
    } else { missing.push('the task (type of text, task verb, and topic)'); }
    if (verb && !def) { missing.push('what "' + lower(verb) + '" means in your course'); }

    if (reader) { parts.push('Reader\nWrite for ' + sentence(lower(reader))); }
    else { missing.push('the reader'); }

    if (req.length) {
      parts.push('Requirements\nYour work must meet each of these requirements:\n' + req.map(function (r) { return '- ' + r; }).join('\n'));
      if (!req.some(function (r) { return /\d/.test(r); })) { missing.push('a number in the requirements (length, sources)'); }
    } else { missing.push('the requirements'); }

    if (opt.length) { parts.push('Optional\n' + opt.map(function (r) { return '- ' + r; }).join('\n')); }

    var grading = [];
    if (grade) { grading.push('Most of your grade is for ' + sentence(lower(grade))); }
    if (lang) { grading.push(lang); }
    grading.push('See the rubric for details.');
    parts.push('Grading\n' + grading.join(' '));
    if (!grade) { missing.push('what counts most in the grade'); }
    if (!lang) { missing.push('how grammar and word choice count'); }

    if (ai || may || maynot) {
      var tools = [];
      if (ai) {
        tools.push('AI level: ' + ai);
        if (supported) {
          if (uses.length) { tools.push('You may use AI for:\n' + uses.map(function (u) { return '- ' + u; }).join('\n')); }
          if (limit) { tools.push('You may not use AI to ' + sentence(limit)); }
          if (document.getElementById('pb-disclose').checked) { tools.push('At the end of your work, add one or two sentences that say how you used AI.'); }
        }
        tools.push('See the AI Course Policy in the syllabus.');
      }
      if (may) { tools.push('You may use ' + sentence(lower(may))); }
      if (maynot) { tools.push('You may not use ' + sentence(lower(maynot))); }
      tools.push('If you are not sure whether a tool is allowed, ask me before you use it.');
      parts.push('Tools\n' + tools.join('\n'));
    }
    if (!ai) { missing.push('the AI level (No AI, AI-supported, or AI-integrated)'); }
    if (supported && !uses.length) { missing.push('which uses of AI are allowed (AI-supported does not say)'); }
    if (supported && !limit) { missing.push('which use of AI is not allowed'); }
    if (!may && !maynot) { missing.push('which language tools are allowed (dictionary, translation tool, grammar checker)'); }

    if (submit) { parts.push('Submitting\nSubmit your work in ' + submit + ' by the due date listed there.'); }
    else { missing.push('where to submit and where to find the due date'); }

    parts.push('Questions\nIf any part of this prompt is unclear, ask me. Questions about a prompt are welcome.');

    document.getElementById('pb-text').textContent = parts.join('\n\n');
    var box = document.getElementById('pb-missing');
    box.textContent = '';
    var p = document.createElement('p');
    if (missing.length) {
      box.className = 'note note-tip';
      p.textContent = 'A student could not tell these things from your prompt yet:';
      box.appendChild(p);
      var ul = document.createElement('ul');
      missing.forEach(function (m) { var li = document.createElement('li'); li.textContent = m; ul.appendChild(li); });
      box.appendChild(ul);
    } else {
      box.className = 'note note-term';
      p.textContent = 'This prompt answers every question on the checklist.';
      box.appendChild(p);
    }
    out.hidden = false;
    out.focus();
  });

  // Show the extra AI questions only when AI-supported is chosen.
  var aiSelect = document.getElementById('pb-ai');
  var aiDetail = document.getElementById('pb-ai-detail');
  function showDetail() { aiDetail.hidden = aiSelect.value.indexOf('AI-supported') !== 0; }
  aiSelect.addEventListener('change', showDetail);
  showDetail();

  form.addEventListener('reset', function () { out.hidden = true; aiDetail.hidden = true; });
})();
