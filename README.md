# Semantic Evaluation for Text-to-SQL with Test Suites

This repo contains test suite evaluation metric for 11 text-to-SQL tasks. Compared to other current metrics, test suite calculates a tighter upper-bound for semantic accuracy efficiently. It is proposed in our EMNLP 2020 paper: [Semantic Evaluation for Text-to-SQL with Distilled Test Suites](https://arxiv.org/abs/2010.02840). It is now the official metric of [Spider](https://yale-lily.github.io/spider), [SParC](https://yale-lily.github.io/sparc), and [CoSQL](https://yale-lily.github.io/cosql), and is also now available for Academic, ATIS, Advising, Geography, IMDB, Restaurants, Scholar, and Yelp (building on the amazing work by [Catherine and Jonathan](https://github.com/jkkummerfeld/text2sql-data)).

Notice: Please refer to [Ruiqi's repo](https://github.com/ruiqi-zhong/TestSuiteEval) for the code to generate neighbor queries and random databases as defined in the paper. We look forward to similar evaluations in other semantic parsing domains.


## Setting Up

To run the test suite (execution) evaluation, first download the test suites (databases) for the 11 text-to-SQL tasks from [here](https://drive.google.com/file/d/1IJvpd30D3qP6BZu_1bwUSi7JCyynEOMp/view?usp=sharing), and put them in `database/` directory.

You also need to install sqlparse and nltk to run the evaluation.

```
pip3 install sqlparse
pip3 install nltk
```

## Official Evaluation for Spider, SParC, and CoSQL

We will report the test suite accuracy for the official [Spider](https://yale-lily.github.io/spider), [SParC](https://yale-lily.github.io/sparc), and [CoSQL](https://yale-lily.github.io/cosql) leaderboards (starting Oct. 2020). The original exact set match accuracy will be reported as a reference. 

Below is the example command to calculate the test suite accuracy for development sets of Spider, CoSQL and SParC.

```
python3 evaluation.py --gold [gold file] --pred [predicted file] --etype [evaluation type] --db [database dir] --table [table file] --plug_value --keep_distinct --progress_bar_for_each_datapoint


arguments:
     [gold file]       gold file where each line is `a gold SQL \t db_id` for Spider, SParC, and CoSQL, and interactions are seperated by one empty line for SParC and CoSQL. See an example at evaluation_examples/gold.txt
    [predicted file]   predicted sql file where each line is a predicted SQL, and interactions are seperated by one empty line. See an example at evaluation_examples/predict.txt
    [database dir]     the directory that contains all the databases and test suites
    [table file]       table.json file which includes foreign key info of each database.
    [evaluation type]  "exec" for test suite accuracy (default), "match" for the original exact set match accuracy, and "all" for both
    --plug_value       whether to plug in the gold value into the predicted query; suitable if your model does not predict values.
    --keep_distinct    whether to keep distinct keyword during evaluation. default is false.
    --progress_bar_for_each_datapoint   whether to print progress bar of running test inputs for each datapoint
```

#### Test Suite Execution Accuracy without Values
If your system does NOT predict values in the SQL queries, you should add the `--plug value` flag, which will extract the values used in the gold query and plug them into the predicted query.
```
python3 evaluation.py 
    --gold [gold file] 
    --pred [predicted file] 
    --db [database dir]
    --etype exec 
    --plug_value 
```
To also compute the original set match accuracy:
```
python3 evaluation.py 
    --gold [gold file] 
    --pred [predicted file] 
    --db [database dir]
    --table [table file]
    --etype all 
    --plug_value 
```

#### Test Suite Execution Accuracy with Values
We encourage people to report performances with value predictions and do not include `--plug value` argument.
```
python3 evaluation.py 
    --gold [gold file] 
    --pred [predicted file] 
    --db [database dir]
    --etype exec 
```

#### Other Agruments
If `--keep_distinct` is included, the distinct keywords will NOT be removed during evaluation. To make a fair comparison with the original exact set match metric, `--keep_distinct` should not be added.

Include `--progress_bar_for_each_datapoint` if you suspect that the execution got stuck on a specific test input; it will print the progress of running on each test input.


## Evaluation for Other Classical Text-to-SQL Datasets

**NOTE** Thanks to @rizar we identified several issues with the current release. Please use it only for the purpose of preliminary exploration.

The prior work on classical text-to-sql datasets (ATIS, Academic, Advising, Geography, IMDB, Restaurants, Scholar, Yelp) usually reports the exact string match accuracy and execution accuracy over a single database content, which either exaggerates or deflates the real semantic accuracy.

The test set for classical text-to-sql datasets are adopted from [this repo](https://github.com/jkkummerfeld/text2sql-data). We used all the test splits if the test split is defined, and the entire dataset otherwise. We also rewrite the SQLs to conform with the style in the Spider dataset. 

All the test datapoints are saved in `classical_test.pkl`. Each test datapoint is represented as a dictonary have the following keys and values:

- `db_id`: which one of the eight original classical datasets does it belong to. database/[db_id]/[db_id].sqlite contains an empty database with the associated schema.
- `query`: the ground truth SQL query (or any semantically equivalent variant) the model needs to predict.
- `variables`: the constants that are used in the SQL query. We also include a field called `ancestor_of_occuring_column`, where we find out all the column that contains this value and recursively find its `ancestor column` (if a column refers to a parent column/has a foreign key reference). This field is especially useful if your algorithm originally uses database content to help generate model predictions.
- `testsuite`: a set of database paths on which we will compare denotation on
- `texts`: the associated natural language descriptions, with the constant value extracted.

You can evaluate your model in whatever configurations you want. For example, you may choose to plug in the values into the text and ask the model itself to figure out which constants the user has given; 
or you can relax the modelling assumption and assume the model has oracle access to the ground truth constant value; or you can further relax the assumption of knowing which "ancestor column" contains the constant provided.
However, in any case, you **SHOULD NOT** change the gold query, since test suite generation is dependent on it.

The `judge` function in evaluate_classical.py contains what you need to evaluate a single model prediction. 
It takes in the ground truth information of a datapoint (an element in `classical_test.pkl`, represented as a dictionary) and a model prediction (as  a string) and returns True/False - whether the prediction is semantically correct.

Suppose you have made a model prediction for every datapoint and write it into a `.txt` file (one prediction per line), you can use the following example command to calculate the accuracy:

```
python3 evaluate_classical.py --gold [gold file] --pred [predicted file] --out_file [output file] --num_processes [process number]

arguments:
    [gold file]        path to gold file: classical_test.pkl
    [predicted file]   the path to the predicted file. See an example evaluation_examples/classical_test_gold.txt 
    [output file]      the output file path. e.g. goldclassicaltest.pkl
    [process number]   number of processes to use
```


## Citation

```
@InProceedings{ruiqi20,
  author =  {Ruiqi Zhong and Tao Yu and Dan Klein},
  title =   {Semantic Evaluation for Text-to-SQL with Distilled Test Suite},
  year =    {2020},
  booktitle =   {The 2020 Conference on Empirical Methods in Natural Language Processing},
  publisher = {Association for Computational Linguistics},
}
```

