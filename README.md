You must run the evaluation in this directory. database/ is the directory that contains all the databases (test suite) for evaluating execution accuracy.
You need to download its content from https://drive.google.com/file/d/1IJvpd30D3qP6BZu_1bwUSi7JCyynEOMp/view?usp=sharing , and the method to generate these databases can be seen at https://arxiv.org/abs/2010.02840.


# Evaluation for SPIDER, CoSQL, SParC

Below is the example command to calculate our new metric for SPIDER, CoSQL and SParC.
Example command: python3 evaluation.py  --gold=evaluation_examples/gold.txt --pred=evaluation_examples/predict.txt --db=database/

You should obtain an average accuracy of 8.1% if your are setting up the directories properly.

Here "gold" argument is the path to the gold sql file and "pred" argument is the path to prediction file.
These two files should be in the same format and have same number of lines/turns, with the only difference that the database name is appended after each line (seperated by tab) in the gold file.

Here are some other arguments of evaluation.py:

```
optional arguments:
  --table TABLE         the tables.json schema file
  --etype {all,exec,match}
                        evaluation type, exec for test suite accuracy, match
                        for the original exact set match accuracy
  --plug_value          whether to plug in the gold value into the predicted
                        query; suitable if your model does not predict values.
  --keep_distinct       whether to keep distinct keyword during evaluation.
                        default is false.
  --progress_bar_for_each_datapoint
                        whether to print progress bar of running test inputs
                        for each datapoint
```

The default argument for "etype" is now "exec". This is different from the original execution evaluation metric, and the details can be seen in the linked paper above.
To evaluate both/the original official metric exact set match, pass in the argment "all"/"match".

If you want to calculate exact set match, you must pass in the tables.json argument.

"plug value" will extract the values used in the gold query and plug them into the predicted query.
We encourage people to report performances with value predictions and do not include this argument; however, if your system do not predict values, you can use this argument to evaluate your system.

If "keep_distinct" is included, the distinct keywords will NOT be removed during evaluation - while in the original exact set match metric, difference in the "distinct" keyword was not considered.

Include "--progress_bar_for_each_datapoint" if you suspect that the execution got stuck on a specific test input; it will print the progress of running on each test input.

For example, consider the following command:
```
python3 evaluation.py  --gold=evaluation_examples/gold.txt --pred=evaluation_examples/predict.txt --db=database/ --keep_distinct --etype=all --table=tables.json --plug_value --progress_bar_for_each_datapoint
```

The evaluation script will calculate both execution and exact set match accuracy, does not remove the distinct keyword, and print the progress bar for each datapoint.

# Evaluation for Classical Text-to-Sql Datasets

The test set for classical text-to-sql datasets (ATIS, Academic, Advising, Geography, IMDB, Restaurants, Scholar, Yelp) are adopted from this repo: https://github.com/jkkummerfeld/text2sql-data ,
We used all the test splits if the test split is defined, and the entire dataset otherwise.
We also rewrite the SQLs to conform with the style in the SPIDER dataset. 

All the test datapoints are saved in classical_test.pkl. 
Each test datapoint is represented as a dictonary have keys and values

- db_id: which one of the eight original classical datasets does it belong to. database/[db_id]/[db_id].sqlite contains an empty database with the associated schema.
- query: the ground truth SQL query (or any semantically equivalent variant) the model needs to predict.
- variables: the constants that are used in the SQL query. 
    We also include a field called "ancestor_of_occuring_column", where we find out all the column that contains this value and recursively find its "ancestor column" (if a column refers to a parent column/has a foreign key reference)
    This field is especially useful if your algorithm originally uses database content to help generate model predictions.
- testsuite: a set of database paths on which we will compare denotation on
- texts: the associated natural language descriptions, with the constant value extracted.

You can evaluate your model in whatever configurations you want. For example, you may choose to plug in the values into the text and ask the model itself to figure out which constants the user has given; 
or you can relax the modelling assumption and assume the model has oracle access to the ground truth constant value; or you can further relax the assumption of knowing which "ancestor column" contains the constant provided.
However, in any case, you **SHOULD NOT** change the gold query, since test suite generation is dependent on it.

The "judge" function in evaluate_classical.py contains what you need to evaluate a single model prediction. 
It takes in the ground truth information of a datapoint (an element in classical_test.pkl, represented as a dictionary) and a model prediction (as  a string) and returns True/False - whether the prediction is semantically correct.

Suppose you have made a model prediction for every datapoint and write it into a .txt file (one prediction per line), you can use the following example command to calculate the accuracy

```
python3 evaluate_classical.py --pred=evaluation_examples/classical_test_gold.txt --out_file=goldclassicaltest.pkl
```

And here are the explanations of the arguments:

```
--pred PRED           the path to the predicted queries
--out_file OUT_FILE   the output file path
--num_processes NUM_PROCESSES
                    number of processes to use
```


