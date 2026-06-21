#!/usr/bin/env python3
"""Generate vocabulary HTML reference files for ANN, CNN, and YOLO."""

import re, os

# ── shared CSS + JS template ──────────────────────────────────────────────────
def make_html(title, subtitle, accent, accent2, entries, out_file):
    # Build sidebar links and section anchors
    sections = []
    num = 1
    for entry in entries:
        if entry[0] == '__section__':
            sections.append(('section', entry[1]))
        else:
            slug = re.sub(r'[^a-z0-9]+', '-', entry[0].lower()).strip('-')
            sections.append(('term', num, entry[0], slug))
            num += 1

    sidebar_html = ''
    for item in sections:
        if item[0] == 'section':
            sidebar_html += f'<div class="nav-part">{item[1]}</div>\n'
        else:
            _, n, term, slug = item
            sidebar_html += f'<a href="#{slug}"><span class="nav-num">{n}</span>{term}</a>\n'

    # Build content cards
    content_html = ''
    num = 1
    for entry in entries:
        if entry[0] == '__section__':
            content_html += f'''
<div class="section-banner" id="sec-{re.sub(r"[^a-z0-9]+","-",entry[1].lower()).strip("-")}">
  <h2>{entry[1]}</h2>
</div>
'''
        else:
            vocab, desc, example = entry
            slug = re.sub(r'[^a-z0-9]+', '-', vocab.lower()).strip('-')
            content_html += f'''
<div class="vocab-card" id="{slug}">
  <div class="vc-header">
    <span class="vc-num">{num}</span>
    <span class="vc-term">{vocab}</span>
  </div>
  <div class="vc-body">
    <div class="vc-row desc-row">
      <span class="row-label">Description</span>
      <p class="row-text">{desc}</p>
    </div>
    <div class="vc-row ex-row">
      <span class="row-label ex-label">Example</span>
      <p class="row-text">{example}</p>
    </div>
  </div>
</div>
'''
            num += 1

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title} — Vocabulary Reference</title>
<style>
:root{{
  --bg:#0d1117;--bg2:#161b22;--bg3:#1c2333;--bg4:#21262d;
  --border:#30363d;--text:#e6edf3;--muted:#8b949e;
  --accent:{accent};--accent2:{accent2};
  --radius:10px;
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html{{font-size:16px;scroll-behavior:smooth;}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;line-height:1.7;}}

/* ── FONT CONTROLLER ── */
#fc{{
  position:fixed;top:16px;right:16px;z-index:2000;
  background:var(--bg3);border:1px solid var(--border);border-radius:10px;
  padding:8px 12px;display:flex;align-items:center;gap:8px;
  box-shadow:0 4px 20px rgba(0,0,0,.5);width:220px;
}}
#fc label{{white-space:nowrap;font-size:12px;color:var(--muted);}}
#fc-val{{color:var(--accent);font-weight:700;min-width:36px;font-size:12px;}}
#fc-slider{{
  flex:1;-webkit-appearance:none;appearance:none;height:4px;border-radius:2px;
  outline:none;cursor:pointer;
  background:linear-gradient(to right,var(--accent) var(--pct,31.25%),var(--bg4) var(--pct,31.25%));
}}
#fc-slider::-webkit-slider-thumb{{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:var(--accent);cursor:pointer;}}
#fc-slider::-moz-range-thumb{{width:14px;height:14px;border-radius:50%;background:var(--accent);cursor:pointer;border:none;}}

/* ── HAMBURGER BUTTON ── */
#sidebar-btn{{
  position:fixed;top:16px;left:16px;z-index:1601;
  background:rgba(28,35,51,.95);border:1px solid rgba(88,166,255,.3);
  border-radius:8px;color:var(--accent);
  width:44px;height:44px;cursor:pointer;padding:0;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;
  transition:background .2s;box-shadow:0 2px 12px rgba(0,0,0,.4);
}}
#sidebar-btn:hover{{background:rgba(88,166,255,.15);}}
#sidebar-btn .bar{{
  display:block;width:20px;height:2px;background:currentColor;border-radius:2px;
  transition:transform .25s,opacity .25s;
}}
#sidebar-btn.open .bar:nth-child(1){{transform:translateY(7px) rotate(45deg);}}
#sidebar-btn.open .bar:nth-child(2){{opacity:0;}}
#sidebar-btn.open .bar:nth-child(3){{transform:translateY(-7px) rotate(-45deg);}}

/* ── SIDEBAR ── */
#sidebar{{
  position:fixed;top:0;left:0;height:100vh;width:280px;
  background:var(--bg2);border-right:1px solid var(--border);
  overflow-y:auto;z-index:1500;
  transform:translateX(-280px);
  transition:transform .3s cubic-bezier(.4,0,.2,1);
  padding:70px 0 40px;
}}
#sidebar.open{{transform:translateX(0);}}
#sidebar::-webkit-scrollbar{{width:4px;}}
#sidebar::-webkit-scrollbar-thumb{{background:rgba(88,166,255,.25);border-radius:4px;}}
.nav-part{{
  font-size:0.65rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--accent);padding:14px 18px 4px;font-weight:700;
}}
#sidebar a{{
  display:flex;align-items:center;gap:10px;
  padding:5px 18px;font-size:0.8rem;
  color:var(--muted);text-decoration:none;
  border-left:2px solid transparent;transition:all .2s;
}}
#sidebar a:hover{{color:var(--text);background:var(--bg3);}}
#sidebar a.active{{color:var(--accent);border-left-color:var(--accent);background:rgba(88,166,255,.06);}}
.nav-num{{
  display:inline-flex;align-items:center;justify-content:center;
  min-width:22px;height:22px;border-radius:4px;
  background:var(--bg3);border:1px solid var(--border);
  font-size:0.68rem;font-weight:700;color:var(--muted);flex-shrink:0;
}}
#sidebar a.active .nav-num{{background:rgba(88,166,255,.15);color:var(--accent);border-color:var(--accent);}}

