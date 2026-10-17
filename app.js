'use strict';

// Values from Tables 1 and 4 of arXiv:2610.18082v1, not locally generated results.
const results = [
  { name: 'Terminus-2', group: 'baseline', overall: [48.6,6.7], tb2: [66.9,9.9], tb3: [36.5,13.5], lhtb: [12.3,8.9], step: [26.7,7.3], time: [46.8,7.0] },
  { name: '+ SC', group: 'baseline', overall: [51.5,6.9], tb2: [68.2,10.3], tb3: [45.5,13.4], lhtb: [13.8,9.2], step: [27.6,7.3], time: [47.9,6.9] },
  { name: '+ WM', group: 'baseline', overall: [49.8,6.8], tb2: [66.9,10.0], tb3: [41.6,14.2], lhtb: [13.0,9.2], step: [27.1,7.5], time: [47.4,7.0] },
  { name: 'BeliefWeaver', group: 'teacher', overall: [53.7,6.6], tb2: [71.2,9.6], tb3: [46.6,13.7], lhtb: [14.8,9.3], step: [29.5,7.4], time: [48.4,6.9] },
  { name: 'SFT', group: 'student', overall: [55.6,7.2], tb2: [69.4,10.4], tb3: [54.1,15.3], lhtb: [20.9,10.7], step: [29.9,8.2], time: [50.3,7.3] },
  { name: 'SFT + OPD', group: 'student', overall: [58.4,6.6], tb2: [74.5,9.3], tb3: [50.9,15.3], lhtb: [23.4,10.5], step: [29.2,7.6], time: [50.1,7.2] },
  { name: 'SFT + OPD + Gen', group: 'student', overall: [57.5,6.8], tb2: [74.2,9.5], tb3: [50.4,16.2], lhtb: [20.6,10.1], step: [28.7,7.7], time: [49.3,7.3] }
];
const benchmarkNotes = {
  overall: 'Aggregate final score across the three benchmark suites.',
  tb2: 'TB2 · Terminal-Bench 2.0. Final test-pass fraction or graded reward.',
  tb3: 'TB3 · Terminal-Bench 3.0. Final test-pass fraction or graded reward.',
  lhtb: 'LHTB · Long-Horizon Terminal-Bench. Final test-pass fraction or graded reward.'
};
const chart = document.querySelector('#result-chart');
for (const row of results) {
  const element = document.createElement('div');
  element.className = `chart-row${row.group === 'teacher' ? ' highlight' : row.name === 'SFT + OPD' ? ' student-highlight' : ''}`;
  element.innerHTML = `<div class="chart-label">${row.name}</div><div class="bar-track" aria-hidden="true"><div class="bar-fill ${row.group}"></div></div><div class="chart-value"></div>`;
  chart.append(element);
}
function renderResults(benchmark) {
  Array.from(chart.children).forEach((element, i) => {
    const [mean, ci] = results[i][benchmark];
    element.querySelector('.bar-fill').style.width = `${mean}%`;
    element.querySelector('.chart-value').innerHTML = `${mean.toFixed(1)} <span>± ${ci.toFixed(1)}</span>`;
  });
  document.querySelector('#benchmark-note').textContent = benchmarkNotes[benchmark];
  document.querySelectorAll('[data-benchmark]').forEach(button => {
    const selected = button.dataset.benchmark === benchmark;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
}
document.querySelectorAll('[data-benchmark]').forEach(button => button.addEventListener('click', () => renderResults(button.dataset.benchmark)));
renderResults('overall');
const tableBody = document.querySelector('#full-results');
results.forEach(row => {
  const tr = document.createElement('tr');
  tr.innerHTML = `<th scope="row">${row.name}</th>` + ['tb2','tb3','lhtb','overall','step','time'].map(key => `<td>${row[key][0].toFixed(1)} ± ${row[key][1].toFixed(1)}</td>`).join('');
  tableBody.append(tr);
});

const methodSteps = [
  ['01 / PROPOSE & PROBE', 'Make the failure testable.', 'The implicit world model proposes repair hypotheses and diagnostic probes, estimates potential progress, and identifies relations between candidate repairs.'],
  ['02 / UPDATE & RANK', 'Let one attempt inform the next.', 'Observations and recorded relations update frontier priorities. Evidence from an attempted repair can also change the rank of related alternatives that have not just been executed.'],
  ['03 / GATE & EXECUTE', 'A high rank is only part of the decision.', 'The diagnostic gate separately checks that a frontier is available, supported by evidence, and targets an unresolved issue. If no frontier is eligible, the agent continues exploration.'],
  ['04 / VERIFY & RETAIN', 'Roll back the state. Keep what was learned.', 'The verifier checks the outcome and the controller retains progress or restores a checkpoint. Attempt history and observations remain in the persistent belief state to guide later recovery.']
];
document.querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => {
  const selected = Number(button.dataset.step);
  document.querySelectorAll('[data-step]').forEach(item => {
    item.classList.toggle('active', item === button);
    item.setAttribute('aria-pressed', String(item === button));
  });
  document.querySelector('.method-detail').dataset.stage = String(selected);
  ['#step-kicker','#step-title','#step-description'].forEach((selector, i) => { document.querySelector(selector).textContent = methodSteps[selected][i]; });
}));

document.querySelector('#copy-citation').addEventListener('click', async () => {
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(document.querySelector('#citation').textContent);
    status.textContent = 'BibTeX copied.';
    document.querySelector('#copy-citation').textContent = 'Copied ✓';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#citation'));
    selection.removeAllRanges(); selection.addRange(range);
    status.textContent = 'Citation selected. Press Ctrl+C (or ⌘C) to copy.';
  }
});

// Derive the visible transcript from the shipped captions to keep the two aligned.
fetch('assets/beliefweaver-short.vtt').then(response => {
  if (!response.ok) throw new Error('Captions unavailable');
  return response.text();
}).then(vtt => {
  const paragraphs = vtt.replace(/^\uFEFF/, '').split(/\r?\n\s*\r?\n/).filter(block => block.includes('-->')).map(block => block.split(/\r?\n/).filter(line => !line.includes('-->') && !/^\d+$/.test(line.trim())).join(' ').trim());
  if (paragraphs.length) {
    const wrapper = document.querySelector('#video-transcript');
    wrapper.replaceChildren();
    paragraphs.forEach(text => { const p = document.createElement('p'); p.textContent = text; wrapper.append(p); });
  }
}).catch(() => { /* The caption download remains available as a static fallback. */ });
