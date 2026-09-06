(function(){
  "use strict";

  /* Each page is now its own URL. Links shared before that change point at
     #hash sections on the homepage, so send those on to the real page. */
  var LEGACY = { home:"/", visit:"/why-visit/", menu:"/menu/",
                 roasts:"/roasts/", about:"/who-we-are/", find:"/find-us/" };
  var landing = LEGACY[(location.hash || "").slice(1)];
  if (landing && landing !== location.pathname) { location.replace(landing); return; }


  /* ---------- hamburger drawer ---------- */
  var toggle = document.getElementById("navToggle");
  var drawer = document.getElementById("drawer");
  function closeDrawer(){
    if (!toggle) return;
    toggle.setAttribute("aria-expanded","false");
    drawer.classList.remove("open");
  }
  function openDrawer(){
    toggle.setAttribute("aria-expanded","true");
    drawer.classList.add("open");
  }
  if (toggle) {
    toggle.addEventListener("click", function(){
      var open = toggle.getAttribute("aria-expanded") === "true";
      if (open) closeDrawer(); else openDrawer();
    });
    document.addEventListener("keydown", function(e){
      if (e.key === "Escape") closeDrawer();
    });
    document.addEventListener("click", function(e){
      if (!drawer.classList.contains("open")) return;
      if (drawer.contains(e.target) || toggle.contains(e.target)) return;
      closeDrawer();
    });
  }

  /* ---------- sliding nav indicator (desktop) ---------- */
  var navind = document.getElementById("navind");
  var navwrap = document.getElementById("nav");
  function moveIndicator(){
    if (!navind || !navwrap) return;
    var current = navwrap.querySelector('.navbtn[aria-current="page"]');
    if (!current || navwrap.offsetParent === null) { navind.classList.remove("ready"); return; }
    var wrapRect = navwrap.getBoundingClientRect(), r = current.getBoundingClientRect();
    navind.style.width = r.width + "px";
    navind.style.transform = "translateX(" + (r.left - wrapRect.left + navwrap.scrollLeft) + "px)";
    navind.classList.add("ready");
  }
  window.addEventListener("resize", moveIndicator);

  /* sticky offset for the menu tabs = header + nav */
  function setStick(){
    var h = document.querySelector(".topbar").offsetHeight + document.querySelector(".mainnav").offsetHeight;
    document.documentElement.style.setProperty("--stick", h + "px");
    document.querySelector(".mainnav").style.top = document.querySelector(".topbar").offsetHeight + "px";
  }
  window.addEventListener("resize", setStick);

  /* ---------------- ticker ---------------- */
  var phrases = ["Roasts Wednesday &amp; Sunday","Cup of tea <b>£1.50</b>","Scone, jam &amp; clotted cream <b>£3.50</b>","The Belly Buster <b>£13.80</b>","Open Wed, Sat &amp; Sun 9–5","Homemade cottage pie","Stall 6 — past the stalls, far corner"];
  var half = phrases.map(function(p){ return "<span>"+p+"</span><span>✦</span>"; }).join("");
  var tick = document.getElementById("tick");
  if (tick) tick.innerHTML = half + half;
  var phrases2 = ["Stall 6, Par Market","Open <b>Wed · Sat · Sun</b>","9am – 5pm","Order at the counter with your table number","Roast dinners <b>from £8.00</b>","Jacket, salad &amp; coleslaw <b>£4.80</b>"];
  var half2 = phrases2.map(function(p){ return "<span>"+p+"</span><span>✦</span>"; }).join("");
  var tick2 = document.getElementById("tick2");
  if (tick2) tick2.innerHTML = half2 + half2;

  /* ---------------- hours / status ---------------- */
  var OPEN = {0:[9,17], 3:[9,17], 6:[9,17]};
  var DAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  function fmtHour(h){ return h === 12 ? "12pm" : (h > 12 ? (h-12)+"pm" : h+"am"); }

  function renderHours(){
    var box = document.getElementById("hours");
    if (!box) return;
    var today = new Date().getDay();
    box.innerHTML = [1,2,3,4,5,6,0].map(function(d){
      var o = OPEN[d];
      var cls = (d === today ? "today " : "") + (o ? "" : "shut");
      return '<li class="'+cls.trim()+'"><span class="day">'+DAYS[d]+'</span><span>'+
             (o ? fmtHour(o[0])+" – "+fmtHour(o[1]) : "Closed")+'</span></li>';
    }).join("");
  }

  function updateStatus(){
    var now = new Date(), d = now.getDay(), h = now.getHours(), m = now.getMinutes();
    var el = document.getElementById("status"), txt = document.getElementById("statusText");
    var o = OPEN[d];
    if (o && h >= o[0] && h < o[1]) {
      el.classList.add("is-open");
      txt.textContent = ((o[1]-h)*60 - m) <= 60 ? "Open — last hour, closes 5pm" : "Open now until 5pm";
      return;
    }
    el.classList.remove("is-open");
    if (o && h < o[0]) { txt.textContent = "Closed — opens at 9am today"; return; }
    for (var i = 1; i <= 7; i++){
      var nd = (d+i) % 7;
      if (OPEN[nd]) { txt.textContent = "Closed — opens " + (i === 1 ? "tomorrow" : DAYS[nd]) + " at 9am"; return; }
    }
  }

  /* ---------------- roast countdown ---------------- */
  function nextRoast(){
    var now = new Date();
    for (var i = 0; i < 8; i++){
      var t = new Date(now.getFullYear(), now.getMonth(), now.getDate()+i, 9, 0, 0);
      if ((t.getDay() === 0 || t.getDay() === 3) && t > now) return t;
    }
    return null;
  }

  function renderCountdown(){
    var el = document.getElementById("countdown");
    if (!el) return;
    var now = new Date(), d = now.getDay(), h = now.getHours();
    if ((d === 0 || d === 3) && h >= 9 && h < 17) {
      el.innerHTML = '<div class="cd-cell" style="min-width:auto;padding:14px 24px"><b>Today</b><small>gravy is on</small></div>';
      return;
    }
    var t = nextRoast();
    if (!t) { el.innerHTML = ""; return; }
    var diff = Math.max(0, t - now);
    var mins = Math.floor(diff/60000) % 60;
    var tick = (el.dataset.mins !== undefined && el.dataset.mins !== String(mins)) ? " tick" : "";
    el.dataset.mins = String(mins);
    el.innerHTML =
      '<div class="cd-cell'+tick+'"><b>'+Math.floor(diff/86400000)+'</b><small>days</small></div>' +
      '<div class="cd-cell'+tick+'"><b>'+(Math.floor(diff/3600000) % 24)+'</b><small>hours</small></div>' +
      '<div class="cd-cell'+tick+'"><b>'+mins+'</b><small>mins</small></div>' +
      '<div class="cd-cell" style="min-width:auto"><b>'+DAYS[t.getDay()].slice(0,3)+'</b><small>next roast</small></div>';
  }

  /* ---------------- menu ---------------- */
  var MENU = [
    { cat:"Breakfast", title:"Breakfast", note:"Served all day. Add chips to any breakfast for £1.50.", items:[
      ["All day breakfast","1 bacon, 1 sausage, 1 egg, fried bread, beans and tomatoes","£6.00"],
      ["All day breakfast with chips","","£7.50"],
      ["Mega breakfast","2 bacon, 2 sausage, 2 egg, 2 fried bread, beans and tomatoes","£8.00"],
      ["Mega breakfast with chips","","£9.50"],
      ["Belly Buster","3 eggs, 4 bacon, 4 sausage, beans, tomatoes, mushrooms, hash browns — with tea or coffee","£13.80"],
      ["Veggie breakfast","1 veggie burger, 1 egg, fried bread, beans and tomatoes","£5.80"],
      ["All extra portions","","£1.00"]
    ]},
    { cat:"Breakfast", title:"On toast &amp; rolls", items:[
      ["Beans or tomatoes on toast","","£4.40"],
      ["2 fried eggs on toast","","£4.40"],
      ["3 scrambled eggs on toast","","£4.80"],
      ["2 poached eggs on toast","","£4.80"],
      ["1 toast and butter","","£0.80"],
      ["2 toast with jam or marmalade","","£2.00"],
      ["1 toasted tea cake","","£1.60"],
      ["Bacon or sausage roll","","£4.50"],
      ["Egg roll","","£4.00"],
      ["Breakfast super roll","2 bacon, 2 sausage &amp; egg","£5.80"]
    ]},
    { cat:"Mains", title:"Main meals", items:[
      ["Cottage pie, chips, peas &amp; gravy","","£8.80"],
      ["Pork with onion gravy","","£8.80"],
      ["Steak pie, chips &amp; peas","","£8.80"],
      ["Ham, 2 eggs, chips &amp; beans or peas","","£8.80"],
      ["Pasty, chips, peas or beans","","£8.80"],
      ["Pasty on its own","","£4.80"],
      ["2 sausage, 2 egg, chips &amp; beans","","£8.80"],
      ["2 fish, chips, peas or beans","","£9.20"],
      ["Scampi &amp; chips, peas or beans","","£9.20"],
      ["Gammon, 2 eggs, chips &amp; peas","","£8.80"],
      ["Chicken curry, chips or rice","","£8.80"],
      ["Hot dog with fried onions","","£4.50"],
      ["Cheese &amp; ham ploughmans","","£7.80"],
      ["Soup &amp; a roll or bread &amp; butter","When available","£4.80"]
    ]},
    { cat:"Mains", title:"Roasts — Wed &amp; Sun", note:"Beef, pork or turkey.", items:[
      ["Large","","£10.00"],["Medium","","£9.00"],["Child's","","£8.00"]
    ]},
    { cat:"Mains", title:"Omelettes", note:"3 egg omelettes with salad &amp; coleslaw. Fillings: ham, cheese, onion, mushroom or bacon.", items:[
      ["Plain","","£5.50"],["1 filling","","£6.50"],["2 fillings","","£7.50"],["3 fillings","","£8.50"],["Add chips","","£2.50"]
    ]},
    { cat:"Light", title:"Sandwiches", items:[
      ["Ham","","£4.00"],["Cheese","","£4.00"],["Tuna","","£5.00"],["Extra portions","","£1.00"],["Toasted","","£0.20"]
    ]},
    { cat:"Light", title:"Paninis", note:"Sweet chilli chicken, ham, cheese, tuna, onion, tomato or bacon.", items:[
      ["1 filling","","£4.80"],["2 fillings","","£5.80"],["3 fillings","","£6.80"],["Add chips","","£2.50"]
    ]},
    { cat:"Light", title:"Jacket potatoes", note:"All served with salad &amp; coleslaw.", items:[
      ["Plain","","£4.80"],["Cheese","","£5.80"],["Beans","","£5.80"],["Tuna","","£6.50"],["Extra filling","","£1.20"]
    ]},
    { cat:"Burgers", title:"Burgers", note:"Served with salad and coleslaw.", items:[
      ["¼lb burger, salad &amp; coleslaw","","£5.00"],
      ["¼lb burger, salad, coleslaw &amp; chips","","£7.50"],
      ["½lb burger, salad &amp; coleslaw","","£7.00"],
      ["½lb burger, salad, coleslaw &amp; chips","","£9.50"],
      ["Chicken burger with salad","","£5.00"],
      ["Chicken burger, salad, coleslaw &amp; chips","","£7.50"],
      ["Burger Bonanza","½lb cheeseburger, 2 bacon, mushroom or egg, salad, coleslaw &amp; chips","£12.00"],
      ["Add cheese to any burger","","£1.00"]
    ]},
    { cat:"Burgers", title:"Chips &amp; extras", items:[
      ["Chips, medium","","£3.00"],["Chips, large","","£3.50"],["Cheesy chips","","£4.80"]
    ]},
    { cat:"Kids", title:"Kids menu", items:[
      ["Small breakfast, beans or toms","","£4.80"],
      ["Burger &amp; chips","","£5.50"],
      ["Nuggets &amp; chips","","£4.80"],
      ["Fish fingers, chips, peas or beans","","£4.80"],
      ["1 sausage, chips, peas or beans","","£4.80"],
      ["1 bacon, chips, peas or beans","","£4.80"],
      ["Fish, chips, peas or beans","","£5.80"]
    ]},
    { cat:"Puddings", title:"Desserts", items:[
      ["Jam roly poly &amp; custard","","£4.20"],
      ["Crumble &amp; custard","","£4.50"],
      ["Sticky toffee pudding","","£4.20"],
      ["Rice pudding with jam","","£3.00"],
      ["Scone with jam and butter","","£3.00"],
      ["Scone with jam and clotted cream","","£3.50"],
      ["Ice cream sundae","Chocolate, strawberry or caramel","£5.00"],
      ["Selection of cakes","When available","£2.20"]
    ]},
    { cat:"Drinks", title:"Hot drinks", items:[
      ["Tea","","£1.50"],["Decaffeinated tea","","£1.50"],["Coffee","","£2.00"],
      ["Decaffeinated coffee","","£2.00"],["Cappuccino","","£2.50"],["Latte","","£2.50"],
      ["Mocha","","£2.50"],["Hot chocolate","","£2.50"],
      ["Deluxe hot chocolate","With cream &amp; marshmallows","£3.00"]
    ]},
    { cat:"Drinks", title:"Cold drinks", items:[
      ["Milkshake","Strawberry, chocolate or banana","£3.00"],
      ["Deluxe milkshake","With cream, marshmallows and ice cream","£4.00"],
      ["Orange juice","","£2.00"],["Milk","","£2.00"],["Cans","","£1.50"],
      ["Fruit Shoot","","£1.00"],["Bottled water","","£1.00"]
    ]}
  ];
  var CATS = ["All","Breakfast","Mains","Light","Burgers","Kids","Puddings","Drinks"];
  var CAT_LABELS = { "All":"Everything", "Light":"Sandwiches &amp; jackets" };

  function groupHTML(g){
    var items = g.items.map(function(it){
      return '<li><span class="name">'+it[0]+(it[1] ? '<span class="desc">'+it[1]+'</span>' : '')+
             '</span><span class="lead"></span><span class="p">'+it[2]+'</span></li>';
    }).join("");
    return '<article class="mgroup"><h3>'+g.title+'</h3>'+
           (g.note ? '<p class="note">'+g.note+'</p>' : '')+'<ul>'+items+'</ul></article>';
  }
  function renderMenu(cat){
    var box = document.getElementById("groups");
    if (!box) return;
    var list = (cat === "All") ? MENU : MENU.filter(function(g){ return g.cat === cat; });
    box.innerHTML = list.map(groupHTML).join("");
  }
  /* put the tab bar — and so the top of the chosen section — just under the
     sticky header. Measured with the bar briefly un-stuck: a stuck element
     reports its pinned position, not where it actually sits in the page. */
  function scrollTabsIntoView(){
    var box = document.getElementById("tabs");
    if (!box) return;
    var stick = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--stick")) || 0;
    var prev = box.style.position;
    box.style.position = "static";
    var top = box.getBoundingClientRect().top + window.pageYOffset;
    box.style.position = prev;
    /* "instant", not "auto" — auto defers to html{scroll-behavior:smooth},
       and an animated scroll fights the content swap that just changed the
       page height underneath it */
    window.scrollTo({ top: Math.max(0, top - stick), behavior: "instant" });
  }

  function renderTabs(){
    var box = document.getElementById("tabs");
    if (!box) return;
    box.innerHTML = CATS.map(function(c,i){
      return '<button class="tab'+(i===0?' is-on':'')+'" data-cat="'+c+'" role="tab" aria-selected="'+(i===0)+'">'+
             (CAT_LABELS[c]||c)+'</button>';
    }).join("");
    box.addEventListener("click", function(e){
      var b = e.target.closest(".tab");
      if (!b) return;
      box.querySelectorAll(".tab").forEach(function(t){
        t.classList.toggle("is-on", t === b);
        t.setAttribute("aria-selected", t === b);
      });
      renderMenu(b.dataset.cat);
      watchInView();
      armReveals();
      armFire();
      scrollTabsIntoView();
    });
  }



  /* ---------- reveal on scroll (every device) ---------- */
  var revealIO = null;
  function armReveals(){
    var els = document.querySelectorAll(".page.is-active .r, .ticker .r");
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) {
      document.querySelectorAll(".r").forEach(function(el){ el.classList.add("shown"); });
      return;
    }
    if (revealIO) revealIO.disconnect();
    revealIO = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (en.isIntersecting){ en.target.classList.add("shown"); revealIO.unobserve(en.target); }
      });
    }, { threshold:0, rootMargin:"0px 0px 220px 0px" });
    els.forEach(function(el,i){
      el.classList.remove("shown");
      el.style.transitionDelay = ((i % 8) * 70) + "ms";
      revealIO.observe(el);
    });
  }


  /* ---------- count-up numbers ---------- */
  function countUp(el){
    if (el.dataset.done) return;
    el.dataset.done = "1";
    var to = parseFloat(el.dataset.to), dp = parseInt(el.dataset.dp || "0", 10), pre = el.dataset.pre || "";
    if (reduce) { el.textContent = pre + to.toFixed(dp); return; }
    var t0 = null, dur = 900;
    function step(t){
      if (!t0) t0 = t;
      var k = Math.min(1, (t - t0) / dur);
      k = 1 - Math.pow(1 - k, 3);
      el.textContent = pre + (to * k).toFixed(dp);
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ---------- one-shot triggers as things arrive ---------- */
  var fireIO = null;

  /* ---------- mobile reviews carousel: dots ---------- */
  function setupReviewCarousel(){
    var track = document.getElementById("reviewsTrack");
    var dotsBox = document.getElementById("reviewsDots");
    if (!track || !dotsBox) return;
    var cards = [].slice.call(track.children);
    dotsBox.innerHTML = cards.map(function(_, i){
      return '<button type="button" aria-label="Go to review '+(i+1)+'"'+(i===0?' class="active"':'')+'></button>';
    }).join("");
    var dots = [].slice.call(dotsBox.children);
    dots.forEach(function(dot, i){
      dot.addEventListener("click", function(){
        cards[i].scrollIntoView({ behavior:"smooth", inline:"center", block:"nearest" });
      });
    });
    var ticking = false;
    track.addEventListener("scroll", function(){
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function(){
        var mid = track.scrollLeft + track.clientWidth / 2;
        var closest = 0, best = Infinity;
        cards.forEach(function(c, i){
          var d = Math.abs((c.offsetLeft + c.offsetWidth/2) - mid);
          if (d < best) { best = d; closest = i; }
        });
        dots.forEach(function(d, i){ d.classList.toggle("active", i === closest); });
        ticking = false;
      });
    }, { passive:true });
  }

  function armFire(){
    if (fireIO) fireIO.disconnect();
    if (!("IntersectionObserver" in window)) {
      document.querySelectorAll(".plate").forEach(function(el){ el.classList.add("lit"); });
      document.querySelectorAll(".stat b[data-to]").forEach(countUp);
      document.querySelectorAll(".plan-svg").forEach(function(el){ el.classList.add("drawn"); });
      return;
    }
    fireIO = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (!en.isIntersecting) return;
        var el = en.target;
        if (el.classList.contains("plate")) el.classList.add("lit");
        else if (el.classList.contains("plan-svg")) el.classList.add("drawn");
        else countUp(el);
        fireIO.unobserve(el);
      });
    }, { threshold:.25 });
    document.querySelectorAll(".page.is-active .plate, .page.is-active .stat b[data-to], .page.is-active .plan-svg")
      .forEach(function(el){ fireIO.observe(el); });
  }

  /* ---------- hero: sign tilts with scroll, cue fades ---------- */
  var cue = document.getElementById("cue");
  function heroScroll(y){
    var sign = document.querySelector(".hanger");
    if (sign) sign.style.setProperty("--tilt", Math.max(-6, Math.min(6, (y / 60))) + "deg");
    if (cue) cue.classList.toggle("gone", y > 60);
  }

  /* ---------- scroll progress + hero parallax ---------- */
  var prog = document.getElementById("prog");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ticking = false;
  function onScroll(){
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function(){
      var max = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + "%";
      if (!reduce) {
        var bg = document.querySelector(".hero-bg");
        if (bg) {
          var y = Math.min(window.scrollY, 700);
          bg.style.transform = "translate3d(0," + (y * 0.22) + "px,0) scale(" + (1 + y * 0.00018) + ")";
        }
        heroScroll(window.scrollY);
      }
      ticking = false;
    });
  }
  window.addEventListener("scroll", onScroll, { passive:true });

  /* ---------- mobile: scroll acts like hover ---------- */
  var touchy = window.matchMedia("(hover: none), (max-width: 820px)");
  var band = null;
  function watchInView(){
    if (band) { band.disconnect(); band = null; }
    document.querySelectorAll(".in-view").forEach(function(el){ el.classList.remove("in-view"); });
    if (!touchy.matches || !("IntersectionObserver" in window)) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    band = new IntersectionObserver(function(entries){
      entries.forEach(function(en){ en.target.classList.toggle("in-view", en.isIntersecting); });
    }, { rootMargin: "-30% 0px -30% 0px", threshold: 0 });
    document.querySelectorAll(".card,.slate,.photo-frame,.mgroup,.price-card,.tile,.stat,.hours li,.facts li,.steps li,.cd-cell,.btn,.notice,.roast-panel,.mapbox,.quote,.chip,.legend span,.directions-card,.wide-photo,.photo-frame,.review-card,.rating-badge").forEach(function(el){ band.observe(el); });
  }
  if (touchy.addEventListener) touchy.addEventListener("change", watchInView);

  /* ---------------- go ---------------- */
  setStick();
  renderTabs();
  renderMenu("All");
  renderHours();
  updateStatus();
  renderCountdown();
  watchInView();
  armReveals();
  armFire();
  onScroll();
  setupReviewCarousel();
  setTimeout(moveIndicator, 60);
  setInterval(updateStatus, 30000);
  setInterval(renderCountdown, 30000);
})();
