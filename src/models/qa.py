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
    compute_predictions_logits, get_final_text)
from transformers.data.processors.squad import SquadExample, SquadResult

MODEL_CLASSES = {
    "bert": (BertConfig, BertForQuestionAnswering, BertTokenizer),
    # "roberta": (RobertaConfig, RobertaForQuestionAnswering, RobertaTokenizer),
    # "xlnet": (XLNetConfig, XLNetForQuestionAnswering, XLNetTokenizer),
    # "xlm": (XLMConfig, XLMForQuestionAnswering, XLMTokenizer),
    # "distilbert": (DistilBertConfig, DistilBertForQuestionAnswering, DistilBertTokenizer),
    "albert": (AlbertConfig, AlbertForQuestionAnswering, AlbertTokenizer),
}


class Model(object):
    def __init__(self, model_name_or_path, model_type='bert', cache_dir=None, do_lower_case=True, max_seq_length=384, doc_stride=128, max_query_length=64):
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

    def find_answer(self, question, context, n_best_size=20, max_answer_length=30):
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

                example_index = batch[3]

                outputs = self.model(**inputs)
                outputs = [output.detach().cpu().tolist()
                           for output in outputs]
                start_logits, end_logits = outputs

                unique_id = int(features[example_index].unique_id)

                squad_result = SquadResult(
                    unique_id, start_logits[0], end_logits[0])

                all_results.append(squad_result)

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
            True,
            False,
            0,
        )

        return predictions[example_id]
