import json
import argparse
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def group_attributes(model_output):
    """Group related attributes together for better summary generation."""
    groups = {
        'image_quality': ['image_id', 'blurry_image'],
        'facial_features': ['attractive', 'sharp_jawline', 'high_cheekbones', 'big_eyes', 'big_lips', 'sharp_nose', 'double chin'],
        'skin_condition': ['clear_skin', 'dark_circles', 'oily_skin'],
        'hair_features': ['bald', 'receeding_hairline', 'long_hair', 'curly_hair', 'grey_hair', 'black_hair'],
        'facial_hair': ['has_beard', 'patchy_beard', 'has_mustache'],
        'grooming': ['well_groomed', 'has_makeup', 'wearing_glasses', 'wearing_hat', 'thick_eyebrow'],
        'expression': ['smiling', 'mouth_open'],
        'demographics': ['adult', 'old', 'male', 'veil']
    }
    
    grouped_results = {}
    for group_name, attrs in groups.items():
        group_values = {attr: model_output.get(attr) for attr in attrs if attr in model_output}
        if group_values:
            grouped_results[group_name] = group_values
    return grouped_results

def get_skincare_recommendations(skin_attributes):
    """Generate specific skincare recommendations based on skin conditions."""
    recommendations = []
    
    if skin_attributes.get('oily_skin') == 1:
        recommendations.extend([
            "Use a gentle, oil-free cleanser twice daily",
            "Apply a non-comedogenic moisturizer",
            "Consider products with salicylic acid or niacinamide",
            "Use clay masks weekly to control excess oil"
        ])
    
    if skin_attributes.get('clear_skin') == 0:
        recommendations.extend([
            "Establish a consistent cleansing routine",
            "Use products with soothing ingredients like aloe vera",
            "Consider adding vitamin C serum for skin clarity"
        ])
    
    if skin_attributes.get('dark_circles') == 1:
        recommendations.extend([
            "Apply eye cream with caffeine and vitamin K",
            "Ensure adequate sleep and hydration",
            "Consider using a color corrector under eyes"
        ])
    
    return recommendations

def get_grooming_recommendations(attributes):
    """Generate specific grooming recommendations based on features."""
    recommendations = []
    
    if attributes.get('receeding_hairline') == 1:
        recommendations.extend([
            "Use anti-hair loss shampoo with biotin",
            "Consider minoxidil treatment after consulting a specialist",
            "Massage scalp regularly to stimulate blood flow"
        ])
    
    if attributes.get('curly_hair') == 1:
        recommendations.extend([
            "Use sulfate-free shampoo for curly hair",
            "Apply leave-in conditioner to maintain moisture",
            "Style with curl-defining cream for better definition"
        ])
    
    if attributes.get('has_beard') == 1:
        recommendations.extend([
            "Apply beard oil daily for softness and shine",
            "Trim beard regularly to maintain shape",
            "Use a specialized beard cleanser"
        ])
    
    return recommendations

def create_natural_summary(grouped_results, model_output, mapping):
    """Create a natural, human-like summary with specific recommendations."""
    parts = []
    
    # Facial Analysis
    facial_features = []
    if model_output.get('attractive') == 1:
        facial_features.append("attractive facial features")
    if model_output.get('sharp_jawline') == 1:
        facial_features.append("defined jawline")
    if model_output.get('high_cheekbones') == 1:
        facial_features.append("high cheekbones")
    
    if facial_features:
        parts.append("Facial Analysis:")
        parts.append(f"You have {', '.join(facial_features[:-1]) + ' and ' + facial_features[-1] if len(facial_features) > 1 else facial_features[0]}.")
    
    # Skin Analysis & Care
    skin_conditions = []
    if grouped_results.get('skin_condition'):
        if model_output.get('clear_skin') == 1:
            skin_conditions.append("clear complexion")
        if model_output.get('oily_skin') == 1:
            skin_conditions.append("oily skin tendencies")
        if model_output.get('dark_circles') == 1:
            skin_conditions.append("noticeable dark circles")
        
        if skin_conditions:
            parts.append("\nSkin Analysis:")
            parts.append(f"Your skin shows {', '.join(skin_conditions)}.")
            
            # Add skincare recommendations
            skincare_tips = get_skincare_recommendations(model_output)
            if skincare_tips:
                parts.append("\nSkincare Recommendations:")
                parts.extend([f"• {tip}" for tip in skincare_tips])
    
    # Grooming Analysis & Recommendations
    grooming_tips = get_grooming_recommendations(model_output)
    if grooming_tips:
        parts.append("\nGrooming Recommendations:")
        parts.extend([f"• {tip}" for tip in grooming_tips])
    
    # Additional Tips
    additional_tips = []
    if model_output.get('male') == 1:
        additional_tips.extend([
            "Use skincare products specifically formulated for men's skin",
            "Consider a men's facial moisturizer with SPF for daily protection",
            "Look for products targeting specific male skin concerns"
        ])
    
    if additional_tips:
        parts.append("\nAdditional Tips:")
        parts.extend([f"• {tip}" for tip in additional_tips])
    
    # Maintenance Advice
    if model_output.get('well_groomed') == 1:
        parts.append("\nMaintenance:")
        parts.append("You're already maintaining good grooming habits. Continue your current routine while incorporating these recommendations for even better results!")
    else:
        parts.append("\nGetting Started:")
        parts.append("Start implementing these recommendations gradually. Begin with the basic skincare routine and add more steps as you become comfortable.")
    
    return "\n".join(parts)

def generate_sentences(model_output, mapping):
    sentences = []
    details = {}
    for attr, value in model_output.items():
        value_str = str(int(round(value)))
        if attr in mapping and value_str in mapping[attr]:
            sentence = mapping[attr][value_str]
        else:
            sentence = f"For {attr}, value is {value}."
        sentences.append(sentence)
        details[attr] = {"value": value, "sentence": sentence}
    return sentences, details

def main():
    parser = argparse.ArgumentParser(description="Attribute Interpreter")
    parser.add_argument('--predictions', required=True, help='Path to predictions JSON file')
    parser.add_argument('--mapping', required=True, help='Path to attribute mapping JSON file')
    parser.add_argument('--out', required=True, help='Path to output JSON file')
    args = parser.parse_args()

    model_output = load_json(args.predictions)
    mapping = load_json(args.mapping)
    grouped_results = group_attributes(model_output)
    sentences, details = generate_sentences(model_output, mapping)
    summary = create_natural_summary(grouped_results, model_output, mapping)
    result = {
        "summary": summary,
        "sentences": sentences,
        "details": details
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Output written to {args.out}")

if __name__ == "__main__":
    main()