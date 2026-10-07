/* Generated vector portraits: friendly robots built from each bot's Bot Island color, avatar shape
   and building (homeroom). Deterministic per bot id. No real people. */
(function(){
function hash(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
function shade(hex,f){const n=parseInt(hex.slice(1),16);let r=n>>16,g=n>>8&255,b=n&255;
  const t=f<0?0:255,p=Math.abs(f);r=Math.round((t-r)*p+r);g=Math.round((t-g)*p+g);b=Math.round((t-b)*p+b);return '#'+((1<<24)+(r<<16)+(g<<8)+b).toString(16).slice(1)}
function headPath(shape,cx,cy,w,h){
  const x0=cx-w/2,y0=cy-h/2,x1=cx+w/2,y1=cy+h/2;
  switch(shape){
    case 'circle': return `M${cx} ${y0}a${w/2} ${h/2} 0 1 1 -0.1 0z`;
    case 'pebble': return `M${x0+w*.1} ${cy}C${x0} ${y0+h*.05} ${x1-w*.05} ${y0-h*.08} ${x1} ${cy-h*.05}C${x1+w*.04} ${y1} ${x0+w*.25} ${y1+h*.06} ${x0+w*.1} ${cy}z`;
    case 'blob': return `M${cx} ${y0}C${x1+w*.05} ${y0-h*.02} ${x1+w*.08} ${cy+h*.1} ${x1-w*.08} ${y1}C${cx+w*.1} ${y1+h*.08} ${x0-w*.02} ${y1+h*.02} ${x0+w*.02} ${cy+h*.05}C${x0-w*.05} ${y0+h*.15} ${x0+w*.2} ${y0} ${cx} ${y0}z`;
    case 'teardrop': return `M${cx} ${y0-h*.08}C${cx+w*.15} ${y0+h*.12} ${x1} ${cy-h*.05} ${x1} ${cy+h*.12}A${w/2} ${h*.38} 0 0 1 ${x0} ${cy+h*.12}C${x0} ${cy-h*.05} ${cx-w*.15} ${y0+h*.12} ${cx} ${y0-h*.08}z`;
    case 'cloud': {const r=w*.2;return `M${x0+r} ${y1}a${r} ${r} 0 0 1 -${r*.2} -${r*1.9}a${r*1.1} ${r*1.1} 0 0 1 ${r*1.5} -${r*1.6}a${r*1.3} ${r*1.3} 0 0 1 ${r*2.3} ${r*.1}a${r*1.1} ${r*1.1} 0 0 1 ${r*1.3} ${r*1.6}a${r} ${r} 0 0 1 -${r*.4} ${r*1.8}z`}
    case 'wedge': return `M${x0+w*.08} ${y0+h*.1}Q${cx} ${y0-h*.12} ${x1-w*.08} ${y0+h*.1}L${x1-w*.18} ${y1-h*.05}Q${cx} ${y1+h*.08} ${x0+w*.18} ${y1-h*.05}z`;
    case 'hex': {const p=[];for(let i=0;i<6;i++){const a=Math.PI/3*i+Math.PI/6;p.push(`${cx+w/2*Math.cos(a)} ${cy+h/2*Math.sin(a)}`)}return 'M'+p.join('L')+'z'}
    case 'sparkle': {const p=[];for(let i=0;i<16;i++){const a=Math.PI/8*i-Math.PI/2,r=i%2?.72:1,rr=i%4==0?1.04:r;p.push(`${cx+w/2*rr*Math.cos(a)} ${cy+h/2*rr*Math.sin(a)}`)}return 'M'+p.join('L')+'z'}
    case 'tablet': return `M${x0+w*.12} ${y0-h*.04}h${w*.76}a${w*.12} ${w*.12} 0 0 1 ${w*.12} ${w*.12}v${h*.84}a${w*.12} ${w*.12} 0 0 1 -${w*.12} ${w*.12}h-${w*.76}a${w*.12} ${w*.12} 0 0 1 -${w*.12} -${w*.12}v-${h*.84}a${w*.12} ${w*.12} 0 0 1 ${w*.12} -${w*.12}z`;
    default: /* squircle */ return `M${cx} ${y0}C${x1-w*.02} ${y0} ${x1} ${y0+h*.02} ${x1} ${cy}C${x1} ${y1-h*.02} ${x1-w*.02} ${y1} ${cx} ${y1}C${x0+w*.02} ${y1} ${x0} ${y1-h*.02} ${x0} ${cy}C${x0} ${y0+h*.02} ${x0+w*.02} ${y0} ${cx} ${y0}z`;
  }
}
function accessory(b,c,cx,top,dark){
  const ink='#1f2937';
  switch(b){
    case 'hq': return `<path d="M${cx-9} 236l9 10 9-10-5 34h-8z" fill="${shade(c,-.45)}"/><path d="M${cx-9} 236h18l-9 10z" fill="${shade(c,-.25)}"/>`; // tie
    case 'library': return `<g fill="none" stroke="${ink}" stroke-width="4"><circle cx="${cx-26}" cy="148" r="17"/><circle cx="${cx+26}" cy="148" r="17"/><path d="M${cx-9} 148h18"/></g>`; // glasses
    case 'observatory': return `<g transform="translate(${cx+62} ${top-6}) rotate(-30)"><rect x="-6" y="-26" width="12" height="40" rx="4" fill="${ink}"/><rect x="-9" y="-32" width="18" height="10" rx="3" fill="#fde047"/></g><path d="M${cx-70} ${top+4}l4 9 10 1-8 6 3 10-9-6-9 6 3-10-8-6 10-1z" fill="#fde047"/>`; // spyglass + star
    case 'bank': return `<path d="M${cx-18} 238l18 9 18-9v18l-18-9-18 9z" fill="${shade(c,-.45)}"/><circle cx="${cx}" cy="247" r="4" fill="#fde047"/>`; // bow tie
    case 'clubhouse': return `<rect x="${cx-62}" y="${top+16}" width="124" height="12" rx="6" fill="#f472b6"/><path d="M${cx+30} 240q14 18 0 34" stroke="${ink}" stroke-width="3" fill="none"/><circle cx="${cx+30}" cy="276" r="6" fill="#fbbf24"/>`; // headband + whistle
    case 'school': return `<path d="M${cx-58} ${top+2}l58-24 58 24-58 24z" fill="${ink}"/><rect x="${cx-32}" y="${top+6}" width="64" height="18" fill="${ink}"/><path d="M${cx+44} ${top+6}v28" stroke="#fbbf24" stroke-width="3"/><circle cx="${cx+44}" cy="${top+36}" r="4" fill="#fbbf24"/>`; // grad cap
    case 'press': return `<path d="M${cx-62} ${top+14}h124l-14-10h-96z" fill="${ink}"/><path d="M${cx-40} ${top+6}q40-34 80 0z" fill="${ink}"/><rect x="${cx+14}" y="${top-12}" width="26" height="14" fill="#fff" stroke="${ink}"/><text x="${cx+27}" y="${top-2}" font-size="8" text-anchor="middle" font-family="Oswald,sans-serif" fill="${ink}">PRESS</text>`; // fedora
    case 'radio': return `<path d="M${cx-62} 150q0-74 62-74t62 74" fill="none" stroke="${ink}" stroke-width="7"/><rect x="${cx-74}" y="136" width="20" height="34" rx="8" fill="${ink}"/><rect x="${cx+54}" y="136" width="20" height="34" rx="8" fill="${ink}"/>`; // headphones
    case 'postoffice': return `<rect x="${cx-58}" y="${top-4}" width="116" height="22" rx="6" fill="#1d4ed8"/><rect x="${cx-58}" y="${top+12}" width="80" height="8" rx="4" fill="#1e3a8a"/><g transform="translate(${cx+16} 246)"><rect width="34" height="22" rx="3" fill="#fff" stroke="${ink}" stroke-width="2"/><path d="M0 0l17 13 17-13" fill="none" stroke="${ink}" stroke-width="2"/></g>`; // mail cap + letter
    case 'workshop': return `<path d="M${cx-60} ${top+14}q0-46 60-46t60 46z" fill="#facc15" stroke="#a16207" stroke-width="3"/><rect x="${cx-68}" y="${top+10}" width="136" height="10" rx="5" fill="#eab308"/><rect x="${cx-5}" y="${top-30}" width="10" height="40" fill="#ca8a04"/>`; // hard hat
    case 'hatchery': return `<ellipse cx="${cx+46}" cy="258" rx="17" ry="22" fill="#fef3c7" stroke="#d6a65a" stroke-width="2"/><path d="M${cx+30} 258l6-6 6 6 6-6 6 6 6-6" fill="none" stroke="#d6a65a" stroke-width="2"/>`; // egg
    case 'lighthouse': return `<g transform="translate(${cx} ${top-34})"><circle r="15" fill="#fde047"/><rect x="-7" y="12" width="14" height="10" rx="2" fill="#9ca3af"/><g stroke="#fde047" stroke-width="3"><path d="M-26 0h-10M26 0h10M0 -24v-10M-19 -19l-7 -7M19 -19l7 -7"/></g></g>`; // light bulb idea
    case 'launchpad': return `<g transform="translate(${cx+44} 254) rotate(35)"><path d="M0 -24q10 12 8 30h-16q-2-18 8-30z" fill="#e5e7eb" stroke="${ink}" stroke-width="2"/><circle cy="-6" r="4" fill="#38bdf8"/><path d="M-8 6l-6 8h28l-6-8" fill="#ef4444"/><path d="M-4 14q4 12 8 0" fill="#f97316"/></g>`; // rocket
    default: return '';
  }
}
window.botPortrait=function(bot,size){
  size=size||300; const c=bot.hex||'#94a3b8', h=hash(bot.id||bot.name), cx=150;
  const eyes=h%4, mouth=(h>>3)%3, ant=(h>>5)%3, cheeks=(h>>7)%2;
  const id='p'+(h%100000);
  const back=`<defs><radialGradient id="${id}bg" cx="35%" cy="30%" r="85%"><stop offset="0" stop-color="${shade(c,.75)}"/><stop offset=".55" stop-color="${shade(c,.35)}"/><stop offset="1" stop-color="${shade(c,-.35)}"/></radialGradient>
    <linearGradient id="${id}hd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${shade(c,.25)}"/><stop offset="1" stop-color="${shade(c,-.15)}"/></linearGradient>
    <filter id="${id}n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="${h%50}"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .10 0"/><feComposite in2="SourceGraphic" operator="in"/></filter></defs>
    <rect width="300" height="300" fill="url(#${id}bg)"/><rect width="300" height="300" fill="#fff" filter="url(#${id}n)"/>
    <g opacity=".18" stroke="#fff" stroke-width="2" fill="none"><path d="M-20 ${200+h%40}q80-60 170-10t170 -30"/><path d="M-20 ${240+h%30}q90-50 180 0t160 -20"/></g>`;
  const hw=bot.shape==='tablet'?120:bot.shape==='sparkle'?168:150, hh=bot.shape==='tablet'?150:bot.shape==='sparkle'?168:128, top=140-hh/2;
  // body + neck
  const body=`<path d="M${cx-80} 300q4-62 80-66t80 66z" fill="${shade(c,-.2)}"/><path d="M${cx-80} 300q4-62 80-66t80 66" fill="none" stroke="${shade(c,-.45)}" stroke-width="3"/>
    <rect x="${cx-14}" y="${140+hh/2-6}" width="28" height="${236-(140+hh/2)+8}" fill="${shade(c,-.35)}"/>
    <circle cx="${cx-34}" cy="272" r="5" fill="${shade(c,.5)}"/><circle cx="${cx-18}" cy="278" r="5" fill="${shade(c,.35)}"/>`;
  const antenna=ant===0?`<path d="M${cx} ${top+4}v-26" stroke="${shade(c,-.45)}" stroke-width="4"/><circle cx="${cx}" cy="${top-24}" r="8" fill="${shade(c,.55)}" stroke="${shade(c,-.45)}" stroke-width="3"/>`
    :ant===1?`<path d="M${cx-24} ${top+8}l-14-26M${cx+24} ${top+8}l14-26" stroke="${shade(c,-.45)}" stroke-width="4"/><circle cx="${cx-38}" cy="${top-18}" r="6" fill="#fde047"/><circle cx="${cx+38}" cy="${top-18}" r="6" fill="#fde047"/>`
    :`<path d="M${cx} ${top+4}q14-18 0-30" fill="none" stroke="${shade(c,-.45)}" stroke-width="4"/><circle cx="${cx}" cy="${top-28}" r="6" fill="#fff"/>`;
  const head=`<path d="${headPath(bot.shape,cx,140,hw,hh)}" fill="url(#${id}hd)" stroke="${shade(c,-.5)}" stroke-width="4" stroke-linejoin="round"/>`;
  const face=`<rect x="${cx-48}" y="118" width="96" height="62" rx="22" fill="#0f172a" opacity=".9"/>`;
  const ec='#a5f3fc';
  const eyeSvg=eyes===0?`<circle cx="${cx-20}" cy="145" r="8" fill="${ec}"/><circle cx="${cx+20}" cy="145" r="8" fill="${ec}"/><circle cx="${cx-17}" cy="142" r="2.5" fill="#fff"/><circle cx="${cx+23}" cy="142" r="2.5" fill="#fff"/>`
    :eyes===1?`<path d="M${cx-30} 148q10-12 20 0M${cx+10} 148q10-12 20 0" stroke="${ec}" stroke-width="5" fill="none" stroke-linecap="round"/>`
    :eyes===2?`<rect x="${cx-34}" y="138" width="68" height="13" rx="6.5" fill="${ec}"/><rect x="${cx-26}" y="141" width="18" height="4" rx="2" fill="#fff" opacity=".8"/>`
    :`<rect x="${cx-28}" y="138" width="14" height="14" rx="3" fill="${ec}"/><rect x="${cx+14}" y="138" width="14" height="14" rx="3" fill="${ec}"/>`;
  const mouthSvg=mouth===0?`<path d="M${cx-14} 162q14 12 28 0" stroke="${ec}" stroke-width="4" fill="none" stroke-linecap="round"/>`
    :mouth===1?`<path d="M${cx-16} 160h32q-4 12-16 12t-16-12z" fill="${ec}"/>`
    :`<path d="M${cx-18} 164h36" stroke="${ec}" stroke-width="4" stroke-dasharray="5 4" stroke-linecap="round"/>`;
  const cheek=cheeks?`<circle cx="${cx-40}" cy="164" r="6" fill="#fb7185" opacity=".55"/><circle cx="${cx+40}" cy="164" r="6" fill="#fb7185" opacity=".55"/>`:'';
  const ears=bot.shape==='sparkle'?'':`<rect x="${cx-hw/2-12}" y="128" width="14" height="30" rx="6" fill="${shade(c,-.3)}"/><rect x="${cx+hw/2-2}" y="128" width="14" height="30" rx="6" fill="${shade(c,-.3)}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="${size}" height="${size}" role="img" aria-label="Robot portrait of ${bot.name}">${back}${body}${antenna}${ears}${head}${face}${eyeSvg}${mouthSvg}${cheek}${accessory(bot.building,c,cx,top,false)}</svg>`;
};
})();
