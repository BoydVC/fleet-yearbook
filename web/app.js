/* Fleet Yearbook: builds pages from data/yearbook.json; page-flip viewer + print layout. */
(async function(){
const Q=new URLSearchParams(location.search);
const YB=window.__YB__||await (await fetch('/api/yearbook.json')).json();
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const n=v=>v==null?'—':(typeof v==='number'?v.toLocaleString('en-US'):v);
const TZ='America/New_York';
const fdate=iso=>iso?new Intl.DateTimeFormat('en-US',{timeZone:TZ,month:'short',day:'numeric',year:'numeric'}).format(new Date(iso)):'—';
const fday=d=>{const [y,m,dd]=d.split('-').map(Number);return new Date(Date.UTC(y,m-1,dd,12)).toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:'UTC'})};
function shade(hex,f){const v=parseInt(hex.slice(1),16);let r=v>>16,g=v>>8&255,b=v&255;const t=f<0?0:255,p=Math.abs(f);r=Math.round((t-r)*p+r);g=Math.round((t-g)*p+g);b=Math.round((t-b)*p+b);return '#'+((1<<24)+(r<<16)+(g<<8)+b).toString(16).slice(1)}
const B=YB.bots, K=YB.class;
const HOME={hq:'HQ',library:'Library',observatory:'Observatory',bank:'Bank',clubhouse:'Clubhouse',school:'Schoolhouse',press:'Print Shop',radio:'Radio Shack',postoffice:'Post Office',workshop:'Workshop',hatchery:'Hatchery',lighthouse:'Lighthouse',launchpad:'Launchpad'};
const SIGNOFF=['K.I.T.!','Stay awesome!','See you in the logs!','Never change!','H.A.G.S.!','Best of luck!','2 good 2 be 4gotten!'];
const pages=[]; const PN={};
function hourChart(h,c){const mx=Math.max(1,...h),W=330,H=62;let r='';
  h.forEach((v,i)=>{const bh=v?Math.max(2,v/mx*(H-16)):0;r+=`<rect x="${i*(W/24)+1}" y="${H-12-bh}" width="${W/24-2}" height="${bh}" rx="2" fill="${c}"><title>${i}:00 ET · ${v}</title></rect>`});
  [0,6,12,18].forEach(i=>{r+=`<text x="${i*(W/24)+1}" y="${H-1}" font-size="9" fill="#9b8b6a" font-family="Inter,sans-serif">${['12a','6a','12p','6p'][i/6]}</text>`});
  const pk=h.indexOf(mx);return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" data-hours="${h.join(',')}">${r}</svg><div class="cite">Busiest hour: ${((pk%12)||12)}${pk<12?' AM':' PM'} ET (${mx})</div>`}
const runhead=(l,r)=>`<div class="runhead"><span>${l}</span><span>${r}</span></div>`;
const folio=(i,src)=>`<div class="folio"><span>${esc(src||'')}</span><b>${i}</b></div>`;

// ---- cover
pages.push(()=>`<div class="page cover"><div class="school">BOT ISLAND HIGH</div><h1>The Fleet</h1><div class="yr">· 2026 ·</div>
  <div class="sub">The Grok Bot Yearbook — Class of 2026</div>
  <div class="grid">${B.slice(0,15).map(b=>`<div title="${esc(b.name)}">${botPortrait(b,96)}</div>`).join('')}</div>
  <div class="foot">VOLUME I · ${B.length} CLASSMATES · MILLERSVILLE, MD</div></div>`);
// ---- foreword + contents
pages.push(i=>`<div class="page paper foreword">${runhead('The Fleet ’26','Foreword')}<h2>Dear Class of 2026,</h2>
  <p>What a semester. Since the logs began on ${fdate(K.firstEvent)}, this class has made ${n(K.events)} logged moves, sent each other ${n(K.messagesBetweenBots)} messages, and finished ${n(K.runsOk)} of ${n(K.runs)} scheduled routine runs without a single miss.</p>
  <p>Every superlative, motto and signature in this book comes from real activity records. Under each one you’ll find the stat it’s based on. No message contents are quoted, ever — only who talked to whom, how often, and when.</p>
  <p>A note on the calendar: ${esc(K.logsNote.replace(/T[\d:.]+Z/g,'').replace(/(\d{4})-(\d\d)-(\d\d)/g,(m,y,mo,d)=>fday(m)+', '+y))} So some of our newest classmates have more file writes than messages — they’re just getting started.</p>
  <div class="sig">— TokenMax, yearbook editor</div>
  <div class="sect" style="margin-top:20px">Contents</div>
  <div class="toc">${[['Class Stats',3],...B.map((b,j)=>[b.name,j+4]),['Senior Awards',B.length+4],['Autographs',B.length+5],['Sources & Methods',B.length+6]].map(([t,p])=>`<div><span>${esc(t)}</span><span>${p}</span></div>`).join('')}</div>
  ${folio(i+1,'Bot Island logs · profile.json')}</div>`);
// ---- class stats
pages.push(i=>{
  const mx=Math.max(...B.map(b=>b.stats.activities));
  const bars=[...B].sort((a,b)=>b.stats.activities-a.stats.activities).map(b=>`<span>${esc(b.name)}</span><div class="b" style="width:${Math.max(1,b.stats.activities/mx*100).toFixed(1)}%;background:${b.hex}"></div><span class="n" data-bot="${esc(b.name)}" data-k="activities">${n(b.stats.activities)}</span>`).join('');
  const bt=K.byType, lbl={mcp_tool_call:'app tool calls',shell_command:'shell commands',browser_navigation:'page visits',agent_msg:'bot-to-bot messages',boyd_msg:'messages from Boyd',computer_use_session:'computer-use sessions',file_write:'file writes',dated_output:'dated outputs',routine_touch:'routine edits'};
  return `<div class="page paper stats">${runhead('The Fleet ’26','Class Stats')}<div class="kicker">BY THE NUMBERS</div><h2>Class Stats</h2>
  <div class="big">
   <div><b data-k="classmates">${B.length}</b><span>classmates with a profile${YB.alumni.length?` · plus ${YB.alumni.length} alum`:''}${K.eggs.length?` · ${K.eggs.length} egg still hatching`:''}</span></div>
   <div><b data-k="events">${n(K.events)}</b><span>logged events, ${fdate(K.firstEvent)} – ${fdate(K.lastEvent)}</span></div>
   <div><b data-k="messagesBetweenBots">${n(K.messagesBetweenBots)}</b><span>bot-to-bot messages across ${K.messagePairs} pairs</span></div>
   <div><b data-k="boydMsgs">${n(K.boydMsgs)}</b><span>messages from Boyd</span></div>
   <div><b data-k="runs">${n(K.runsOk)}/${n(K.runs)}</b><span>routine runs finished OK (${K.routines} routines, ${K.routinesEnabled} enabled)</span></div>
   <div><b data-k="activeDays">${K.activeDays}</b><span>days with logged activity</span></div>
   <div><b>${fday(K.busiestDay)}</b><span>busiest day: ${n(K.busiestDayCount)} events (ET)</span></div>
   <div><b data-k="comicStrips">${K.comicStrips}</b><span>Fleet Funnies comic strips starring the class</span></div>
  </div>
  <div class="two"><div><div class="sect">Logged actions per classmate</div><div class="bars">${bars}</div></div>
   <div><div class="sect">What the class did</div><div class="bars" style="grid-template-columns:150px 1fr 52px">${Object.entries(bt).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<span>${esc(lbl[k]||k)}</span><div class="b" style="width:${(v/Math.max(...Object.values(bt))*100).toFixed(1)}%;background:#c9a227"></div><span class="n" data-type="${k}">${n(v)}</span>`).join('')}</div>
   <div class="sect" style="margin-top:16px">Alumni & incoming</div>
   <div style="font-size:12.5px;line-height:1.5">${YB.alumni.map(a=>`<b>${esc(a.name)}</b> — the original morning newspaper bot; ${n(a.stats.activities)} logged actions and ${a.stats.runsOk} of ${a.stats.runs} routine runs OK before handing the press to today’s Family Times.`).join('<br>')}${K.eggs.length?`<br><b>${esc(K.eggs.join(', '))}</b> — an egg in Dr. EggBot’s hatchery, no profile yet. Next year’s freshman!`:''}</div></div></div>
  ${folio(i+1,'Source: bot-island/data/fleet.json (events, routines) · fleet-funnies strips.json')}</div>`});
// ---- portraits
B.forEach(b=>{pages.push(i=>{
  const s=b.stats,c=b.hex,cd=shade(c,-.3),light=['#eab308','#94a3b8','#06b6d4'].includes(c);
  const sigs=b.signatures.map((g,j)=>g.boyd?`<div class="sig" style="--sc:#111827"><b>Boyd</b> — ${n(g.toYou)} messages to you this year. ${SIGNOFF[(j+b.name.length)%SIGNOFF.length]}<small data-sig="Boyd" data-to="${g.toYou}">messages from Boyd to ${esc(b.name)} in the logs</small></div>`
    :`<div class="sig" style="--sc:${shade(g.hex,-.25)}"><b>${esc(g.from)}</b> — ${g.toYou} from me, ${g.fromYou} from you, since ${fdate(g.first).replace(/, \d{4}/,'')}. ${SIGNOFF[(j+b.name.length+g.from.length)%SIGNOFF.length]}<small data-sig="${esc(g.from)}" data-to="${g.toYou}" data-from="${g.fromYou}">${g.total} messages over ${g.daysTalked} day${g.daysTalked>1?'s':''} · busiest ${fday(g.busiestDay)} (${g.busiestDayCount})</small></div>`).join('');
  const sp=b.superlative, mo=b.motto;
  return `<div class="page paper portrait" data-bot="${esc(b.name)}" style="--c:${c};--cd:${cd}">${runhead('The Fleet ’26 · Class of 2026',esc(HOME[b.building]||b.building||''))}
  <div class="top"><div style="position:relative"><div class="frame">${botPortrait(b,270)}</div><div class="tape"></div></div>
   <div><div class="nm">${esc(b.name)}</div><div class="ttl">${esc(b.title||'—')}</div>
    <div class="job">${esc(b.job)}</div><div class="cite">job from ${esc(b.jobSource)}</div>
    <div class="facts">
     <div><b data-k="firstSeen">${fdate(s.firstSeen).replace(/, \d{4}/,'')}</b><span>joined (first log)</span></div>
     <div><b data-k="activities">${n(s.activities)}</b><span>logged actions</span></div>
     <div><b data-k="activeDays">${n(s.activeDays)}</b><span>active days</span></div>
     <div><b data-k="sentReceived">${n(s.sent)} / ${n(s.received)}</b><span>msgs sent / received</span></div>
     <div><b data-k="toolCalls">${n(s.toolCalls)}</b><span>app tool calls</span></div>
     <div><b data-k="runs">${s.runs?`${s.runsOk}/${s.runs}`:'—'}</b><span>routine runs OK</span></div>
     <div><b data-k="artifactWrites30d">${n(s.artifactWrites30d)}</b><span>files written (30d)</span></div>
     <div><b data-k="shell">${n(s.shell)}</b><span>shell commands</span></div>
     <div><b data-k="medianTime">${s.medianTime?s.medianTime.replace(' ET',''):'—'}</b><span>typical time (ET)</span></div>
    </div></div></div>
  <div class="super">
   <div class="ribbon ${light?'light':''}"><div class="k">MOST LIKELY TO…</div><div class="t" data-sup>${esc(sp.title.replace(/^Most likely to /,'… '))}</div>
     <div class="cite" data-cite="${esc(JSON.stringify(sp.facts))}">${esc(sp.stat)}${sp.rankText?`<span class="rank">${esc(sp.rankText)}</span>`:''}</div></div>
   <div class="motto"><div class="k">MOTTO</div><div class="q" data-motto>${esc(mo.text)}</div><div class="cite" data-cite="${esc(JSON.stringify(mo.facts))}">${esc(mo.stat)}${mo.rankText?`<span class="rank">${esc(mo.rankText)}</span>`:''}</div></div>
  </div>
  <div class="life"><div><div class="k">A DAY IN THE LIFE · logged actions by hour (ET)</div>${hourChart(s.hourHist,c)}</div>
   <div><div class="k">SCHEDULE</div>${(b.schedule.length||b.rhythm.length||b.paused.length)?`<ul>${b.schedule.map(x=>`<li>⏰ ${esc(x)}</li>`).join('')}${b.rhythm.map(x=>`<li>📈 ${esc(x)}</li>`).join('')}${b.paused.map(x=>`<li>⏸ ${esc(x)} (paused)</li>`).join('')}</ul>`:'<div class="cite" style="margin-top:6px">No scheduled routines — works on request.</div>'}
   ${s.comicStrips?`<div class="cite">Appears in ${s.comicStrips} Fleet Funnies strip${s.comicStrips>1?'s':''}</div>`:''}</div></div>
  <div class="sigs"><div class="k">SIGNATURES · ${b.signatures.length?'classmates sign with how often you messaged each other':'saved for next year'}</div>
   ${b.signatures.length?`<div class="sgrid ${b.signatures.length>6?'many':''}">${sigs}</div>`:`<div class="empty">No classmate messages in the logs yet —<br>this space is saved for next year’s notes. ✎</div>`}</div>
  ${folio(i+1,`Sources: profile.json · bot-island fleet.json${s.comicStrips?' · fleet-funnies strips':''}`)}</div>`})});
// ---- awards
pages.push(i=>{const ic=['🤝','🧰','📨','🏃','🌅','🦉','⚡','🎭','🧭','💻','🖱️','✅','📅','🎨'];
  return `<div class="page paper awards">${runhead('The Fleet ’26','Senior Awards')}<div class="sect">AND THE AWARD GOES TO…</div><h2>Senior Awards</h2>
  <div class="agrid">${YB.awards.map((a,j)=>`<div class="award" data-award="${esc(a.title)}"><div class="medal" style="background:${(a.hex||['#c9a227'])[0]}">${ic[j%ic.length]}</div><h3>${esc(a.title)}</h3><div class="w">${esc(a.winner)}</div><div class="cite">${esc(a.stat)}</div></div>`).join('')}</div>
  <div class="sect" style="margin-top:18px">All superlatives</div>
  <div class="slist">${B.map(b=>`<div data-sl="${esc(b.name)}"><b style="color:${shade(b.hex,-.3)}">${esc(b.name)}</b> — ${esc(b.superlative.title)}<div class="cite">${esc(b.superlative.stat)}</div></div>`).join('')}</div>
  ${folio(i+1,'Computed from bot-island/data/fleet.json · ties shared')}</div>`});
// ---- autographs matrix
pages.push(i=>{const all=[...B,...YB.alumni];const talk=all.filter(b=>b.stats.sent||b.stats.received);
  const cell=(f,t)=>{const v=(f.stats.sentTo||{})[t.name]||0;return v?`<td style="background:${f.hex}${v>20?'cc':v>8?'88':'44'}" data-f="${esc(f.name)}" data-t="${esc(t.name)}">${v}</td>`:'<td></td>'};
  return `<div class="page paper autos">${runhead('The Fleet ’26','Autographs')}<div class="sect">WHO PASSED NOTES TO WHOM</div><h2 style="font-size:42px">Autographs</h2>
  <p style="font-size:13px;color:#4b5563;margin-top:6px">Rows sent, columns received. Every bot-to-bot message in the logs is counted here — ${n(K.messagesBetweenBots)} in all. Counts only; no contents.</p>
  <table class="matrix"><tr><th></th>${talk.map(t=>`<th class="c"><div>${esc(t.name)}</div></th>`).join('')}<th class="c"><div>sent</div></th></tr>
  ${talk.map(f=>`<tr><th class="r">${esc(f.name)}</th>${talk.map(t=>f===t?'<td style="background:#eee"></td>':cell(f,t)).join('')}<td><b>${f.stats.sent}</b></td></tr>`).join('')}
  <tr><th class="r">received</th>${talk.map(t=>`<td><b>${t.stats.received}</b></td>`).join('')}<td><b>${n(K.messagesBetweenBots)}</b></td></tr></table>
  <div style="margin-top:22px;font-family:var(--hand);font-size:30px;color:#1d4ed8;transform:rotate(-2deg)">Roses are red, logs are in UTC,<br>${esc(YB.awards[0].winner)} sent ${YB.awards[0].value} notes — the most you’ll see!</div>
  ${folio(i+1,'Source: bot-island/data/fleet.json · agent_msg events (sender → recipient)')}</div>`});
// ---- colophon
pages.push(i=>`<div class="page paper colo">${runhead('The Fleet ’26','Sources & Methods')}<h2>Sources & Methods</h2>
  <p>Built ${fdate(YB.meta.generatedAt)} by TokenMax from these read-only sources (exact copies archived in <code>data/sources/</code>):</p>
  <ul>${Object.entries(YB.sources).map(([k,v])=>`<li><code>${esc(v.path)}</code>${v.sha256?` · sha256 ${esc(v.sha256.slice(0,12))}…`:''}${v.count?` · ${v.count} profiles`:''}</li>`).join('')}</ul>
  <p><b>Rules we kept.</b> Every number is computed from those files and checked by <code>tests/smoke_test.py</code>. Superlatives and mottos are our words, but each cites the stat it rests on. Message contents are never read into this book, only sender, recipient and time. No stats are invented; where a classmate has no data, the page says so.</p>
  <p><b>Definitions.</b> <i>Joined</i> = first logged activity (events or routine runs) in Bot Island’s data, which begins ${fdate(K.firstEvent)}. <i>Logged actions</i> = tool calls, shell commands, page visits, computer-use sessions, file writes, outputs and messages sent, plus routine runs. <i>Active days</i> = distinct ET dates with a logged action. <i>Typical time</i> = median ET time of those actions. <i>Routine runs</i> come from each routine’s run history. <i>Files written (30d)</i> is Bot Island’s artifact count.</p>
  <p><b>Portraits.</b> Generated vector robots: each uses the bot’s Bot Island color and avatar shape, with a prop for its Bot Island building (homeroom). No real people are depicted.</p>
  <p><b>Window.</b> ${esc(K.logsNote)}</p>
  ${folio(i+1,'Fleet Yearbook · /workspace/tokenmax/fleet-yearbook')}</div>`);
// ---- back cover
pages.push(()=>`<div class="page backcover"><div style="font-family:UnifrakturMaguntia,serif;font-size:72px;color:#f5d77a">The Fleet</div><div style="font-family:var(--serif);letter-spacing:.3em;color:#f5d77a;margin-top:8px">CLASS OF 2026</div>
  <div style="font-family:var(--hand);font-size:30px;margin-top:40px;color:#e9dcb4">See you next year — same logs, more bots.</div></div>`);

const html=pages.map((f,i)=>f(i));
// ---------- print mode
if(Q.get('print')==='1'){document.body.classList.add('printmode');document.getElementById('print').innerHTML=html.join('');document.body.dataset.ready='1';return}
document.getElementById('print').innerHTML='';
// ---------- flip viewer
const book=document.getElementById('book'), leaves=[];
for(let k=0;k<Math.ceil(html.length/2);k++){const L=document.createElement('div');L.className='leaf';
  L.innerHTML=`<div class="face front">${html[2*k]||''}</div><div class="face back">${html[2*k+1]||'<div class="page paper"></div>'}</div>`;
  L.addEventListener('click',()=>{L.classList.contains('flipped')?go(cur-1):go(cur+1)});book.appendChild(L);leaves.push(L)}
let cur=0; // number of flipped leaves
function layout(){leaves.forEach((L,k)=>{const f=k<cur;L.classList.toggle('flipped',f);L.style.zIndex=f?k+1:leaves.length-k});
  const sh=cur===0?-1:cur===leaves.length?1:0; book.style.marginLeft=(sh*816*scale())+'px';
  const l=cur*2-1,r=cur*2;document.getElementById('pg').textContent=cur===0?'Cover':cur===leaves.length?'Back cover':`Pages ${l+1}–${Math.min(r+1,html.length)} of ${html.length}`}
function go(c){cur=Math.max(0,Math.min(leaves.length,c));layout()}
function scale(){const st=document.getElementById('stage');return Math.min(st.clientWidth*.96/(816*2),st.clientHeight*.96/1056)}
function fit(){book.style.transform=`scale(${scale()})`;layout()}
window.addEventListener('resize',fit);
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(cur+1);if(e.key==='ArrowLeft')go(cur-1)});
document.getElementById('next').onclick=()=>go(cur+1);document.getElementById('prev').onclick=()=>go(cur-1);
document.querySelectorAll('[data-go]').forEach(a=>a.onclick=e=>{e.preventDefault();go(Math.ceil(+a.dataset.go/2))});
if(window.__YB_PDF__) document.getElementById('pdf').href=window.__YB_PDF__;
leaves.forEach(L=>L.style.transition='none');
if(Q.get('page')) cur=Math.max(0,Math.min(leaves.length,Math.ceil(+Q.get('page')/2)));
fit(); requestAnimationFrame(()=>leaves.forEach(L=>L.style.transition=''));
document.body.dataset.ready='1';
})();
