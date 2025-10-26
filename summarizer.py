import json
import os
from attribute_interpreter_v2 import group_attributes, create_natural_summary, get_skincare_recommendations, get_grooming_recommendations

def convert_model_output_to_binary(model_output):
    """
    Convert model output with probability/predicted format to simple binary format
    for the attribute interpreter.
    """
    binary_output = {}
    for attr, data in model_output.items():
        if isinstance(data, dict) and "predicted" in data:
            binary_output[attr] = 1 if data["predicted"] else 0
        else:
            binary_output[attr] = data
    return binary_output

def generate_summary(model_output):
    """
    Generate a natural language summary from model predictions.
    
    Args:
        model_output (dict): Model predictions with probability/predicted format
        
    Returns:
        dict: Contains summary, grouped results, and recommendations
    """
    try:
        # Convert to binary format for the interpreter
        binary_output = convert_model_output_to_binary(model_output)
        
        # Group attributes for better organization
        grouped_results = group_attributes(binary_output)
        
        # Create natural summary
        summary = create_natural_summary(grouped_results, binary_output, {})
        
        # Extract specific recommendations
        skincare_tips = get_skincare_recommendations(binary_output)
        grooming_tips = get_grooming_recommendations(binary_output)
        
        return {
            "summary": summary,
            "grouped_attributes": grouped_results,
            "skincare_recommendations": skincare_tips,
            "grooming_recommendations": grooming_tips,
            "raw_predictions": model_output
        }
        
    except Exception as e:
        return {
            "summary": f"Error generating summary: {str(e)}",
            "grouped_attributes": {},
            "skincare_recommendations": [],
            "grooming_recommendations": [],
            "raw_predictions": model_output
        }

def save_analysis_to_file(analysis_data, filename="analysis_output.json"):
    """
    Save analysis results to a JSON file.
    
    Args:
        analysis_data (dict): Complete analysis results
        filename (str): Output filename
        
    Returns:
        str: Path to saved file
    """
    try:
        output_path = os.path.join(os.path.dirname(__file__), filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        return output_path
    except Exception as e:
        print(f"Error saving analysis: {str(e)}")
        return None
