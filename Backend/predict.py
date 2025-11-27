"""
Use trained breast cancer detection model to predict on new images
"""

import numpy as np
import cv2
from tensorflow import keras
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

def load_model(model_path):
    """Load the trained model"""
    print(f"Loading model from {model_path}...")
    model = keras.models.load_model(model_path)
    print("Model loaded successfully!")
    return model

def preprocess_image(image_path, img_size=(224, 224)):
    """Load and preprocess an image for prediction (matches training preprocessing)"""
    print(f"Loading image: {image_path}")
    
    # Read image
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Create a mask to find the breast tissue (non-black regions)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Threshold to find non-black regions (breast tissue)
    # Use Otsu's method for automatic thresholding
    _, tissue_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Apply morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    tissue_mask = cv2.morphologyEx(tissue_mask, cv2.MORPH_CLOSE, kernel)
    tissue_mask = cv2.morphologyEx(tissue_mask, cv2.MORPH_OPEN, kernel)
    
    # Find the bounding box of the breast tissue
    contours, _ = cv2.findContours(tissue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Get the largest contour (main breast tissue)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Add some padding (10%)
        pad_w, pad_h = int(w * 0.1), int(h * 0.1)
        x = max(0, x - pad_w)
        y = max(0, y - pad_h)
        w = min(img.shape[1] - x, w + 2 * pad_w)
        h = min(img.shape[0] - y, h + 2 * pad_h)
        
        # Crop to breast tissue region
        img = img[y:y+h, x:x+w]
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance tissue
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Convert back to RGB
    img = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    
    # Resize to target size
    img = cv2.resize(img, img_size)
    
    # Normalize to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

def get_gradcam_heatmap(model, img_array, last_conv_layer_name=None):
    """Generate Grad-CAM heatmap to show which regions the model focuses on"""
    try:
        # Find the base model (EfficientNet or ResNet)
        base_model = None
        for layer in model.layers:
            if 'efficientnet' in layer.name.lower() or 'resnet' in layer.name.lower():
                base_model = layer
                break
        
        if base_model is None:
            print("Warning: Could not find base model (EfficientNet or ResNet)")
            return None
        
        # Get the last convolutional layer from the base model
        # For EfficientNet, use 'top_activation' which is after top_conv and top_bn
        if last_conv_layer_name is None:
            last_conv_layer_name = 'top_activation'
        
        last_conv_layer = base_model.get_layer(last_conv_layer_name)
        
        # Create a model that outputs the last conv layer activations
        efficientnet_output_model = keras.Model(
            inputs=base_model.inputs,
            outputs=last_conv_layer.output
        )
        
        # Create a model from conv outputs to final prediction
        # We need to manually pass through the remaining layers
        classifier_input = keras.Input(shape=last_conv_layer.output.shape[1:])
        x = classifier_input
        
        # Apply the layers after the base model
        for layer in model.layers[2:]:  # Skip input and base model layers
            x = layer(x)
        
        classifier_model = keras.Model(classifier_input, x)
        
        # Now compute gradients
        with tf.GradientTape() as tape:
            # Get conv outputs from base model
            conv_outputs = efficientnet_output_model(img_array)
            tape.watch(conv_outputs)
            
            # Get predictions from classifier
            predictions = classifier_model(conv_outputs)
            loss = predictions[:, 0]
        
        # Extract the gradients
        grads = tape.gradient(loss, conv_outputs)
        
        if grads is None:
            print("Warning: Could not compute gradients")
            return None
        
        # Compute the guided gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight the channels by the gradients
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Normalize the heatmap
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
        return heatmap.numpy()
    except Exception as e:
        print(f"Warning: Could not generate Grad-CAM heatmap: {e}")
        import traceback
        traceback.print_exc()
        return None

def find_roi_bbox(heatmap, threshold=0.5):
    """Find bounding box of the suspicious region from heatmap"""
    # Threshold the heatmap
    mask = (heatmap > threshold).astype(np.uint8) * 255
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Get the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    return (x, y, w, h)

def assess_risk_level(probability):
    """Assess risk level based on malignancy probability"""
    if probability >= 0.8:
        return "HIGH RISK", "Strongly suspicious for malignancy"
    elif probability >= 0.6:
        return "MODERATE-HIGH RISK", "Suspicious findings, recommend biopsy"
    elif probability >= 0.4:
        return "MODERATE RISK", "Indeterminate findings, close follow-up"
    elif probability >= 0.2:
        return "LOW-MODERATE RISK", "Probably benign, routine follow-up"
    else:
        return "LOW RISK", "Benign findings"

def generate_diagnostic_report(prediction, probability, confidence):
    """Generate detailed diagnostic information"""
    risk_level, assessment = assess_risk_level(probability)
    
    report = {
        'primary_diagnosis': prediction,
        'malignancy_probability': f"{probability:.1%}",
        'benign_probability': f"{(1-probability):.1%}",
        'confidence': f"{confidence:.1%}",
        'risk_level': risk_level,
        'clinical_assessment': assessment,
        'birads_equivalent': get_birads_category(probability),
        'recommendation': get_recommendation(probability)
    }
    
    return report

def get_birads_category(probability):
    """Map probability to BI-RADS-like category"""
    if probability >= 0.95:
        return "BI-RADS 5 - Highly suggestive of malignancy (>95%)"
    elif probability >= 0.75:
        return "BI-RADS 4C - High suspicion (50-95%)"
    elif probability >= 0.5:
        return "BI-RADS 4B - Moderate suspicion (10-50%)"
    elif probability >= 0.2:
        return "BI-RADS 4A - Low suspicion (2-10%)"
    elif probability >= 0.02:
        return "BI-RADS 3 - Probably benign (<2%)"
    else:
        return "BI-RADS 2 - Benign finding"

def get_recommendation(probability):
    """Provide clinical recommendation based on probability"""
    if probability >= 0.75:
        return "URGENT: Tissue diagnosis recommended (biopsy)"
    elif probability >= 0.5:
        return "Biopsy recommended for definitive diagnosis"
    elif probability >= 0.3:
        return "Short-term follow-up (3-6 months) or consider biopsy"
    elif probability >= 0.1:
        return "Routine follow-up in 6-12 months"
    else:
        return "Continue routine screening"

def visualize_prediction(image_path, heatmap, bbox, diagnostic_report, output_path=None, target_size=(224, 224)):
    """Create visualization with heatmap overlay and bounding box"""
    # Load original image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, target_size)
    
    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Original image
    axes[0].imshow(img_resized)
    axes[0].set_title('Original Image', fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    # Heatmap overlay
    axes[1].imshow(img_resized)
    if heatmap is not None:
        # **FIX:** The 'heatmap' passed in is already resized, so no need to resize again
        axes[1].imshow(heatmap, cmap='jet', alpha=0.5)
    axes[1].set_title('Attention Map (Grad-CAM)', fontsize=14, fontweight='bold')
    axes[1].axis('off')
    
    # Image with red square
    axes[2].imshow(img_resized)
    if bbox is not None:
        x, y, w, h = bbox
        
        # **FIX:** The bbox coordinates are now correctly scaled to the target_size (e.g., 224x224)
        # because find_roi_bbox was called on the resized heatmap.
        
        # Draw red square around suspicious region
        rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=4, edgecolor='red', facecolor='none'
        )
        axes[2].add_patch(rect)
        
        # Draw crosshair at center
        center_x = x + w // 2
        center_y = y + h // 2
        axes[2].plot(center_x, center_y, 'r+', markersize=20, markeredgewidth=3)
    axes[2].set_title('Suspicious Region', fontsize=14, fontweight='bold')
    axes[2].axis('off')
    
    # Add diagnostic info as text
    info_text = f"""DIAGNOSIS: {diagnostic_report['primary_diagnosis']}
Risk Level: {diagnostic_report['risk_level']}
Malignancy: {diagnostic_report['malignancy_probability']}
{diagnostic_report['birads_equivalent']}
{diagnostic_report['recommendation']}"""
    
    plt.suptitle(info_text, fontsize=11, y=0.02, fontfamily='monospace', 
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save or show
    if output_path is None:
        # Save in current directory instead of nested jpeg folder
        base_name = os.path.basename(image_path)
        output_path = base_name.replace('.jpg', '_diagnosis.jpg').replace('.png', '_diagnosis.png')
    
    try:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {output_path}")
    except PermissionError:
        # If permission denied, save to current directory
        fallback_path = os.path.basename(output_path)
        plt.savefig(fallback_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {fallback_path}")
    
    plt.close()

def predict(model, image_path, threshold=0.5, visualize=True):
    """Make prediction on a single image with detailed diagnosis"""
    # --- START OF FIX ---
    img_size = (224, 224) # Define target size
    
    # Preprocess image
    img = preprocess_image(image_path, img_size)
    # --- END OF FIX ---
    
    # Make prediction
    print("Making prediction...")
    prediction_proba = model.predict(img, verbose=0)[0][0]
    
    # Convert to binary prediction
    prediction = "MALIGNANT" if prediction_proba > threshold else "BENIGN"
    confidence = prediction_proba if prediction_proba > threshold else (1 - prediction_proba)
    
    # Generate Grad-CAM heatmap
    print("Generating attention map...")
    heatmap_small = get_gradcam_heatmap(model, img) # This is the small (e.g., 7x7) heatmap
    
    # --- START OF FIX ---
    bbox = None
    heatmap_resized = None # This will be our full 224x224 heatmap
    
    if heatmap_small is not None:
        # Resize the small heatmap to match the input image size
        heatmap_resized = cv2.resize(heatmap_small, img_size, interpolation=cv2.INTER_LINEAR)
        
        # Now, find the bounding box on the *full-size* resized heatmap
        bbox = find_roi_bbox(heatmap_resized, threshold=0.5)
    # --- END OF FIX ---
    
    # If no bbox detected but malignancy probability is above 20%, mark center region
    if bbox is None and prediction_proba >= 0.2:
        # Create a default bounding box in the center of the image
        center_val = img_size[0] // 4
        size_val = img_size[0] // 2
        bbox = (center_val, center_val, size_val, size_val) # e.g., (56, 56, 112, 112)
        print("Note: Using center region as default suspicious area")
    
    # Generate diagnostic report
    diagnostic_report = generate_diagnostic_report(prediction, prediction_proba, confidence)
    
    # Display results
    print("\n" + "="*70)
    print("DETAILED DIAGNOSTIC REPORT")
    print("="*70)
    print(f"Image: {image_path}")
    print(f"\nPrimary Diagnosis:      {diagnostic_report['primary_diagnosis']}")
    print(f"Risk Level:             {diagnostic_report['risk_level']}")
    print(f"\nProbabilities:")
    print(f"  Malignant:            {diagnostic_report['malignancy_probability']}")
    print(f"  Benign:               {diagnostic_report['benign_probability']}")
    print(f"  Confidence:           {diagnostic_report['confidence']}")
    print(f"\nAssessment:             {diagnostic_report['birads_equivalent']}")
    print(f"Clinical Note:          {diagnostic_report['clinical_assessment']}")
    print(f"\nRecommendation:         {diagnostic_report['recommendation']}")
    
    if bbox:
        print(f"\nSuspicious Region:      Detected at coordinates {bbox}")
    else:
        print(f"\nSuspicious Region:      No focal region detected")
    
    print("="*70)
    
    # Create visualization
    if visualize:
        print("\nCreating visualization...")
        # --- START OF FIX ---
        # Pass the *resized* heatmap to the visualizer
        visualize_prediction(image_path, heatmap_resized, bbox, diagnostic_report, target_size=img_size)
        # --- END OF FIX ---
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'probability': prediction_proba,
        'diagnostic_report': diagnostic_report,
        'bbox': bbox,
        'heatmap': heatmap_resized # Return the full-size heatmap
    }

def predict_batch(model, image_paths, threshold=0.5):
    """Make predictions on multiple images"""
    results = []
    
    for img_path in image_paths:
        try:
            result = predict(model, img_path, threshold)
            results.append({
                'image': img_path,
                **result
            })
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            results.append({
                'image': img_path,
                'error': str(e)
            })
    
    return results

# Example usage
if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path> [model_path] [threshold]")
        print("\nExample:")
        print("  python predict.py my_image.jpg")
        print("  python predict.py my_image.jpg best_cbis_ddsm_model.keras")
        print("  python predict.py my_image.jpg best_cbis_ddsm_model.keras 0.5")
        print("\nThis will generate a detailed diagnosis with visualization.")
        sys.exit(1)
    
    # Get arguments
    image_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 else "best_cbis_ddsm_model.keras"
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    
    # Load model
    model = load_model(model_path)
    
    # Make prediction with visualization
    result = predict(model, image_path, threshold, visualize=True)