/* ── BACKDROP ── */
#backdrop{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:1400;}}

/* ── RESPONSIVE ── */
@media(min-width:1024px){{
  body.sb-open .container{{margin-left:300px;}}
  .container{{transition:margin-left .3s cubic-bezier(.4,0,.2,1);}}
}}
@media(max-width:599px){{
  #sidebar{{width:85vw;}}
}}

/* ── LAYOUT ── */
.container{{max-width:860px;margin:0 auto;padding:80px 20px 60px;}}

/* ── HERO ── */
.hero{{text-align:center;padding:20px 0 36px;}}
.hero h1{{
  font-size:2.2rem;font-weight:800;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:6px;
}}
.hero p{{color:var(--muted);font-size:0.95rem;}}
.hero .pills{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:14px;}}
.pill{{
  display:inline-block;padding:3px 12px;border-radius:20px;font-size:0.75rem;font-weight:600;
  background:rgba(88,166,255,.12);color:var(--accent);border:1px solid rgba(88,166,255,.3);
}}

/* ── SECTION BANNER ── */
.section-banner{{
  background:linear-gradient(135deg,var(--bg2),var(--bg3));
  border:1px solid var(--border);border-radius:10px;
  padding:14px 22px;margin:32px 0 16px;
  border-left:4px solid var(--accent);
}}
.section-banner h2{{
  font-size:1rem;font-weight:700;letter-spacing:.04em;
  text-transform:uppercase;color:var(--accent);margin:0;
}}

/* ── VOCAB CARD ── */
.vocab-card{{
  background:var(--bg2);border:1px solid var(--border);border-radius:10px;
  margin-bottom:14px;overflow:hidden;
  transition:border-color .2s,box-shadow .2s;
}}
.vocab-card:hover{{
  border-color:var(--accent);
  box-shadow:0 0 0 1px var(--accent), 0 4px 20px rgba(0,0,0,.3);
}}
.vc-header{{
  display:flex;align-items:center;gap:14px;
  padding:12px 18px 10px;
  border-bottom:1px solid var(--border);
  background:var(--bg3);
}}
.vc-num{{
  display:inline-flex;align-items:center;justify-content:center;
  min-width:30px;height:30px;border-radius:6px;
  background:rgba(88,166,255,.12);border:1px solid var(--accent);
  font-size:0.78rem;font-weight:800;color:var(--accent);flex-shrink:0;
}}
.vc-term{{
  font-size:1rem;font-weight:700;color:var(--accent);
}}
.vc-body{{padding:14px 18px 16px;display:flex;flex-direction:column;gap:12px;}}
.vc-row{{display:flex;gap:12px;align-items:flex-start;}}
.row-label{{
  flex-shrink:0;min-width:88px;
  font-size:0.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--muted);padding-top:2px;
}}
.ex-label{{color:var(--accent2);}}
.row-text{{font-size:0.88rem;color:var(--text);line-height:1.65;}}
.ex-row .row-text{{
  color:var(--muted);font-style:italic;
  background:var(--bg3);border:1px solid var(--border);border-radius:6px;
  padding:8px 12px;font-style:normal;
  border-left:3px solid var(--accent2);
  font-family:'Courier New',monospace;font-size:0.82rem;
}}

