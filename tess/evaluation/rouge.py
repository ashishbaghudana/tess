from pythonrouge.pythonrouge import Pythonrouge
from rouge import Rouge


def rouge_para(predicted_summary, golden_summary):

    # initialize setting of ROUGE, eval ROUGE-1, 2, SU4
    # if summary_file_exis=True, you should specify predict summary(peer_path) and golden summary(model_path) paths
    rouge = Rouge()
    rouge_scores = rouge.get_scores(predicted_summary, golden_summary)
    score = {
        'ROUGE-1': rouge_scores[0]['rouge-1']['f'],
        'ROUGE-2': rouge_scores[0]['rouge-2']['f'],
        'ROUGE-L': rouge_scores[0]['rouge-l']['f']
    }
    return score


def rouge_sent(predict_summary, golden_summary):

    import spacy
    nlp = spacy.load('en_core_web_sm')
    predict_summary = predict_summary.replace('\n', ' ')
    golden_summary = golden_summary.replace('\n', ' ')

    doc = nlp(predict_summary)
    predict_sent_list = [sent.text for sent in doc.sents]

    doc = nlp(golden_summary)
    golden_sent_list = [sent.text for sent in doc.sents]

    max_rouge_1 = -99999
    max_rouge_2 = -99999

    for p_idx, predict_sent in enumerate(predict_sent_list):
        for g_idx, golden_sent in enumerate(golden_sent_list):

            # initialize setting of ROUGE to eval ROUGE-1, 2, SU4
            # if you evaluate ROUGE by sentence list as above, set summary_file_exist=False
            # if recall_only=True, you can get recall scores of ROUGE
            rouge = Pythonrouge(summary_file_exist=False,
                                summary=[[predict_sent]], reference=[[[golden_sent]]],
                                n_gram=2, ROUGE_SU4=True, ROUGE_L=True,
                                recall_only=True, stemming=True, stopwords=True,
                                word_level=True, length_limit=True, length=50,
                                use_cf=False, cf=95, scoring_formula='average',
                                resampling=True, samples=1000, favor=True, p=0.5)
            score = rouge.calc_score()

            if score['ROUGE-1'] > max_rouge_1:
                max_rouge_1 = score['ROUGE-1']

            if score['ROUGE-2'] > max_rouge_2:
                max_rouge_2 = score['ROUGE-2']

    return {"ROUGE-1": max_rouge_1, "ROUGE-2": max_rouge_2}
