yolo_versions = [
    {"version": "YOLOv1", "description": "Original YOLO by Joseph Redmon; single-pass detection, fast but less accurate on small objects"},
    {"version": "YOLOv2 (YOLO9000)", "description": "Added anchor boxes, batch normalization, and multi-scale training; detects 9000+ classes"},
    {"version": "YOLOv3", "description": "Multi-scale predictions using feature pyramid; improved small object detection"},
    {"version": "YOLOv4", "description": "By Alexey Bochkovskiy; introduced CSPNet backbone (CSPDarknet53) and mosaic augmentation"},
    {"version": "YOLOv5", "description": "By Ultralytics; PyTorch-native, easy to use, multiple model sizes (n/s/m/l/x)"},
    {"version": "YOLOv6", "description": "By Meituan; focused on industrial applications with efficient reparameterization"},
    {"version": "YOLOv7", "description": "By WongKinYiu; extended efficient layer aggregation (E-ELAN), state-of-the-art speed/accuracy"},
    {"version": "YOLOv8", "description": "By Ultralytics; unified framework for detection, segmentation, pose, and classification"},
    {"version": "YOLOv9", "description": "Introduced Programmable Gradient Information (PGI) and Generalized ELAN (GELAN)"},
    {"version": "YOLOv10", "description": "By Tsinghua University; NMS-free end-to-end detection with dual-assignment training"},
    {"version": "YOLOv11", "description": "By Ultralytics; improved architecture efficiency and accuracy across all task types"},
]

for item in yolo_versions:
    print(f"{item['version']}: {item['description']}")
