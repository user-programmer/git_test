from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        val = kwargs.get(side, {'sz': 4, 'val': 'single', 'color': 'CCCCCC'})
        node = OxmlElement(f'w:{side}')
        node.set(qn('w:sz'), str(val.get('sz', 4)))
        node.set(qn('w:val'), val.get('val', 'single'))
        node.set(qn('w:color'), val.get('color', 'CCCCCC'))
        tcBorders.append(node)
    tcPr.append(tcBorders)

def add_title_page(doc, title, subtitle, accent_hex):
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(28)
    r, g, b = bytes.fromhex(accent_hex)
    run.font.color.rgb = RGBColor(r, g, b)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run(subtitle)
    run2.font.size = Pt(13)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    doc.add_paragraph()
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run3 = p3.add_run('Vocabulary Reference Card  •  Print Edition')
    run3.font.size = Pt(10)
    run3.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run3.italic = True

    doc.add_page_break()

def add_entry(doc, num, vocab, description, example, accent_hex):
    r, g, b = bytes.fromhex(accent_hex)
    accent = RGBColor(r, g, b)

    # Number + vocabulary term
    p_head = doc.add_paragraph()
    p_head.paragraph_format.space_before = Pt(10)
    p_head.paragraph_format.space_after = Pt(2)
    run_num = p_head.add_run(f'{num}.  ')
    run_num.font.size = Pt(11)
    run_num.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run_term = p_head.add_run(vocab)
    run_term.bold = True
    run_term.font.size = Pt(13)
    run_term.font.color.rgb = accent

    # Description
    p_desc_label = doc.add_paragraph()
    p_desc_label.paragraph_format.space_before = Pt(1)
    p_desc_label.paragraph_format.space_after = Pt(0)
    p_desc_label.paragraph_format.left_indent = Inches(0.3)
    rl = p_desc_label.add_run('Description: ')
    rl.bold = True
    rl.font.size = Pt(9)
    rl.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    rd = p_desc_label.add_run(description)
    rd.font.size = Pt(9)

    # Example
    p_ex = doc.add_paragraph()
    p_ex.paragraph_format.space_before = Pt(1)
    p_ex.paragraph_format.space_after = Pt(4)
    p_ex.paragraph_format.left_indent = Inches(0.3)
    re_label = p_ex.add_run('Example: ')
    re_label.bold = True
    re_label.font.size = Pt(9)
    re_label.font.color.rgb = accent
    re_body = p_ex.add_run(example)
    re_body.font.size = Pt(9)
    re_body.italic = True

    # Divider
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(0)
    run_div = p_div.add_run('─' * 90)
    run_div.font.size = Pt(6)
    run_div.font.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)

def add_section_header(doc, text, accent_hex):
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    r2, g2, b2 = bytes.fromhex(accent_hex)
    run = p.add_run(f'  {text.upper()}  ')
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(r2, g2, b2)

# ─────────────────────────────────────────────────────────────
# ANN DOCUMENT
# ─────────────────────────────────────────────────────────────

