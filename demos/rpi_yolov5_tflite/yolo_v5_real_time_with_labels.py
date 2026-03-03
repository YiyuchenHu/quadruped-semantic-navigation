#!/usr/bin/env python3
"""
YOLOv5 Real-Time Object Detection with Labels
Raspberry Pi Camera + TensorFlow Lite

This script demonstrates real-time object detection using YOLOv5 TFLite models
with the patched Picamera2 library.
"""

import argparse
import time
from pathlib import Path

import cv2
import numpy as np
from picamera2 import Picamera2

# Default model path
DEFAULT_MODEL_PATH = Path(__file__).parent / "models" / "yolov5s-int8.tflite"

# COCO class names (YOLOv5 default)
CLASS_NAMES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
    'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
    'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
    'toothbrush'
]


def load_tflite_model(model_path):
    """Load TensorFlow Lite model"""
    try:
        import tflite_runtime.interpreter as tflite
    except ImportError:
        raise ImportError("TensorFlow Lite runtime not found. Install with: pip install tflite-runtime")
    
    interpreter = tflite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    return interpreter


def preprocess_image(image, input_size=(640, 640)):
    """Preprocess image for YOLOv5 input"""
    # Resize and pad
    h, w = image.shape[:2]
    scale = min(input_size[0] / h, input_size[1] / w)
    new_h, new_w = int(h * scale), int(w * scale)
    
    resized = cv2.resize(image, (new_w, new_h))
    padded = np.full((input_size[0], input_size[1], 3), 114, dtype=np.uint8)
    padded[:new_h, :new_w] = resized
    
    # Convert to RGB and normalize
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    normalized = rgb.astype(np.float32) / 255.0
    
    # Add batch dimension
    return np.expand_dims(normalized, axis=0)


def postprocess_output(output, conf_threshold=0.25, iou_threshold=0.45):
    """Postprocess YOLOv5 output to get detections"""
    # YOLOv5 output format: [batch, num_detections, 85]
    # 85 = 4 (bbox) + 1 (objectness) + 80 (classes)
    
    detections = []
    output = output[0]  # Remove batch dimension
    
    for detection in output:
        x, y, w, h, obj_conf = detection[:5]
        class_scores = detection[5:]
        
        if obj_conf < conf_threshold:
            continue
        
        class_id = np.argmax(class_scores)
        class_conf = class_scores[class_id]
        confidence = obj_conf * class_conf
        
        if confidence < conf_threshold:
            continue
        
        detections.append({
            'bbox': [x, y, w, h],
            'confidence': confidence,
            'class_id': int(class_id),
            'class_name': CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f'class_{class_id}'
        })
    
    # Apply NMS (simplified version)
    # TODO: Implement proper NMS if needed
    
    return detections


def draw_detections(image, detections):
    """Draw bounding boxes and labels on image"""
    h, w = image.shape[:2]
    
    for det in detections:
        x, y, w_box, h_box = det['bbox']
        # Convert from center format to corner format
        x1 = int((x - w_box / 2) * w)
        y1 = int((y - h_box / 2) * h)
        x2 = int((x + w_box / 2) * w)
        y2 = int((y + h_box / 2) * h)
        
        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label
        label = f"{det['class_name']}: {det['confidence']:.2f}"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), (0, 255, 0), -1)
        cv2.putText(image, label, (x1, y1 - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    return image


def main():
    parser = argparse.ArgumentParser(description='YOLOv5 Real-Time Detection Demo')
    parser.add_argument('--model', type=str, default=str(DEFAULT_MODEL_PATH),
                        help='Path to TFLite model file')
    parser.add_argument('--width', type=int, default=640,
                        help='Camera width')
    parser.add_argument('--height', type=int, default=480,
                        help='Camera height')
    parser.add_argument('--conf-threshold', type=float, default=0.25,
                        help='Confidence threshold')
    args = parser.parse_args()
    
    # Check model file
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        print("Please download a YOLOv5 TFLite model and place it in the models/ directory")
        return
    
    # Load model
    print(f"Loading model: {model_path}")
    interpreter = load_tflite_model(model_path)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    input_size = input_details[0]['shape'][1:3]  # [height, width]
    print(f"Model input size: {input_size}")
    
    # Initialize camera
    print("Initializing camera...")
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(
        main={"size": (args.width, args.height)}
    ))
    picam2.start()
    
    print("Starting detection loop. Press 'q' to quit.")
    
    fps_counter = 0
    fps_start_time = time.time()
    
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Preprocess
            input_data = preprocess_image(frame, input_size)
            
            # Run inference
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            
            # Postprocess
            detections = postprocess_output(output_data, args.conf_threshold)
            
            # Draw detections
            frame_with_detections = draw_detections(frame.copy(), detections)
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter % 30 == 0:
                fps = 30 / (time.time() - fps_start_time)
                fps_start_time = time.time()
                print(f"FPS: {fps:.2f}, Detections: {len(detections)}")
            
            # Display
            cv2.imshow('YOLOv5 Detection', frame_with_detections)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        print("Demo ended.")


if __name__ == '__main__':
    main()
