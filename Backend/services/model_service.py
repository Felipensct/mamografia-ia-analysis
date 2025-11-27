"""
Service for trained breast cancer detection model predictions
"""

import os
import numpy as np
import cv2
from tensorflow import keras
import tensorflow as tf
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import json
import gc
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configurar TensorFlow para uso eficiente de memória
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduzir logs

# Configurar GPU para crescimento dinâmico de memória
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"✅ GPU configurada para crescimento dinâmico de memória: {len(gpus)} GPU(s)")
    except RuntimeError as e:
        print(f"⚠️ Erro ao configurar GPU: {e}")

# Limitar uso de threads para reduzir overhead de CPU
tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(2)

class ModelService:
    def __init__(self, model_path: str = None):
        """
        Initialize the model service with lazy loading
        
        Args:
            model_path: Path to the trained model file. If None, uses default path.
        """
        self.model = None
        self.model_path = model_path or os.path.join(
            Path(__file__).parent.parent, 
            "best_cbis_ddsm_model.keras"
        )
        # NÃO carregar o modelo no __init__ - usar lazy loading
        print(f"📋 ModelService inicializado. Modelo será carregado sob demanda.")
    
    def _load_model(self):
        """Load the trained model (lazy loading)"""
        if self.model is not None:
            return  # Já está carregado
            
        try:
            if os.path.exists(self.model_path):
                print(f"🤖 Carregando modelo treinado de {self.model_path}...")
                self.model = keras.models.load_model(self.model_path, compile=False)
                print("✅ Modelo carregado com sucesso!")
            else:
                print(f"⚠️ Arquivo do modelo não encontrado em {self.model_path}")
                self.model = None
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {str(e)}")
            self.model = None
    
    def _unload_model(self):
        """Unload the model and free memory"""
        if self.model is not None:
            print("🧹 Liberando memória do modelo...")
            del self.model
            self.model = None
            
            # Limpar cache do TensorFlow/Keras
            keras.backend.clear_session()
            
            # Forçar garbage collection
            gc.collect()
            
            print("✅ Memória liberada")
    
    def is_available(self) -> bool:
        """Check if model file exists and can be loaded"""
        return os.path.exists(self.model_path)
    
    def preprocess_image(self, image_path: str, img_size=(224, 224)) -> np.ndarray:
        """
        Load and preprocess an image for prediction
        
        Args:
            image_path: Path to the image file
            img_size: Target size for the image
            
        Returns:
            Preprocessed image array ready for prediction
        """
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create a mask to find the breast tissue (non-black regions)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Threshold to find non-black regions (breast tissue)
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
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
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
    
    def assess_risk_level(self, probability: float) -> tuple:
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
    
    def get_birads_category(self, probability: float) -> str:
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
    
    def get_recommendation(self, probability: float) -> str:
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
    
    def generate_diagnostic_report(self, prediction: str, probability: float, confidence: float) -> Dict[str, Any]:
        """Generate detailed diagnostic information"""
        risk_level, assessment = self.assess_risk_level(probability)
        
        report = {
            'primary_diagnosis': prediction,
            'malignancy_probability': f"{probability:.1%}",
            'benign_probability': f"{(1-probability):.1%}",
            'confidence': f"{confidence:.1%}",
            'risk_level': risk_level,
            'clinical_assessment': assessment,
            'birads_equivalent': self.get_birads_category(probability),
            'recommendation': self.get_recommendation(probability)
        }
        
        return report
    
    def get_gradcam_heatmap(self, img_array: np.ndarray, last_conv_layer_name: str = None) -> Optional[np.ndarray]:
        """
        Generate Grad-CAM heatmap to show which regions the model focuses on
        
        Args:
            img_array: Preprocessed image array (with batch dimension)
            last_conv_layer_name: Name of the last convolutional layer
            
        Returns:
            Heatmap array or None if generation fails
        """
        try:
            # Find the base model (EfficientNet or ResNet)
            base_model = None
            for layer in self.model.layers:
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
            for layer in self.model.layers[2:]:  # Skip input and base model layers
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
    
    def find_roi_bbox(self, heatmap: np.ndarray, threshold: float = 0.5) -> Optional[Tuple[int, int, int, int]]:
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
    
    def generate_visualization(self, image_path: str, heatmap: Optional[np.ndarray], 
                              bbox: Optional[Tuple[int, int, int, int]], 
                              diagnostic_report: Dict[str, Any], 
                              output_dir: str = None, target_size: Tuple[int, int] = (224, 224)) -> Optional[str]:
        """
        Generate visualization image with Grad-CAM heatmap and diagnosis overlay
        
        Args:
            image_path: Path to original image
            heatmap: Grad-CAM heatmap array (already resized to target_size)
            bbox: Bounding box coordinates (x, y, w, h)
            diagnostic_report: Diagnostic report dictionary
            output_dir: Directory to save the visualization
            target_size: Size of the displayed images
            
        Returns:
            Path to the generated visualization image, or None if failed
        """
        try:
            # Read and preprocess original image for display
            img = cv2.imread(image_path)
            if img is None:
                return None
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img, target_size)
            
            # Create figure with 3 subplots
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            # Original image
            axes[0].imshow(img_resized)
            axes[0].set_title('Original Image', fontsize=14, fontweight='bold')
            axes[0].axis('off')
            
            # Heatmap overlay
            axes[1].imshow(img_resized)
            if heatmap is not None:
                # The 'heatmap' passed in is already resized, so no need to resize again
                axes[1].imshow(heatmap, cmap='jet', alpha=0.5)
            axes[1].set_title('Attention Map (Grad-CAM)', fontsize=14, fontweight='bold')
            axes[1].axis('off')
            
            # Image with red square
            axes[2].imshow(img_resized)
            if bbox is not None:
                x, y, w, h = bbox
                
                # The bbox coordinates are now correctly scaled to the target_size (e.g., 224x224)
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
            
            # Determine output path
            if output_dir is None:
                output_dir = os.path.dirname(image_path)
            
            base_name = os.path.basename(image_path)
            output_filename = base_name.replace('.jpg', '_diagnosis.jpg').replace('.png', '_diagnosis.png')
            if not (output_filename.endswith('.jpg') or output_filename.endswith('.png')):
                output_filename = output_filename + '_diagnosis.jpg'
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Save figure
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"📊 Visualization saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"⚠️ Error generating visualization: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict(self, image_path: str, threshold: float = 0.5, generate_viz: bool = True) -> Dict[str, Any]:
        """
        Make prediction on a single image with detailed diagnosis
        
        Args:
            image_path: Path to the image file
            threshold: Threshold for binary classification (default: 0.5)
            generate_viz: Whether to generate visualization image (default: True)
            
        Returns:
            Dictionary containing prediction results and diagnostic report
        """
        if not self.is_available():
            raise RuntimeError("Modelo não está disponível")
        
        try:
            # Carregar modelo sob demanda (lazy loading)
            self._load_model()
            
            if self.model is None:
                raise RuntimeError("Falha ao carregar o modelo")
            
            # Define target size
            img_size = (224, 224)
            
            # Preprocess image
            img = self.preprocess_image(image_path, img_size)
            
            # Make prediction
            print("Fazendo predição...")
            prediction_proba = float(self.model.predict(img, verbose=0)[0][0])
            
            # Convert to binary prediction
            prediction = "MALIGNANT" if prediction_proba > threshold else "BENIGN"
            confidence = prediction_proba if prediction_proba > threshold else (1 - prediction_proba)
            
            # Generate Grad-CAM heatmap
            print("Generating attention map...")
            heatmap_small = self.get_gradcam_heatmap(img)  # This is the small (e.g., 7x7) heatmap
            
            bbox = None
            heatmap_resized = None  # This will be our full 224x224 heatmap
            
            if heatmap_small is not None:
                # Resize the small heatmap to match the input image size
                heatmap_resized = cv2.resize(heatmap_small, img_size, interpolation=cv2.INTER_LINEAR)
                
                # Now, find the bounding box on the *full-size* resized heatmap
                bbox = self.find_roi_bbox(heatmap_resized, threshold=0.5)
            
            # If no bbox detected but malignancy probability is above 20%, mark center region
            if bbox is None and prediction_proba >= 0.2:
                # Create a default bounding box in the center of the image
                center_val = img_size[0] // 4
                size_val = img_size[0] // 2
                bbox = (center_val, center_val, size_val, size_val)  # e.g., (56, 56, 112, 112)
                print("Note: Using center region as default suspicious area")
            
            # Generate diagnostic report
            diagnostic_report = self.generate_diagnostic_report(prediction, prediction_proba, confidence)
            
            # Generate visualization if requested
            viz_path = None
            viz_filename = None
            if generate_viz:
                print("Creating visualization...")
                # Pass the *resized* heatmap to the visualizer
                viz_path = self.generate_visualization(image_path, heatmap_resized, bbox, 
                                                      diagnostic_report, target_size=img_size)
                if viz_path:
                    viz_filename = os.path.basename(viz_path)
            
            # Build result
            result = {
                'success': True,
                'model': 'EfficientNetV2 (Trained on CBIS-DDSM)',
                'prediction': prediction,
                'confidence': confidence,
                'probability': prediction_proba,
                'diagnostic_report': diagnostic_report,
                'analysis': self._format_analysis_text(diagnostic_report, prediction_proba),
                'visualization_path': viz_path,
                'visualization_filename': viz_filename
            }
            
            print(f"✅ Predição concluída: {prediction} ({prediction_proba:.1%})")
            
            # Liberar memória do modelo após uso
            self._unload_model()
            
            return result
            
        except Exception as e:
            print(f"❌ Erro na predição: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Liberar memória mesmo em caso de erro
            self._unload_model()
            
            return {
                'success': False,
                'error': str(e),
                'model': 'EfficientNetV2 (Trained on CBIS-DDSM)'
            }
        finally:
            # Garantir limpeza de memória
            if img is not None:
                del img
            if heatmap_small is not None:
                del heatmap_small
            if heatmap_resized is not None:
                del heatmap_resized
            gc.collect()
    
    def _format_analysis_text(self, report: Dict[str, Any], probability: float) -> str:
        """Format diagnostic report as readable text"""
        
        text = f"""

## Diagnóstico Primário: {report['primary_diagnosis']}

### Probabilidades
- **Malignidade:** {report['malignancy_probability']}
- **Benigno:** {report['benign_probability']}
- **Confiança:** {report['confidence']}

### Avaliação de Risco
**Nível de Risco:** {report['risk_level']}

**Avaliação Clínica:** {report['clinical_assessment']}

### Classificação BI-RADS Equivalente
{report['birads_equivalent']}

### Recomendação Clínica
{report['recommendation']}

---

### Observações Importantes
⚠️ **IMPORTANTE:** Esta análise é fornecida por um modelo de inteligência artificial treinado e deve ser utilizada apenas como ferramenta de suporte à decisão clínica. 

**NÃO substitui o diagnóstico de um profissional médico qualificado.**

A interpretação final deve sempre ser realizada por um radiologista ou médico especializado, considerando:
- Histórico clínico completo do paciente
- Exames anteriores e comparações
- Contexto clínico e sintomas
- Outros exames complementares

### Como Usar Este Resultado
1. **Revisão Profissional:** Apresente este resultado a um médico radiologista
2. **Contexto Clínico:** Considere o histórico médico completo
3. **Confirmação:** Em casos suspeitos, realize biopsia conforme recomendação médica
4. **Acompanhamento:** Siga as recomendações de follow-up do profissional

"""
        return text.strip()

# Global instance
_model_service_instance = None

def get_model_service() -> ModelService:
    """Get or create the global model service instance"""
    global _model_service_instance
    if _model_service_instance is None:
        _model_service_instance = ModelService()
    return _model_service_instance
