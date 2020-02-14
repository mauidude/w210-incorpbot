import logging

import torch
from torch.utils.data import DataLoader, SequentialSampler
from transformers import (AlbertConfig, AlbertForQuestionAnswering,
                          AlbertTokenizer, BertConfig,
                          BertForQuestionAnswering, BertTokenizer,
                          DistilBertConfig, DistilBertForQuestionAnswering,
                          DistilBertTokenizer, XLMConfig,
                          XLMForQuestionAnswering, XLMTokenizer, XLNetConfig,
                          XLNetForQuestionAnswering, XLNetTokenizer,
                          squad_convert_examples_to_features)
from transformers.data.metrics.squad_metrics import (
    compute_predictions_log_probs, compute_predictions_logits, get_final_text)
from transformers.data.processors.squad import SquadExample, SquadResult

logger = logging.getLogger('qa')

MODEL_CLASSES = {
    "bert": (BertConfig, BertForQuestionAnswering, BertTokenizer),
    # "roberta": (RobertaConfig, RobertaForQuestionAnswering, RobertaTokenizer),
    # "xlnet": (XLNetConfig, XLNetForQuestionAnswering, XLNetTokenizer),
    # "xlm": (XLMConfig, XLMForQuestionAnswering, XLMTokenizer),
    # "distilbert": (DistilBertConfig, DistilBertForQuestionAnswering, DistilBertTokenizer),
    "albert": (AlbertConfig, AlbertForQuestionAnswering, AlbertTokenizer),
}


class Model(object):
    def __init__(self, model_name_or_path, nlp, model_type='bert', cache_dir=None, do_lower_case=True, max_seq_length=384, doc_stride=128,
                 max_query_length=64, version_2_with_negative=False, null_score_diff_threshold=0, verbose=True):
        config_class, model_class, tokenizer_class = MODEL_CLASSES[model_type]

        self.config = config_class.from_pretrained(
            model_name_or_path,
            cache_dir=cache_dir if cache_dir else None,
        )

        self.tokenizer = tokenizer_class.from_pretrained(
            model_name_or_path,
            do_lower_case=do_lower_case,
            cache_dir=cache_dir if cache_dir else None,
        )

        self.model = model_class.from_pretrained(
            model_name_or_path,
            from_tf=bool(".ckpt" in model_name_or_path),
            config=self.config,
            cache_dir=cache_dir if cache_dir else None,
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.max_seq_length = max_seq_length
        self.doc_stride = doc_stride
        self.max_query_length = max_query_length
        self.do_lower_case = do_lower_case
        self.nlp = nlp
        self.model_type = model_type
        self.verbose = verbose
        self.version_2_with_negative = version_2_with_negative
        self.null_score_diff_threshold = null_score_diff_threshold

    def find_answer(self, question, context, n_best_size=20, max_answer_length=30, full_sentence=False):
        # heavily inspired by "https://github.com/huggingface/transformers/blob/v2.3.0/examples/run_squad.py#L212-L317"
        example_id = '55555'
        example = SquadExample(example_id,
                               question,
                               context,
                               None,
                               None,
                               None)

        features, dataset = squad_convert_examples_to_features(
            [example],
            self.tokenizer,
            self.max_seq_length,
            self.doc_stride,
            self.max_query_length,
            False,
            return_dataset='pt')

        sampler = SequentialSampler(dataset)
        dataloader = DataLoader(dataset, sampler=sampler, batch_size=1)

        all_results = []
        for batch in dataloader:
            self.model.eval()
            batch = tuple(t.to(self.device) for t in batch)

            with torch.no_grad():
                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                }

                if self.model_type in {"xlm", "roberta", "distilbert"}:
                    del inputs["token_type_ids"]

                example_index = batch[3]

                # XLNet and XLM use more arguments for their predictions
                if self.model_type in {"xlnet", "xlm"}:
                    inputs.update({"cls_index": batch[4], "p_mask": batch[5]})

                outputs = self.model(**inputs)
                output = [o.detach().cpu().tolist() for o in outputs]

                unique_id = int(features[example_index].unique_id)

                # Some models (XLNet, XLM) use 5 arguments for their predictions, while the other "simpler"
                # models only use two.
                if len(output) >= 5:
                    start_logits = output[0]
                    start_top_index = output[1]
                    end_logits = output[2]
                    end_top_index = output[3]
                    cls_logits = output[4]

                    squad_result = SquadResult(
                        unique_id,
                        start_logits[0],
                        end_logits[0],
                        start_top_index=start_top_index[0],
                        end_top_index=end_top_index[0],
                        cls_logits=cls_logits[0],
                    )

                else:
                    start_logits, end_logits = output
                    squad_result = SquadResult(
                        unique_id, start_logits[0], end_logits[0])

                all_results.append(squad_result)

        # XLNet and XLM use a more complex post-processing procedure
        if self.model_type in {"xlnet", "xlm"}:
            if hasattr(model, "config"):
                start_n_top = self.model.config.start_n_top
                end_n_top = self.model.config.end_n_top
            else:
                start_n_top = self.model.module.config.start_n_top
                end_n_top = self.model.module.config.end_n_top

            predictions = compute_predictions_log_probs(
                [example],
                features,
                all_results,
                n_best_size,
                max_answer_length,
                '/tmp/pred.out',
                '/tmp/nbest.out',
                '/tmp/null.out',
                start_n_top,
                end_n_top,
                self.version_2_with_negative,
                tokenizer,
                self.verbose,
            )
        else:
            predictions = compute_predictions_logits(
                [example],
                features,
                all_results,
                n_best_size,
                max_answer_length,
                self.do_lower_case,
                '/tmp/pred.out',
                '/tmp/nbest.out',
                '/tmp/null.out',
                self.verbose,
                self.version_2_with_negative,
                self.null_score_diff_threshold,
            )

        prediction = predictions[example_id]

        logger.debug(f'found prediction: "{prediction}"')

        # empty prediction indicates unknown answer
        if not prediction:
            logger.debug('empty prediction')
            return None

        if full_sentence:
            doc = self.nlp(context)
            for sent in doc.sents:
                if prediction in sent.text:
                    prediction = sent.text
                    break

        return prediction
