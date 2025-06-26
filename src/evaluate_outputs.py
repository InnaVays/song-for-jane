from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util
import torch


# Evaluate Similarity
def compute_embedding_similarity(text1, text2, model_name='all-MiniLM-L6-v2'):
    embed_model = SentenceTransformer(model_name)
    embeddings = embed_model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    
    return round(similarity, 4)


def evaluate_text_metrics(prompt: str, output: str , with_sm: bool = False):
    # BLEU
    bleu = sentence_bleu([prompt.split()], output.split())

    # ROUGE
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    rouge = scorer.score(prompt, output)

    # METEOR
    meteor = meteor_score([prompt], output)

    # SIMILARITY
    if with_sm:
        similarity = compute_embedding_similarity(prompt, output) 
    else: 
        similarity = 0
    return {
        "BLEU": round(bleu, 4),
        "ROUGE-1": round(rouge['rouge1'].fmeasure, 4),
        "ROUGE-L": round(rouge['rougeL'].fmeasure, 4),
        "METEOR": round(meteor, 4),
        "SIMILARITY": round(similarity, 4),
    }


# Example
if __name__ == "__main__":
    reference = "My home is quiet and the rain is singing"
    generated = "The rain sings softly in my quiet home"
    results = evaluate_text_metrics(reference, generated)
    print(results)