ann_entries = [
    # SECTION: Core Concepts
    ('__section__', 'Part 1 — Core Concepts'),
    ('Artificial Neural Network (ANN)',
     'A computational model inspired by the human brain, made up of layers of interconnected neurons. It learns to map inputs to outputs by adjusting internal parameters called weights through a training process.',
     'A 2-layer ANN with inputs [study_hours=8, sleep_hours=7] predicts whether a student Passes or Fails an exam.'),
    ('Neuron / Node',
     'The basic processing unit of an ANN. Each neuron receives one or more numeric inputs, multiplies each by a weight, sums them all, adds a bias, then passes the result through an activation function.',
     'Neuron receives x₁=0.8 and x₂=0.5; computes z = (0.8×0.4)+(0.5×-0.3)+0.1 = 0.29; outputs sigmoid(0.29) = 0.572.'),
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
     'A hidden layer of 3 neurons learns combinations like "high study AND low sleep" or "average of both", enabling the network to separate Pass from Fail cases.'),
    ('Output Layer',
     'The final layer that produces the network\'s prediction. For binary classification it has 1 neuron (0–1 probability). For 10-class classification it has 10 neurons, each giving a probability for one class.',
     'For Pass/Fail: Output neuron outputs 0.58, meaning 58% probability of Pass. Since 0.58 > 0.5, the prediction is PASS.'),

    # SECTION: Activation Functions
    ('__section__', 'Part 2 — Activation Functions'),
    ('Activation Function',
     'A mathematical function applied to a neuron\'s weighted sum to introduce non-linearity. Without it, stacking layers would still just be one linear equation. It decides whether and how strongly a neuron "fires".',
     'Without activation: 3 linear layers = 1 linear layer. With ReLU, the network can learn curves and complex decision boundaries.'),
    ('Sigmoid',
     'An S-shaped activation function that squashes any real number into the range 0 to 1. Formula: σ(z) = 1/(1+e⁻ᶻ). Ideal for binary classification output layers because the result can be read as a probability.',
     'σ(0.97) = 0.725; σ(0) = 0.5; σ(−3) = 0.047. Used as the final neuron for Pass/Fail — output 0.58 means 58% chance of Pass.'),
    ('ReLU (Rectified Linear Unit)',
     'The most widely used activation function in hidden layers. Formula: max(0, z). If the input is positive, it passes through unchanged; if negative, it outputs zero. Fast and avoids the vanishing gradient problem.',
     'ReLU(3.5) = 3.5; ReLU(−1.2) = 0. In an 8×8 image ANN, many hidden neurons output zero (ReLU kills negative weighted sums), keeping the network sparse and efficient.'),
    ('Tanh (Hyperbolic Tangent)',
     'An activation function that maps any value to the range −1 to +1, and is zero-centred. Often used in hidden layers when data has both positive and negative patterns, as it can distinguish them naturally.',
     'tanh(0)=0, tanh(1)=0.76, tanh(−1)=−0.76. More useful than Sigmoid for hidden layers in text or NLP tasks where negative features matter.'),
    ('Softmax',
     'An activation function used in the output layer for multi-class problems. It converts a vector of raw scores (logits) into probabilities that all sum to exactly 1, so each value represents the probability of one class.',
     'Raw scores [2.0, 1.0, 0.1] → Softmax → [0.70, 0.24, 0.06]. The first class has 70% probability and would be chosen as the prediction.'),

    # SECTION: Training
    ('__section__', 'Part 3 — Training'),
    ('Forward Pass',
     'The process of sending input data through the network from the input layer to the output layer, computing each neuron\'s output at every layer in sequence. This produces a prediction without changing any weights.',
     'Input [0.8, 0.7] → Hidden layer (3 neurons) → Output neuron → ŷ=0.58. The number flows forward through every weight and activation until a result appears.'),
    ('Loss Function',
     'A formula that measures how wrong the network\'s prediction is compared to the true label. The goal of training is to minimise this value. Different tasks use different loss functions.',
     'Prediction ŷ=0.58, true label y=1 (Pass). Binary Cross-Entropy: L = −log(0.58) = 0.544. If ŷ were 0.99, L = −log(0.99) = 0.01 — much lower, indicating near-perfect prediction.'),
    ('Binary Cross-Entropy',
     'The standard loss function for binary (two-class) classification. Penalises confident wrong answers heavily and rewards confident correct answers. Formula: L = −[y·log(ŷ) + (1−y)·log(1−ŷ)].',
     'y=1, ŷ=0.58 → L = −log(0.58) = 0.544. y=1, ŷ=0.99 → L = 0.01. y=0, ŷ=0.02 → L ≈ 0.02. Lower is better.'),
    ('Backpropagation',
     'The algorithm that computes how much each weight in the network contributed to the prediction error. It uses the chain rule of calculus to work backwards from the output layer to the input layer, calculating gradients.',
     'After computing loss=0.544, backprop finds that weight w=0.7 should decrease slightly: gradient=0.12 means "if w increases, loss increases". So we subtract η×0.12 from w.'),
    ('Gradient Descent',
     'The optimisation method that updates each weight by a small step in the direction that reduces the loss. Formula: w_new = w_old − η × (∂Loss/∂w). Repeated over many iterations, the loss converges toward a minimum.',
     'w=0.7, gradient=0.12, η=0.1 → w_new = 0.7 − 0.1×0.12 = 0.688. The weight moved a small step closer to a value that produces lower loss.'),
    ('Learning Rate (η)',
     'A hyperparameter that controls how large each weight update step is during gradient descent. Too large: training overshoots and becomes unstable. Too small: training is slow. Typical values: 0.001 to 0.01.',
     'η=1.0 (too large): weights oscillate and loss goes up. η=0.0001 (too small): needs 10× more epochs. η=0.01 (good): loss steadily decreases each epoch.'),
    ('Epoch',
     'One complete pass through the entire training dataset — every sample is seen once by the network. Training runs for many epochs until the loss stops improving. Typical range: 10 to 1000 epochs.',
     'With 5 training samples: Epoch 1 shows loss=0.95. After 100 epochs the loss drops to 0.15, and after 200 epochs to 0.05, showing the network is converging.'),
    ('Batch Size',
     'The number of training samples processed together before the weights are updated. Full batch uses all data at once (stable but slow). Mini-batch (32–256) balances speed and stability. Stochastic uses 1 sample.',
     'With 1000 training images and batch size=32: each epoch processes 1000÷32 ≈ 31 batches. Weights update 31 times per epoch instead of just once.'),
    ('Normalisation',
     'Scaling raw input values to a small consistent range (usually 0–1 or −1 to +1) before feeding them to the network. Prevents large values from dominating small ones and speeds up training significantly.',
     'Pixel value 200 ÷ 255 = 0.784. Study hours 8 ÷ 10 = 0.8. Without normalisation, a 200-pixel value would have 200× more influence on the weighted sum than a 1-hour study value.'),

    # SECTION: Image Processing
    ('__section__', 'Part 4 — Image Processing'),
    ('Grayscale Image',
     'An image where each pixel is represented by a single number from 0 (pure black) to 255 (pure white), encoding only brightness with no colour information. It requires only 1 channel of data.',
     'An 8×8 grayscale image has 64 pixel values: [20, 30, 40, 25, 140, 160, 200, 220, ...]. After normalisation: [0.08, 0.12, 0.16, 0.10, 0.55, 0.63, 0.78, 0.86, ...].'),
    ('RGB Image',
     'A colour image where each pixel has three separate values — Red, Green, and Blue — each ranging from 0 to 255. The three channels combine to produce every visible colour. An RGB image holds 3× more data than grayscale.',
     'A pixel showing orange has R=210, G=80, B=60. White is R=255, G=255, B=255. An 8×8 RGB image has 8×8×3=192 values vs 64 for grayscale.'),
    ('Flatten',
     'The operation of converting a 2D image grid into a 1D vector so it can be fed into an ANN\'s input layer (which expects a flat list of numbers). Done by reading pixels row by row from top-left to bottom-right.',
     '4×4 image → read Row 1 [10,30,200,220], Row 2 [5,50,210,240], Row 3 [15,80,190,230], Row 4 [20,60,200,250] → flat vector of 16 values fed to 16 input neurons.'),
    ('Weighted Sum (Σ)',
     'The core computation inside each neuron: multiply every input by its corresponding weight, then add all the results together, then add the bias. Written as z = Σ(xᵢ × wᵢ) + b.',
     'Inputs [0.8, 0.7], weights [0.5, −0.3], bias 0.1: z = (0.8×0.5)+(0.7×−0.3)+0.1 = 0.40−0.21+0.10 = 0.29. This z then goes into the activation function.'),
]

