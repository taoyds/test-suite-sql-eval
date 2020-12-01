import argparse
from typing import List, Dict, Any, Tuple
import pickle as pkl
import tqdm
from exec_eval import exec_on_db, result_eq
import os
from collections import defaultdict
import time
from multiprocessing import cpu_count, Pool

NUM_PROCESSES = cpu_count() // 3
if NUM_PROCESSES == 0:
    NUM_PROCESSES = 1
MULTIPLICATIVE_OVERHEAD = 3
ADDITIVE_OVERHEAD = 30
GOLD_TIMEOUT = 100


def load_predictions(f_path: str) -> List[str]:
    preds = []
    with open(f_path, 'r') as in_file:
        for l in in_file:
            preds.append(l.strip())
    return preds


def acc(l, idxes=None):
    if idxes is None:
        idxes = [_ for _ in range(len(l))]
    c = 0
    for idx in idxes:
        if l[idx]:
            c += 1
    return float(c) / len(idxes)


# the input is a tuple of gold_dict and model prediction
# and teh output is whether the model prediction passes the entire test suite
def judge(args: Tuple[Dict[str, Any], str]) -> bool:
    gold_dict, pred = args

    testsuite_paths = gold_dict['testsuite']
    gold_query = gold_dict['query']
    order_matters = 'order by' in gold_query.lower()

    pass_all_testcase = True
    for testcase_path in testsuite_paths:

        start = time.time()
        flg, gold_result = exec_on_db(testcase_path, gold_query, timeout=GOLD_TIMEOUT)
        duration = time.time() - start
        timeout = ADDITIVE_OVERHEAD + MULTIPLICATIVE_OVERHEAD * duration

        if flg != 'result':
            print('Warning: executing gold query results in an exception')
            continue
        flg, pred_result = exec_on_db(testcase_path, pred, timeout=int(timeout))
        if flg != 'result':
            pass_all_testcase = False
            break
        if not result_eq(gold_result, pred_result, order_matters):
            pass_all_testcase = False
            break
    return pass_all_testcase


def main(preds: List[str], gold_file: str = "classical_test.pkl", verbose: bool = True, num_processes: int = NUM_PROCESSES) -> List[bool]:
    gold_dicts = pkl.load(open(gold_file, 'rb'))
    assert len(gold_dicts) == len(preds), 'number of gold and prediction should be equal'
    group_name2idxes = defaultdict(list)

    for idx, gold_dict in enumerate(gold_dicts):
        group_name2idxes[gold_dict['db_id']].append(idx)

    with Pool(num_processes) as pool:
        result = list(tqdm.tqdm(pool.imap(judge, zip(gold_dicts, preds)), total=len(gold_dicts)))

    if verbose:
        print('overall accuracy: ', acc(result))
        for group, idxes in group_name2idxes.items():
            print('accuracy for ', group, acc(result, idxes))
    return result


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold', dest='gold', type=str, help="the path to the predicted queries")
    parser.add_argument('--pred', dest='pred', type=str, help="the path to the predicted queries")
    parser.add_argument('--out_file', type=str, required=True, help='the output file path')
    parser.add_argument('--num_processes', default=NUM_PROCESSES, help='number of processes to use')
    args = parser.parse_args()

    preds = load_predictions(args.pred)
    assert not os.path.exists(args.out_file), 'output file path %s already exists' % args.out_file

    result = main(preds=preds, gold_file=args.gold, verbose=True, num_processes=args.num_processes)
    pkl.dump(result, open(args.out_file, 'wb'))
    print('total time used: ', time.time() - start)