/* ── PRINT STYLES ── */
@media print{{
  #fc,#sidebar-btn,#sidebar,#backdrop{{display:none!important;}}
  body{{background:#fff;color:#000;}}
  .container{{margin:0;padding:20px;max-width:100%;}}
  .vocab-card{{break-inside:avoid;border:1px solid #ccc;margin-bottom:10px;}}
  .vc-header{{background:#f5f5f5;}}
  .vc-term{{color:#1a1a6e;}}
  .section-banner{{background:#eef;border-left:4px solid #339;}}
  .section-banner h2{{color:#339;}}
  .row-text{{color:#222;}}
  .ex-row .row-text{{background:#f9f9f9;border-color:#ccc;color:#444;}}
}}

@media(max-width:600px){{
  .vc-header{{flex-wrap:wrap;}}
  .vc-row{{flex-direction:column;gap:4px;}}
  .row-label{{min-width:unset;}}
  .hero h1{{font-size:1.6rem;}}
}}
</style>
</head>
<body>

<!-- Font Controller -->
<div id="fc">
  <label>A</label>
  <input id="fc-slider" type="range" min="10" max="64" step="1" value="16" style="--pct:31.25%"/>
  <span id="fc-val">16px</span>
</div>

<!-- Hamburger -->
<button id="sidebar-btn" aria-label="Toggle navigation" title="Toggle menu">
  <span class="bar"></span>
  <span class="bar"></span>
  <span class="bar"></span>
</button>

<div id="backdrop"></div>

<!-- Sidebar -->
<nav id="sidebar">
{sidebar_html}
</nav>

<!-- Content -->
<div class="container">
  <div class="hero">
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <div class="pills">
      <span class="pill">Vocabulary</span>
      <span class="pill">Description</span>
      <span class="pill">Example</span>
      <span class="pill">Print Ready</span>
    </div>
  </div>

{content_html}
</div>

<script>
// ── FONT CONTROLLER ──
(function(){{
  const slider = document.getElementById('fc-slider');
  const valLbl = document.getElementById('fc-val');
  const MIN=10, MAX=64, DEFAULT=16;
  function applySize(px){{
    document.documentElement.style.fontSize = px+'px';
    valLbl.textContent = px+'px';
    slider.style.setProperty('--pct', ((px-MIN)/(MAX-MIN)*100).toFixed(2)+'%');
  }}
  slider.value = DEFAULT; applySize(DEFAULT);
  slider.addEventListener('input', ()=>applySize(+slider.value));
}})();

// ── SIDEBAR ──
(function(){{
  const sidebar = document.getElementById('sidebar');
  const btn     = document.getElementById('sidebar-btn');
  const backdrop= document.getElementById('backdrop');

  function open(){{
    sidebar.classList.add('open');
    btn.classList.add('open');
    document.body.classList.add('sb-open');
    if(window.innerWidth < 1024) backdrop.style.display='block';
  }}
  function close(){{
    sidebar.classList.remove('open');
    btn.classList.remove('open');
    document.body.classList.remove('sb-open');
    backdrop.style.display='none';
  }}

  btn.addEventListener('click', ()=> sidebar.classList.contains('open') ? close() : open());
  backdrop.addEventListener('click', close);
  if(window.innerWidth >= 1024) open();
  window.addEventListener('resize', ()=>{{ if(window.innerWidth >= 1024) backdrop.style.display='none'; }});

  // Active link highlighting
  const links    = sidebar.querySelectorAll('a[href^="#"]');
  const cards    = Array.from(document.querySelectorAll('.vocab-card[id]'));

  const obs = new IntersectionObserver(entries => {{
    entries.forEach(e => {{
      if(e.isIntersecting){{
        links.forEach(a => a.classList.remove('active'));
        const active = sidebar.querySelector(`a[href="#${{e.target.id}}"]`);
        if(active){{ active.classList.add('active'); active.scrollIntoView({{block:'nearest'}}); }}
      }}
    }});
  }}, {{rootMargin:'-10% 0px -80% 0px', threshold:0}});

  cards.forEach(c => obs.observe(c));

  links.forEach(a => a.addEventListener('click', ()=>{{
    if(window.innerWidth < 1024) close();
  }}));
}})();
</script>
</body>
</html>'''

    path = f'/home/user/git_test/{out_file}'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Saved {out_file}')


# ── VOCABULARY DATA ───────────────────────────────────────────────────────────

ann_entries = [
    ('__section__', 'Part 1 — Core Concepts'),
    ('Artificial Neural Network (ANN)',
     'A computational model inspired by the human brain, made up of layers of interconnected neurons. It learns to map inputs to outputs by adjusting internal parameters called weights through a training process.',
     'A 2-layer ANN with inputs [study_hours=8, sleep_hours=7] predicts whether a student Passes or Fails an exam.'),
    ('Neuron / Node',
     'The basic processing unit of an ANN. Each neuron receives one or more numeric inputs, multiplies each by a weight, sums them all, adds a bias, then passes the result through an activation function.',
     'Neuron receives x₁=0.8 and x₂=0.5; computes z = (0.8×0.4)+(0.5×−0.3)+0.1 = 0.29; outputs sigmoid(0.29) = 0.572.'),
    ('Weight',
     'A numeric parameter that controls how strongly an input influences a neuron\'s output. Positive weights amplify the input; negative weights suppress it. Weights are learned during training via backpropagation.',
     'Weight w₁=0.4 on input x₁=0.8 contributes 0.4×0.8=0.32 to the neuron\'s weighted sum.'),
    ('Bias',
     'A constant value added to the weighted sum inside a neuron, separate from any input. It shifts the activation threshold, allowing the neuron to fire even when all inputs are zero.',
     'With inputs zero but bias=0.1, the neuron still has z=0.1 and a non-zero output, rather than being completely silent.'),
    ('Input Layer',
     'The first layer of the network. It holds the raw input data, one neuron per feature. No computation happens here — it simply passes values to the next layer.',
     'For the Pass/Fail problem: Input Layer has 2 neurons — one for study_hours (0.8) and one for sleep_hours (0.7).'),
    ('Hidden Layer',
     'One or more intermediate layers between Input and Output. Each neuron learns to detect a pattern or combination of the previous layer\'s signals. More hidden layers allow detection of more complex patterns.',
     'A hidden layer of 3 neurons learns combinations like "high study AND low sleep" or "average of both", helping the network separate Pass from Fail cases.'),
    ('Output Layer',
     'The final layer that produces the network\'s prediction. For binary classification it has 1 neuron (0–1 probability). For 10-class classification it has 10 neurons, each giving a probability for one class.',
     'For Pass/Fail: Output neuron outputs 0.58, meaning 58% probability of Pass. Since 0.58 > 0.5, the prediction is PASS.'),

    ('__section__', 'Part 2 — Activation Functions'),
    ('Activation Function',
     'A mathematical function applied to a neuron\'s weighted sum to introduce non-linearity. Without it, stacking layers would still just be one linear equation. It decides whether and how strongly a neuron "fires".',
     'Without activation: 3 linear layers = 1 linear layer. With ReLU, the network can learn curves and complex decision boundaries.'),
    ('Sigmoid',
     'An S-shaped activation function that squashes any real number into the range 0 to 1. Formula: σ(z) = 1/(1+e⁻ᶻ). Ideal for binary classification output layers because the result can be read as a probability.',
     'σ(0.97)=0.725;  σ(0)=0.5;  σ(−3)=0.047. Used as the final neuron for Pass/Fail — output 0.58 means 58% chance of Pass.'),
    ('ReLU (Rectified Linear Unit)',
     'The most widely used activation function in hidden layers. Formula: max(0, z). If the input is positive it passes through unchanged; if negative it outputs zero. Fast and avoids the vanishing gradient problem.',
     'ReLU(3.5)=3.5;  ReLU(−1.2)=0. In an 8×8 image ANN, many hidden neurons output zero (ReLU kills negative weighted sums), keeping the network sparse and efficient.'),
    ('Tanh (Hyperbolic Tangent)',
     'An activation function that maps any value to the range −1 to +1, and is zero-centred. Often used in hidden layers when data has both positive and negative patterns, as it can distinguish them naturally.',
     'tanh(0)=0,  tanh(1)=0.76,  tanh(−1)=−0.76. More useful than Sigmoid for hidden layers in text or NLP tasks where negative features matter.'),
    ('Softmax',
     'An activation function used in the output layer for multi-class problems. It converts a vector of raw scores (logits) into probabilities that all sum to exactly 1, so each value represents the probability of one class.',
     'Raw scores [2.0, 1.0, 0.1] → Softmax → [0.70, 0.24, 0.06]. The first class has 70% probability and would be chosen as the prediction.'),

    ('__section__', 'Part 3 — Training'),
    ('Forward Pass',
     'The process of sending input data through the network from the input layer to the output layer, computing each neuron\'s output at every layer in sequence. This produces a prediction without changing any weights.',
     'Input [0.8, 0.7] → Hidden layer (3 neurons) → Output neuron → ŷ=0.58. Numbers flow forward through every weight and activation until a result appears.'),
    ('Loss Function',
     'A formula that measures how wrong the network\'s prediction is compared to the true label. The goal of training is to minimise this value. Different tasks use different loss functions.',
     'Prediction ŷ=0.58, true label y=1 (Pass). Binary Cross-Entropy: L = −log(0.58) = 0.544. If ŷ were 0.99: L = −log(0.99) = 0.01 — much lower, indicating a near-perfect prediction.'),
    ('Binary Cross-Entropy',
     'The standard loss function for binary (two-class) classification. Penalises confident wrong answers heavily and rewards confident correct answers. Formula: L = −[y·log(ŷ) + (1−y)·log(1−ŷ)].',
     'y=1, ŷ=0.58 → L=0.544.  y=1, ŷ=0.99 → L=0.01.  y=0, ŷ=0.02 → L≈0.02. Lower is better.'),
    ('Backpropagation',
     'The algorithm that computes how much each weight contributed to the prediction error. It uses the chain rule of calculus to work backwards from the output layer to the input layer, calculating gradients for every weight.',
     'After computing loss=0.544, backprop finds weight w=0.7 has gradient=0.12, meaning "increasing w increases loss". So we subtract η×0.12 from w to move toward lower loss.'),
    ('Gradient Descent',
     'The optimisation method that updates each weight by a small step in the direction that reduces the loss. Formula: w_new = w_old − η × (∂Loss/∂w). Repeated over many iterations, the loss converges toward a minimum.',
     'w=0.7, gradient=0.12, η=0.1 → w_new = 0.7 − 0.1×0.12 = 0.688. The weight moved a small step closer to a value that produces lower loss.'),
    ('Learning Rate (η)',
     'A hyperparameter that controls how large each weight update step is during gradient descent. Too large: training overshoots and becomes unstable. Too small: training is slow. Typical values: 0.001 to 0.01.',
     'η=1.0 (too large): weights oscillate, loss goes up. η=0.0001 (too small): needs 10× more epochs. η=0.01 (good): loss steadily decreases each epoch.'),
    ('Epoch',
     'One complete pass through the entire training dataset — every sample is seen once by the network. Training runs for many epochs until the loss stops improving. Typical range: 10 to 1000 epochs.',
     'With 5 training samples: Epoch 1 → loss=0.95. After 100 epochs → loss=0.15. After 200 epochs → loss=0.05, showing the network is converging.'),
    ('Batch Size',
     'The number of training samples processed together before the weights are updated. Full batch uses all data at once (stable but slow). Mini-batch (32–256) balances speed and stability. Stochastic uses 1 sample.',
     'With 1000 training images and batch_size=32: each epoch processes 1000÷32≈31 batches. Weights update 31 times per epoch instead of just once.'),
    ('Normalisation',
     'Scaling raw input values to a small consistent range (usually 0–1 or −1 to +1) before feeding them to the network. Prevents large values from dominating small ones and speeds up training significantly.',
     'Pixel value 200 ÷ 255 = 0.784. Study hours 8 ÷ 10 = 0.8. Without normalisation, a 200-pixel value would have 200× more influence on the weighted sum than a 1-hour study value.'),

    ('__section__', 'Part 4 — Image Processing'),
    ('Grayscale Image',
     'An image where each pixel is represented by a single number from 0 (pure black) to 255 (pure white), encoding only brightness with no colour information. It requires only 1 channel of data.',
     'An 8×8 grayscale image has 64 pixel values: [20, 30, 40, 25, 140, 160, 200, 220, ...]. After normalisation: [0.08, 0.12, 0.16, 0.10, 0.55, 0.63, 0.78, 0.86, ...].'),
    ('RGB Image',
     'A colour image where each pixel has three separate values — Red, Green, and Blue — each ranging from 0 to 255. The three channels combine to produce every visible colour. An RGB image holds 3× more data than grayscale.',
     'An orange pixel: R=210, G=80, B=60. White: R=255, G=255, B=255. An 8×8 RGB image has 8×8×3=192 values vs 64 for grayscale.'),
    ('Flatten',
     'The operation of converting a 2D image grid into a 1D vector so it can be fed into an ANN\'s input layer. Done by reading pixels row by row from top-left to bottom-right. Spatial structure is lost.',
     '4×4 image → Row1 [10,30,200,220], Row2 [5,50,210,240], Row3 [15,80,190,230], Row4 [20,60,200,250] → flat 16-value vector fed to 16 input neurons.'),
    ('Weighted Sum (Σ)',
     'The core computation inside each neuron: multiply every input by its corresponding weight, then add all the results together, then add the bias. Written as z = Σ(xᵢ × wᵢ) + b.',
     'Inputs [0.8, 0.7], weights [0.5, −0.3], bias 0.1: z = (0.8×0.5)+(0.7×−0.3)+0.1 = 0.40−0.21+0.10 = 0.29. This z then goes into the activation function.'),
]

cnn_entries = [
    ('__section__', 'Part 1 — Dataset & Input'),
    ('Dataset',
     'A collection of labelled examples used to train and evaluate a neural network. Divided into training set (to learn from), validation set (to tune hyperparameters), and test set (to measure final accuracy).',
     'CIFAR-10: 60,000 colour images in 10 classes (cat, dog, car, plane…). 50,000 for training, 10,000 for testing. Each image is 32×32×3 = 3,072 input values.'),
    ('Pixel Value',
     'A single numeric value representing the brightness or colour intensity of one point in a digital image. In grayscale, one value per pixel (0–255). In RGB, three values per pixel — one each for Red, Green, and Blue.',
     'Top-left pixel of a red strawberry: R=220, G=40, B=30. Normalised: R=0.863, G=0.157, B=0.118. These three values become three separate inputs to the CNN.'),
    ('Preprocessing',
     'Steps applied to raw data before feeding it to the network: normalising pixel values to 0–1, resizing images to a fixed size, converting to the right format, and optionally augmenting (flipping, rotating) for variety.',
     'Raw JPEG (variable size, uint8 0–255) → resize to 224×224 → divide by 255 → float32 tensor [224,224,3] → ready to enter the CNN.'),

    ('__section__', 'Part 2 — Convolutional Layers'),
    ('Convolutional Layer',
     'The core layer of a CNN. A small filter (e.g. 3×3) slides across the input at every position, computing a dot product at each step. This produces a Feature Map highlighting where the filter\'s pattern appears.',
     'A 3×3 edge filter slides over a 6×6 image. At each of 16 positions (stride 1, no padding) it computes one value, producing a 4×4 feature map showing where edges were found.'),
    ('Filter / Kernel',
     'A small grid of learnable weights (e.g. 3×3 or 5×5) that slides across the input looking for one specific pattern. Multiple filters in the same layer each detect a different feature — edges, corners, textures.',
     'Horizontal-edge filter: [[−1,−1,−1],[0,0,0],[1,1,1]]. Placed over a dark-to-bright boundary, the dot product gives a large positive value, detecting the horizontal edge.'),
    ('Feature Map (Activation Map)',
     'The 2D output produced by applying one filter to the entire input. Each value represents how strongly that filter\'s pattern was present at that spatial location. Multiple filters produce multiple feature maps.',
     'Applying 32 different 3×3 filters to a 32×32×3 input produces 32 feature maps of size 30×30, a combined output of shape [30×30×32] — 32 detected patterns across the image.'),
    ('Stride',
     'The number of pixels the filter moves per step as it slides across the input. Stride 1 moves one pixel at a time (large output). Stride 2 skips every other position, halving the output size and reducing computation.',
     '3×3 filter on 6×6 input: stride=1 → 4×4 output (16 positions). stride=2 → 2×2 output (4 positions). Larger stride = faster computation but coarser feature map.'),
    ('Padding',
     'Adding rows/columns of zeros around the input border before convolution. "Valid" padding: no zeros, output shrinks. "Same" padding: zeros added so output stays the same spatial size as the input.',
     '3×3 filter on 6×6 input, no padding → 4×4 output. With same padding (1 zero border each side) → 6×6 output. Padding preserves spatial dimensions through convolution.'),
    ('Weight Sharing',
     'In a CNN the same filter weights are reused at every spatial position across the image. This means a pattern detector learned in one location automatically detects that pattern everywhere in the image.',
     'A 3×3 filter with 9 weights detects horizontal edges anywhere in a 224×224 image. Without weight sharing, you would need unique weights for each of 224×224=50,176 positions.'),

    ('__section__', 'Part 3 — Activation & Pooling'),
    ('ReLU (Rectified Linear Unit)',
     'The activation function applied after each convolution. Replaces any negative value with zero and keeps positive values unchanged: f(z)=max(0,z). Introduces non-linearity and prevents vanishing gradients.',
     'Feature map values [−0.5, 1.2, −0.3, 0.8] after ReLU → [0, 1.2, 0, 0.8]. Negative "non-activations" are silenced; only positive detections pass forward.'),
    ('Max Pooling',
     'A down-sampling operation that divides the feature map into small regions and keeps only the maximum value from each. Reduces spatial size, makes the network robust to small shifts/translations, and reduces computation.',
     '2×2 max pool (stride 2) on [[1,3,2,4],[5,6,7,8],[9,2,3,1],[4,6,2,8]]: top-left max=6, top-right=8, bottom-left=9, bottom-right=8 → output [[6,8],[9,8]]. Size halved from 4×4 to 2×2.'),
    ('Receptive Field',
     'The region of the original input image that influences a particular neuron\'s output. Early layers have small receptive fields (see fine details). Deeper layers have large receptive fields (see large patterns or whole objects).',
     'Layer 1 neurons see a 3×3 input region (detect edges). Layer 3 neurons see a 9×9 region (detect textures). Layer 6 neurons may see 32×32 region (detect object parts like ears or wheels).'),

    ('__section__', 'Part 4 — Dense Layers & Output'),
    ('Flatten Layer',
     'Converts the 3D output of the last convolutional/pooling layer (height × width × channels) into a 1D vector. Required before feeding into fully-connected Dense layers.',
     'Last pooling output shape: 4×4×64 = 1,024 values. Flatten converts this to a vector [v₁, v₂, ..., v₁₀₂₄] that a Dense layer can accept.'),
    ('Dense Layer (Fully Connected)',
     'A layer where every neuron connects to every neuron in the previous layer. It combines all detected features to make the final classification decision. Typically placed after the convolutional layers.',
     'Flattened vector of 1,024 values feeds into a Dense layer of 256 neurons. Each of 256 neurons has 1,024 weights → 256×1,024=262,144 parameters just for this one layer.'),
    ('Dropout',
     'A regularisation technique that randomly sets a fraction of neurons to zero during training (e.g. 50% chance each). Forces the network not to rely on any single neuron, reducing overfitting and improving generalisation.',
     'Before dropout: [0.8, 0.5, 0.3, 0.9, 0.2]. With Dropout(0.5): [0, 0.5, 0, 0.9, 0] — two neurons randomly silenced. At test time, dropout is turned off and all neurons are active.'),
    ('Overfitting',
     'When a model learns the training data too specifically — including noise — and performs poorly on new unseen data. Signs: training accuracy 99%, test accuracy 65%. Prevented by dropout, regularisation, and more data.',
     'CNN trained on 100 cat images with no dropout: 99% training accuracy but only 60% on new photos. Adding Dropout(0.5) improves test accuracy to 85%.'),
    ('Softmax Output',
     'The final layer activation for multi-class CNNs. Converts raw scores into class probabilities that sum to 1. The class with the highest probability is the prediction.',
     'CIFAR-10 raw scores [1.2, 0.3, 3.7, ...] → Softmax → [0.04, 0.02, 0.55, ...]. Class 3 (bird) has 55% probability and is chosen as the prediction.'),

    ('__section__', 'Part 5 — Training'),
    ('Loss Function',
     'Measures how wrong the CNN\'s predictions are. Minimised during training. Categorical Cross-Entropy is standard for multi-class problems; Binary Cross-Entropy for two-class problems.',
     'True class: cat (index 3). CNN output: [0.02,0.01,0.01,0.85,0.02,...]. Loss = −log(0.85) = 0.163. If it predicted 0.20 for cat: loss = −log(0.20) = 1.61 — much higher.'),
    ('Backpropagation',
     'The algorithm that computes gradients for every weight in the CNN by applying the chain rule from output back to input. Each filter\'s weights are nudged to reduce the loss after every mini-batch.',
     'Loss=0.54. Backprop flows: output layer → Dense → Flatten → Pool → Conv3 → Conv2 → Conv1. Each filter\'s 9 weights get their own gradient and update step.'),
    ('Batch Normalisation',
     'Applied after a layer to normalise outputs to mean≈0 and variance≈1 within each mini-batch. Stabilises training, allows higher learning rates, and acts as mild regularisation.',
     'Conv layer outputs: [−5.2, 0.3, 12.1, −0.8]. After Batch Norm: [−0.7, 0.1, 1.4, −0.2]. Prevents later layers from seeing wildly varying input scales across batches.'),
    ('Training Loop',
     'The repeated cycle: (1) Forward pass → predict. (2) Compute loss. (3) Backward pass → compute gradients. (4) Update weights. Repeats for every mini-batch, for many epochs, until the model converges.',
     'Epoch 1: loss=2.1, accuracy=12%. Epoch 10: loss=1.4, accuracy=48%. Epoch 50: loss=0.6, accuracy=80%. Epoch 100: loss=0.3, accuracy=92%. Loop runs until improvement plateaus.'),
]

yolo_entries = [
    ('__section__', 'Part 1 — YOLO Fundamentals'),
    ('YOLO (You Only Look Once)',
     'A family of real-time object detection models. Unlike earlier methods that process an image multiple times, YOLO passes the image through the CNN exactly once and simultaneously predicts all bounding boxes and classes.',
     'R-CNN feeds 2,000 region crops into the CNN separately → slow. YOLO feeds 1 image → single CNN pass → all detections at once. YOLOv8n achieves ~80 FPS on a GPU for real-time video.'),
    ('Single-Pass Detection',
     'YOLO\'s defining characteristic: the entire image goes through the network exactly once. The CNN processes all spatial locations simultaneously, making detection much faster than region-proposal methods.',
     'R-CNN runs CNN 2,000 times per image (once per candidate region). YOLO runs CNN once: 640×640 image → [backbone→neck→head] → 8,400 box predictions, all in one forward pass.'),
    ('R-CNN (Region-based CNN)',
     'An earlier object detection approach that first generates ~2,000 candidate regions using selective search, then runs a CNN separately on each region. Accurate but extremely slow (47 seconds per image).',
     'R-CNN on 640×640 image: Selective Search → 2,000 regions → run VGG-16 on each → 2,000 × CNN forward passes → classify each region. YOLO replaces this with 1 forward pass.'),
    ('Darknet Framework',
     'An open-source neural network framework written in C and CUDA by Joseph Redmon. Used to train and run YOLOv1–v4. Designed for speed on GPUs and CPUs. Later versions (v5–v11) moved to PyTorch.',
     'Train YOLOv3 with Darknet: ./darknet detector train cfg/coco.data cfg/yolov3.cfg darknet53.conv.74. The C/CUDA code runs faster than Python on embedded devices like Jetson Nano.'),
    ('Anchor Boxes',
     'Predefined bounding box shapes of various aspect ratios and scales, used in YOLOv2–v7. The network predicts small adjustments to these anchors rather than predicting coordinates from scratch, making learning easier.',
     'Anchors: [(10×13), (16×30), (33×23)]. A car best matches anchor (33×23). Network predicts offsets Δx=0.2, Δy=−0.1, Δw=1.4, Δh=0.9 to refine anchor into the exact box.'),
    ('Grid System',
     'YOLO divides the input image into an S×S grid (e.g. 80×80, 40×40, 20×20). Each grid cell is responsible for detecting objects whose centre falls within that cell, giving YOLO its spatial structure.',
     'Image divided into 80×80 grid = 6,400 cells. A dog\'s centre is at pixel (320,240) on a 640×640 image → grid cell (40,30). That cell is responsible for detecting the dog.'),
    ('mAP (mean Average Precision)',
     'The standard metric for evaluating object detection. Precision measures how many detections were correct; Recall measures how many true objects were found. AP averages over confidence thresholds; mAP averages AP over all classes.',
     'COCO dataset: YOLOv8n mAP₅₀₋₉₅=37.3%. Across 80 classes, averaging precision at IoU thresholds 0.50–0.95, the model is correct 37.3% of the time. YOLOv8x achieves 53.9%.'),
    ('FPS (Frames Per Second)',
     'A measure of detection speed — how many images the model can process per second. Higher FPS enables real-time video. Larger models are more accurate but slower; nano models prioritise speed.',
     'YOLOv8n: ~80 FPS on GPU (real-time for 30 FPS video). YOLOv8x: ~20 FPS on same GPU. On CPU: YOLOv8n ~5 FPS, YOLOv8x ~1 FPS.'),

    ('__section__', 'Part 2 — YOLOv8 Architecture'),
    ('Backbone',
     'The first part of a YOLO network that processes the raw image and extracts multi-scale feature representations. Typically a deep CNN pre-trained on large datasets. YOLOv8 uses CSPDarknet with C2f modules.',
     'YOLOv8n backbone: input [640×640×3] → 5 stages → feature maps at [80×80×128], [40×40×256], [20×20×512]. Each scale captures different levels of detail.'),
    ('Neck (PAN-FPN)',
     'The middle section of YOLO that combines feature maps from different backbone scales. Fuses low-resolution (large context) and high-resolution (fine detail) features to improve detection at all object sizes.',
     'PAN-FPN: takes backbone outputs [80×80], [40×40], [20×20] → upsample and merge → enriched feature maps. Now the 80×80 map has both fine detail AND context from the 20×20 deep map.'),
    ('Head',
     'The final part of the network that makes actual predictions from the neck\'s feature maps. In YOLOv8 the head is decoupled — separate branches for classification (what) and regression (where), at three scales.',
     'For each of 8,400 candidate positions (6400+1600+400), the head outputs: [x,y,w,h] box, confidence score, and 80 class probabilities. Final output: all detected objects in the image.'),
    ('CSPDarknet',
     'Cross Stage Partial Network — the backbone architecture used from YOLOv4 onward. It splits the feature map into two paths: one goes through dense convolution blocks, one skips ahead. Both are merged at the end.',
     'Without CSP: layer output copied to every subsequent layer → high memory. With CSP: 50% of channels go through Conv layers, 50% skip → then merge. YOLOv8n achieves similar accuracy to YOLOv5s with 30% fewer parameters.'),
    ('C2f Module',
     'YOLOv8\'s core feature extraction block (Cross-Stage Partial with 2 Faster bottlenecks). Enables richer gradient flow during training while keeping the model compact. Replaces the C3 block from YOLOv5.',
     'C2f input: 256-channel feature map → split → Branch 1: through 2 bottlenecks. Branch 2: direct connection. Both merged → 256-channel output with richer learned features.'),
    ('SPPF (Spatial Pyramid Pooling Fast)',
     'A module at the end of the backbone that applies max pooling three times with the same small kernel, then concatenates all results. Captures context at multiple effective scales without heavy computation.',
     'Input [20×20×512] → MaxPool(5×5) → MaxPool(5×5) → MaxPool(5×5) → concatenate all four → [20×20×2048] → 1×1 conv → [20×20×512]. Efficient multi-scale context at low cost.'),
    ('SiLU Activation',
     'Sigmoid Linear Unit — the activation function used in YOLOv8, defined as SiLU(x) = x × sigmoid(x). Smooth, non-monotonic, and outperforms ReLU on deep networks like YOLO backbones.',
     'SiLU(1.0)=0.731;  SiLU(−1.0)=−0.269;  SiLU(0)=0. Unlike ReLU which hard-clips at 0, SiLU allows small negative values, preserving gradient flow for negative activations.'),
    ('Decoupled Head',
     'A prediction head where the classification task (what class?) and regression task (where is it?) have separate processing branches. YOLOv8 uses decoupled heads, improving accuracy over the coupled heads used in older versions.',
     'Coupled (YOLOv5): one Conv branch → outputs class + box together. Decoupled (YOLOv8): Branch A → box [x,y,w,h]. Branch B → class probabilities [80 values]. Each branch specialises independently.'),

    ('__section__', 'Part 3 — Detection & Evaluation'),
    ('Bounding Box',
     'A rectangle described by four values [x, y, w, h] that locates a detected object in the image. x,y are the centre coordinates; w,h are width and height — all normalised relative to image size (0 to 1).',
     'Dog detected at: x=0.5 (image centre), y=0.6, w=0.3 (30% of width), h=0.4 (40% of height). On 640×640: centre at (320,384), box size 192×256 pixels.'),
    ('Confidence Score',
     'A value from 0 to 1 representing how certain the model is that a box contains an object of the predicted class. Boxes below a threshold (e.g. 0.25) are discarded as low-confidence detections.',
     '[car, confidence=0.92] → kept. [car, confidence=0.18] → discarded (below 0.25 threshold). Score comes from: objectness × class_probability = 0.97 × 0.95 = 0.92.'),
    ('IoU (Intersection over Union)',
     'A metric measuring how much two bounding boxes overlap. Computed as (area of overlap) ÷ (area of union). Used to judge whether a detection matches a ground-truth box. IoU > 0.5 is typically a correct detection.',
     'Predicted box: 60px². Ground-truth: 80px². Overlap: 50px². Union: 60+80−50=90px². IoU = 50/90 = 0.556 > 0.5 → counted as a correct detection (true positive).'),
    ('NMS (Non-Maximum Suppression)',
     'A post-processing step that removes duplicate detections. When multiple boxes detect the same object, NMS keeps the one with the highest confidence and removes all others that overlap it beyond an IoU threshold.',
     'Three boxes for one car: [conf=0.95], [conf=0.88], [conf=0.72], all IoU > 0.5 with each other. NMS: keep 0.95 (highest), discard 0.88 and 0.72. Final output: 1 detection for the car.'),
    ('Anchor-Free Detection',
     'An approach (used in YOLOv8+) where the model directly predicts bounding box coordinates without relying on predefined anchor shapes. Simplifies training, eliminates anchor tuning, improves accuracy on varied shapes.',
     'Anchor-based YOLOv5: predicts offsets [Δx,Δy,Δw,Δh] relative to fixed anchor (30×60). Anchor-free YOLOv8: directly predicts [cx=0.51, cy=0.62, w=0.28, h=0.41] — no preset anchor shapes needed.'),
    ('DFL Loss (Distribution Focal Loss)',
     'A loss function used in YOLOv8 for bounding box regression. Instead of predicting one coordinate value directly, it predicts a probability distribution over possible values, making boundary prediction more precise.',
     'Classic: predict box right-edge=150px directly. DFL: predict distribution [p(140)=0.1, p(145)=0.2, p(150)=0.5, p(155)=0.2] → weighted average=150px. More stable for ambiguous object boundaries.'),
    ('TAL (Task-Aligned Learning)',
     'YOLOv8\'s training assignment strategy that determines which predicted boxes are matched to which ground-truth objects. Uses a combined score of classification confidence and box IoU to create better training targets.',
     'Old strategy: assign by IoU alone. TAL: score = (class_prob)^α × (IoU)^β. Box with 0.8 class confidence and 0.75 IoU: score = 0.8×0.75=0.60. Better boxes are rewarded; ambiguous cases resolved more accurately.'),
]

# ── Generate all three ────────────────────────────────────────────────────────

make_html(
    title='Artificial Neural Networks',
    subtitle='Vocabulary Reference — Fundamentals · Grayscale · RGB Images',
    accent='#3fb950', accent2='#58a6ff',
    entries=ann_entries,
    out_file='ann_vocabulary_description.html'
)

make_html(
    title='Convolutional Neural Networks',
    subtitle='Vocabulary Reference — Architecture · Layers · Training',
    accent='#58a6ff', accent2='#bc8cff',
    entries=cnn_entries,
    out_file='cnn_vocabulary_description.html'
)

make_html(
    title='YOLO Object Detection',
    subtitle='Vocabulary Reference — Versions · Architecture · YOLOv8',
    accent='#f0883e', accent2='#e3b341',
    entries=yolo_entries,
    out_file='yolo_vocabulary_description.html'
)

print('All done.')