# ─────────────────────────────────────────────────────────────
# CNN DOCUMENT
# ─────────────────────────────────────────────────────────────

cnn_entries = [
    ('__section__', 'Part 1 — Dataset & Input'),
    ('Dataset',
     'A collection of labelled examples used to train and evaluate a neural network. Divided into training set (to learn from), validation set (to tune hyperparameters), and test set (to measure final accuracy).',
     'CIFAR-10: 60,000 colour images in 10 classes (cat, dog, car, plane, etc.). 50,000 for training, 10,000 for testing. Each image is 32×32 pixels × 3 channels = 3,072 input values.'),
    ('Pixel Value',
     'A single numeric value representing the brightness or colour intensity of one point in a digital image. In grayscale, one value per pixel (0–255). In RGB, three values per pixel — one for Red, Green, and Blue each.',
     'The top-left pixel of a red strawberry image: R=220, G=40, B=30. Normalised: R=0.863, G=0.157, B=0.118. These three values become three separate inputs to the CNN.'),
    ('Preprocessing',
     'Steps applied to raw data before feeding it to the network: normalising pixel values to 0–1, resizing images to a fixed size, converting to the right format, and optionally augmenting (flipping, rotating) for more training variety.',
     'Raw JPEG image (variable size, uint8 0–255) → resize to 224×224 → divide by 255 → float32 tensor of shape [224,224,3] → ready to enter the CNN.'),

    ('__section__', 'Part 2 — Convolutional Layers'),
    ('Convolutional Layer',
     'The core layer of a CNN. A small filter (e.g. 3×3) slides across the input image at every position, computing a dot product at each step. This produces a Feature Map highlighting where the filter\'s pattern appears in the image.',
     'A 3×3 edge-detection filter slides over a 6×6 image. At each of the 16 positions (with stride 1, no padding), it computes one output value, producing a 4×4 feature map showing where edges were found.'),
    ('Filter / Kernel',
     'A small grid of learnable weights (e.g. 3×3 or 5×5) that slides across the input looking for one specific pattern. Multiple filters in the same layer each detect a different feature (edges, corners, textures, etc.).',
     'A 3×3 horizontal-edge filter: [[−1,−1,−1],[0,0,0],[1,1,1]]. When placed over a horizontal boundary between dark and bright pixels, the dot product gives a large positive value, detecting the edge.'),
    ('Feature Map (Activation Map)',
     'The output produced by applying one filter to an entire input. Each value in the feature map represents how strongly that filter\'s pattern was present at that spatial location. Multiple filters produce multiple feature maps.',
     'Applying 32 different 3×3 filters to a 32×32×3 input produces 32 feature maps of size 30×30, a combined output of shape 30×30×32 — representing 32 detected patterns across the image.'),
    ('Stride',
     'The number of pixels the filter moves each step as it slides across the input. Stride 1 moves one pixel at a time (large output). Stride 2 skips every other position, halving the output size and reducing computation.',
     'A 3×3 filter on a 6×6 input: stride=1 → 4×4 output (16 positions). stride=2 → 2×2 output (4 positions). Larger stride = faster computation but coarser feature map.'),
    ('Padding',
     'Adding extra rows/columns of zeros around the input border before applying convolution. "Valid" padding: no zeros added, output shrinks. "Same" padding: zeros added so output stays the same size as input.',
     'A 3×3 filter on a 6×6 input without padding → 4×4 output. With "same" padding (one row/col of zeros each side) → 6×6 output. Padding preserves spatial dimensions after convolution.'),
    ('Weight Sharing',
     'In a CNN, the same filter weights are used at every spatial position when sliding across the image. This means a "cat ear" detector learned at one location of an image automatically works everywhere in the image.',
     'A 3×3 filter with 9 weights detects horizontal edges anywhere in a 224×224 image. Without weight sharing, you would need a unique set of weights for each of the 224×224=50,176 positions.'),

    ('__section__', 'Part 3 — Activation & Pooling'),
    ('ReLU (Rectified Linear Unit)',
     'The activation function applied after each convolution. It replaces any negative value with zero and keeps positive values unchanged: f(z)=max(0,z). Introduces non-linearity and prevents vanishing gradients during training.',
     'Feature map values [−0.5, 1.2, −0.3, 0.8] after ReLU → [0, 1.2, 0, 0.8]. The two negative "non-activations" are silenced; only positive detections pass forward.'),
    ('Max Pooling',
     'A down-sampling operation that divides the feature map into small regions and keeps only the maximum value from each. Reduces spatial size, makes the network robust to small shifts/translations, and reduces computation.',
     '2×2 max pool with stride 2 on [[1,3,2,4],[5,6,7,8],[9,2,3,1],[4,6,2,8]]: top-left 2×2 gives max=6, top-right=8, bottom-left=9, bottom-right=8 → output [[6,8],[9,8]]. Size halved from 4×4 to 2×2.'),
    ('Receptive Field',
     'The region of the original input image that influences a particular neuron\'s output. Early layers have small receptive fields (see fine details). Deeper layers have large receptive fields (see large patterns or whole objects).',
     'Layer 1 neurons see 3×3 input region (detect edges). Layer 2 neurons see 5×5 region (detect corners). Layer 5 neurons may see 32×32 region (detect whole faces or objects).'),

    ('__section__', 'Part 4 — Dense Layers & Output'),
    ('Flatten Layer',
     'Converts the 3D output of the last convolutional/pooling layer (height × width × channels) into a 1D vector. This is required before feeding the data into fully-connected Dense layers.',
     'Last pooling layer output shape: 4×4×64 = 1,024 values. Flatten converts this to a vector [v₁, v₂, ..., v₁₀₂₄] that a Dense layer can process.'),
    ('Dense Layer (Fully Connected)',
     'A layer where every neuron connects to every neuron in the previous layer. It combines all detected features to make the final classification decision. Typically placed after the convolutional layers.',
     'Flattened vector of 1,024 values feeds into a Dense layer of 256 neurons. Each of the 256 neurons has 1,024 weights, giving 256×1,024=262,144 parameters just for this one layer.'),
    ('Dropout',
     'A regularisation technique that randomly sets a fraction of neurons to zero during training (e.g. 50% chance each). Forces the network to not rely on any single neuron, reducing overfitting and improving generalisation.',
     'Before dropout: [0.8, 0.5, 0.3, 0.9, 0.2]. With Dropout(0.5): [0, 0.5, 0, 0.9, 0] — two neurons randomly silenced. At test time, dropout is turned off and all neurons are active.'),
    ('Overfitting',
     'When a model learns the training data too specifically — including noise — and performs poorly on new unseen data. Signs: training accuracy 99%, test accuracy 65%. Prevented by dropout, regularisation, and more data.',
     'A CNN trained on 100 cat images with no dropout memorises them: 99% training accuracy but only 60% on new cat photos. Adding Dropout(0.5) improves test accuracy to 85%.'),
    ('Softmax Output',
     'The final layer of a multi-class CNN, converting raw scores into class probabilities that sum to 1. The class with the highest probability is the prediction.',
     'For 10-class CIFAR-10: raw scores [1.2, 0.3, 3.7, ...] → Softmax → [0.04, 0.02, 0.55, ...]. Class 3 (bird) has 55% probability and is chosen as the prediction.'),

    ('__section__', 'Part 5 — Training'),
    ('Loss Function',
     'Measures how wrong the CNN\'s predictions are. Minimised during training. Categorical Cross-Entropy is standard for multi-class problems; Binary Cross-Entropy for two-class problems.',
     'True class: cat (index 3). CNN output probabilities: [0.02,0.01,0.01,0.85,0.02,...]. Loss = −log(0.85) = 0.163. If it had predicted 0.20 for cat: loss = −log(0.20) = 1.61 — much higher.'),
    ('Backpropagation',
     'The algorithm that computes gradients for every weight in the CNN by applying the chain rule from output to input. Each filter\'s weights are nudged to reduce the loss after every batch of training examples.',
     'Loss = 0.54. Backprop flows backwards: output layer → Dense layer → Flatten → Pool → Conv layer 3 → Conv layer 2 → Conv layer 1. Each filter\'s 9 weights get their own gradient update.'),
    ('Batch Normalisation',
     'A technique applied after a layer that normalises the layer\'s outputs to have mean≈0 and variance≈1 within each training mini-batch. Stabilises training, allows higher learning rates, and acts as mild regularisation.',
     'Conv layer outputs spread: [−5.2, 0.3, 12.1, −0.8]. Batch Norm rescales them to approximately [−0.7, 0.1, 1.4, −0.2]. This prevents later layers from seeing wildly varying input scales.'),
    ('Training Loop',
     'The repeated cycle: (1) Forward pass → predict. (2) Compute loss. (3) Backward pass → compute gradients. (4) Update weights. This repeats for every mini-batch, for many epochs, until the model converges.',
     'Epoch 1: loss=2.1, accuracy=12%. Epoch 10: loss=1.4, accuracy=48%. Epoch 50: loss=0.6, accuracy=80%. Epoch 100: loss=0.3, accuracy=92%. The loop runs until improvement plateaus.'),
]

# ─────────────────────────────────────────────────────────────
# YOLO DOCUMENT
# ─────────────────────────────────────────────────────────────

yolo_entries = [
    ('__section__', 'Part 1 — YOLO Fundamentals'),
    ('YOLO (You Only Look Once)',
     'A family of real-time object detection models. Unlike earlier methods that process an image multiple times, YOLO passes the image through the CNN exactly once and simultaneously predicts all bounding boxes and classes.',
     'R-CNN: feeds 2,000 region crops into CNN separately → slow. YOLO: feeds 1 image → single CNN pass → outputs all detections at once. YOLOv8n achieves ~80 FPS on a GPU for real-time video.'),
    ('Single-Pass Detection',
     'YOLO\'s defining characteristic: the entire image goes through the network once. The CNN processes all spatial locations simultaneously, making detection much faster than region-proposal methods.',
     'R-CNN runs CNN 2,000 times per image (once per candidate region). YOLO runs CNN once: 640×640 image → [backbone→neck→head] → 8,400 box predictions, all in one forward pass.'),
    ('R-CNN (Region-based CNN)',
     'An earlier object detection approach that first generates ~2,000 candidate region proposals using selective search, then runs a CNN separately on each region. Accurate but extremely slow (47 seconds per image).',
     'R-CNN on a 640×640 image: Selective Search → 2,000 regions → run VGG-16 on each → 2,000 × CNN forward passes → classify each region → output. YOLO replaces this with 1 forward pass.'),
    ('Darknet Framework',
     'An open-source neural network framework written in C and CUDA by Joseph Redmon. Used to train and run YOLOv1–v4. It is designed for speed on GPUs and CPUs. Later versions (v5–v11) moved to PyTorch.',
     'Darknet trains YOLOv3 with: ./darknet detector train cfg/coco.data cfg/yolov3.cfg darknet53.conv.74. The C/CUDA implementation runs faster than Python on embedded devices like Jetson Nano.'),
    ('Anchor Boxes',
     'Predefined bounding box shapes of various aspect ratios and scales, used in YOLOv2–v8. The network predicts adjustments to these anchors rather than predicting box coordinates from scratch, making learning easier.',
     'Three anchors: [(10×13), (16×30), (33×23)] pixels. A car in the image best matches anchor (33×23). The network predicts small offsets (Δx=0.2, Δy=−0.1, Δw=1.4, Δh=0.9) to refine the anchor into the exact box.'),
    ('Grid System',
     'YOLO divides the input image into an S×S grid (e.g. 80×80, 40×40, 20×20). Each grid cell is responsible for detecting objects whose centre falls within that cell. This gives YOLO its spatial structure.',
     'Image divided into 80×80 grid = 6,400 cells. A dog\'s centre is at pixel (320,240) on a 640×640 image → grid cell (40,30). That cell\'s predictions are responsible for detecting the dog.'),
    ('mAP (mean Average Precision)',
     'The standard metric for evaluating object detection models. Precision measures how many detections were correct; Recall measures how many true objects were found. AP averages this over all confidence thresholds; mAP averages AP over all classes.',
     'On COCO dataset: YOLOv8n mAP₅₀₋₉₅=37.3%. This means: across all 80 classes, averaging precision at IoU thresholds from 0.50 to 0.95, the model is correct 37.3% of the time. YOLOv8x achieves 53.9%.'),
    ('FPS (Frames Per Second)',
     'A measure of detection speed — how many images the model can process per second. Higher FPS = faster, enabling real-time video. Larger models are more accurate but slower; nano models prioritise speed.',
     'YOLOv8n: ~80 FPS on GPU (real-time for 30 FPS video). YOLOv8x: ~20 FPS on same GPU (still real-time, more accurate). Running on CPU: YOLOv8n ~5 FPS (barely real-time), YOLOv8x ~1 FPS.'),

    ('__section__', 'Part 2 — YOLOv8 Architecture'),
    ('Backbone',
     'The first part of a YOLO network that processes the raw image and extracts multi-scale feature representations. It is typically a deep CNN pre-trained on large datasets. YOLOv8 uses CSPDarknet with C2f modules.',
     'YOLOv8n backbone: image [640×640×3] → after 5 stages of convolution+pooling → feature maps at scales [80×80×128], [40×40×256], [20×20×512]. Each scale captures different detail levels.'),
    ('Neck (Feature Pyramid Network)',
     'The middle section of YOLO that combines feature maps from different backbone scales. It fuses low-resolution (large receptive field) and high-resolution (fine detail) features to improve detection at all object sizes.',
     'PAN-FPN neck: takes backbone outputs [80×80], [40×40], [20×20] → upsample and merge them → produces enriched feature maps at each scale. Now the 80×80 map has both fine detail AND context from the 20×20 map.'),
    ('Head',
     'The final part of the network that makes actual predictions from the neck\'s feature maps. In YOLOv8 the head is decoupled — separate branches for classification (what) and regression (where), at three scales.',
     'For each of the 8,400 candidate positions (6400+1600+400), the head outputs: box coordinates [x,y,w,h], objectness confidence score, and class probabilities [80 classes for COCO]. Final output: all objects in the image.'),
    ('CSPDarknet',
     'Cross Stage Partial Network — the backbone architecture used in YOLOv4 onward. It splits the feature map into two paths: one goes through the dense block, one skips ahead. Both are concatenated at the end, reducing redundancy.',
     'Without CSP: layer output copied to every next layer → huge memory. With CSP: 50% of channels go through Conv layers, 50% skip → then merge. YOLOv8n achieves similar accuracy to YOLOv5s with 30% fewer parameters.'),
    ('C2f Module',
     'YOLOv8\'s feature extraction building block (Cross-Stage Partial with 2 bottleneck branches). It improves upon C3 by enabling richer gradient flow during training while keeping the model compact.',
     'C2f input: 256-channel feature map → split → Branch 1: through 2 bottlenecks (learns complex patterns). Branch 2: direct connection. Both merged → 256-channel output. Replaces the C3 block from YOLOv5.'),
    ('SPPF (Spatial Pyramid Pooling Fast)',
     'A module at the end of the backbone that applies max pooling three times with the same small kernel, then concatenates all results. It captures context at multiple effective scales without heavy computation.',
     'Input feature map [20×20×512] → MaxPool(5×5) → MaxPool(5×5) → MaxPool(5×5) → concatenate all four [original + 3 pooled] → [20×20×2048] → 1×1 conv → [20×20×512]. Efficient multi-scale context.'),
    ('PAN-FPN (Path Aggregation Network + Feature Pyramid)',
     'The neck architecture that enables bidirectional feature flow: top-down (FPN path, sends semantic info downward) and bottom-up (PAN path, sends fine spatial details upward). Both paths combined improve all-scale detection.',
     'FPN top-down: 20×20 deep features → upsample to 40×40 → merge with backbone 40×40. PAN bottom-up: 40×40 result → downsample to 20×20 → merge again. Every scale level now sees both local detail and global context.'),
    ('SiLU Activation',
     'Sigmoid Linear Unit — the activation function used in YOLOv8, defined as SiLU(x) = x × sigmoid(x). It is smooth, non-monotonic, and has been shown to outperform ReLU on deep networks like YOLO backbones.',
     'SiLU(1.0) = 1.0×0.731 = 0.731; SiLU(−1.0) = −1.0×0.269 = −0.269; SiLU(0) = 0. Unlike ReLU which hard-clips at 0, SiLU allows small negative values, preserving gradient flow for negative activations.'),

    ('__section__', 'Part 3 — Detection & Evaluation'),
    ('Bounding Box',
     'A rectangle described by four values [x, y, w, h] that locates a detected object in the image. x,y are the centre coordinates; w,h are width and height — all normalised relative to the image size (0 to 1).',
     'Dog detected at: x=0.5 (centre of image), y=0.6, w=0.3 (30% of image width), h=0.4 (40% of image height). On a 640×640 image: centre at (320,384), box size 192×256 pixels.'),
    ('Confidence Score',
     'A value from 0 to 1 that represents how certain the model is that a bounding box contains an object and belongs to the predicted class. Boxes below a threshold (e.g. 0.25) are discarded.',
     'Detection: [car, confidence=0.92] → kept. [car, confidence=0.18] → discarded (below 0.25 threshold). The 0.92 score comes from objectness × class probability: 0.97 × 0.95 = 0.92.'),
    ('IoU (Intersection over Union)',
     'A metric measuring how much two bounding boxes overlap. Computed as (area of overlap) ÷ (area of union). Used to judge whether a detection matches a ground-truth box. IoU > 0.5 is typically considered a correct detection.',
     'Predicted box covers 60 pixels², ground-truth box covers 80 pixels². Overlap area = 50 pixels². Union = 60+80−50=90 pixels². IoU = 50/90 = 0.556 > 0.5 → counted as correct detection.'),
    ('NMS (Non-Maximum Suppression)',
     'A post-processing step that removes duplicate detections. When multiple bounding boxes detect the same object, NMS keeps the one with the highest confidence and removes all others that overlap it by more than an IoU threshold.',
     'Three boxes detected for one car: [conf=0.95,IoU w/each other=0.8], [conf=0.88], [conf=0.72]. NMS: keep 0.95 (highest confidence), discard 0.88 and 0.72 (IoU > 0.5 threshold with the kept box). Final: 1 detection.'),
    ('Anchor-Free Detection',
     'An approach (used in YOLOv8+) where the model directly predicts bounding box coordinates without relying on predefined anchor shapes. Simplifies training, eliminates anchor tuning, and improves accuracy on varied object shapes.',
     'Anchor-based YOLOv5: predicts offsets [Δx,Δy,Δw,Δh] relative to fixed anchor (30×60). Anchor-free YOLOv8: directly predicts [cx=0.51, cy=0.62, w=0.28, h=0.41] from scratch — no anchor shapes needed.'),
    ('Decoupled Head',
     'A prediction head design where the classification task (what class?) and the regression task (where is it?) have separate processing branches. YOLOv8 uses decoupled heads, which improves accuracy compared to shared heads.',
     'Coupled head (YOLOv5): one set of Conv layers → outputs both class probs and box coords together. Decoupled (YOLOv8): Branch A → box [x,y,w,h]. Branch B → class probabilities [80 values]. Each branch specialises independently.'),
    ('DFL Loss (Distribution Focal Loss)',
     'A loss function used in YOLOv8 for bounding box regression. Instead of predicting a single box coordinate value, it predicts a probability distribution over possible values, making box boundary prediction more precise.',
     'Classic regression: predict box right-edge = 150px directly. DFL: predict a distribution [p(140)=0.1, p(145)=0.2, p(150)=0.5, p(155)=0.2] → weighted average = 150px. More stable for ambiguous boundaries.'),
    ('TAL (Task-Aligned Learning)',
     'YOLOv8\'s training assignment strategy that determines which predicted boxes are matched to which ground-truth objects during training. It uses a combined score of classification accuracy and box IoU to create better assignments.',
     'Old strategy: assign box to ground truth purely by IoU. TAL: score = (class_prob)^α × (IoU)^β. A box with 0.8 class confidence and 0.75 IoU scores: 0.8×0.75=0.60. Better boxes are rewarded; ambiguous cases resolved more accurately.'),
]

# ─────────────────────────────────────────────────────────────
# BUILD DOCUMENTS
# ─────────────────────────────────────────────────────────────

docs = [
    ('ann_vocabulary_description.docx',  ann_entries,  '3fb950', 'Artificial Neural Networks',  'Fundamentals • Grayscale • RGB Images'),
    ('cnn_vocabulary_description.docx',  cnn_entries,  '58a6ff', 'Convolutional Neural Networks', 'Architecture • Layers • Training'),
    ('yolo_vocabulary_description.docx', yolo_entries, 'f0883e', 'YOLO Object Detection',        'Versions • Architecture • YOLOv8'),
]

for filename, entries, accent, title, subtitle in docs:
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    add_title_page(doc, title, subtitle, accent)

    num = 1
    for entry in entries:
        if entry[0] == '__section__':
            add_section_header(doc, entry[1], accent)
        else:
            vocab, description, example = entry
            add_entry(doc, num, vocab, description, example, accent)
            num += 1

    doc.save(f'/home/user/git_test/{filename}')
    print(f'Saved {filename}  ({num-1} entries)')

print('Done.')
