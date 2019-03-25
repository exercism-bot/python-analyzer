import ast
from pylint import epylint as lint
import json

# Feedback for common mistakes
no_module = "No module called two_fer.py found in file path."
no_method = "No method called two_fer."
malformed_code = "The code is malformed and cannot be parsed for analysis."
simple_concat = "String concatenation with the + operator is a valid approach, but f-strings and str.format offer more " \
                "functionality and elegant solutions."
no_def_arg = "No default arguments are used in this solution. An ideal solution should make use of a default argument " \
             "and either f-strings or str.format."
conditionals = "Conditionals are unnecessarily used in this solution. An ideal solution should make use of a default " \
               "argument and either f-strings or str.format."
no_return = "'return' is not used to return the result string. This solution should fail pytest. Try run 'pytest' inside" \
            "the two-fer directory and observe the pass/fail results."
wrong_def_arg = "A value other than 'you' is used as a default argument."
percent_formatting = "%-formatting is a valid approach, but f-strings and str.format offer more functionality and " \
                     "elegant solutions."

def analyze(file_path):
    """
    Analyze the user's Two Fer solution to give feedback and disapprove malformed solutions.

    :return: A tuple containing a list of feedback comments as its first entry, a bool indicating whether a
        solution should be approved as its second entry, a list of comments generated by Pylint as its third entry,
        and a 'status' string corresponding to the value of the status key in the generated JSON, as its fourth
        entry.
    """

    # Input file
    try:
        with open(file_path, 'r') as f:
           user_solution = f.read()
    except:
        # If the proper file cannot be found, disapprove this solution
        output = {}
        output['status'] = 'disapprove_with_comment'
        output['comment'] = [no_module]
        output['pylint_comment'] = []
        json_output = json.dumps(output)
        file = open('analysis.json', 'w')
        file.write(json_output)
        file.close()
        return ([no_module], False, [], 'disapprove_with_comment')

    try:
        # Parse file to abstract syntax tree
        tree = ast.parse(user_solution)
    except:
        # If ast.parse fails, the code is malformed and this solution is disapproved
        output = {}
        output['status'] = 'disapprove_with_comment'
        output['comment'] = [malformed_code]
        output['pylint_comment'] = []
        json_output = json.dumps(output)
        file = open('analysis.json', 'w')
        file.write(json_output)
        file.close()
        return ([malformed_code], False, [], 'disapprove_with_comment')

    # List of comments to return at end, each comment is a string
    comments = []
    pylint_comments =[]
    # Whether to approve the user's solution based on analysis. Note that this only denotes if it's POSSIBLE for the
    # user's solution to be approved; just because the user didn't submit something that automatically makes it get
    # disapproved, like an empty file or missing method header, doesn't mean it's actually correct. Final assessment
    # of the user's solution must be done by a mentor (unless the solution is one of the optimal solutions we check for).
    approve = True
    # Does the solution have a method called two_fer?
    has_method = False
    # Does the solution correctly use a default argument?
    uses_def_arg = False
    # Does the solution have a return value?
    has_return = False
    # Does the solution use str.format?
    uses_format = False
    # Does the solution use f-strings?
    uses_f_string = False

    for node in ast.walk(tree):
        # Search for method called two_fer
        if isinstance(node, ast.FunctionDef):
            if node.name == 'two_fer': has_method = True

        # Search for use of string concatenation with + operator
        elif isinstance(node, ast.Add) and simple_concat not in comments: comments += [simple_concat]

        # Search for use of default arguments
        elif isinstance(node, ast.arguments):
            if node.defaults:
                uses_def_arg = True
                # Search for use of incorrect default argument
                try:
                    if node.defaults[0].s != 'you' and wrong_def_arg not in comments: comments += [wrong_def_arg]
                except:
                    if wrong_def_arg not in comments: comments += [wrong_def_arg]

        # Search for use of unnecessary conditionals
        elif isinstance(node, ast.If) and conditionals not in comments: comments += [conditionals]

        # Search for use of %-formatting
        elif isinstance(node, ast.Mod) and percent_formatting not in comments: comments += [percent_formatting]

        # Search for return
        elif isinstance(node, ast.Return): has_return = True

        # Search for use of str.format
        elif isinstance(node, ast.Call):
            try:
                if node.func.attr == 'format': uses_format = True
            except:
                pass

        # Search for use of f-strings
        try:
            if isinstance(node, ast.FormattedValue): uses_f_string = True
        except:
            pass # Fail if python version is too low
    if not has_method:
        comments += [no_method]
        approve = False

    if not uses_def_arg:
        comments += [no_def_arg]

    if not has_return:
        comments += [no_return]
        approve = False

    # Use Pylint to generate comments for code, e.g. if code follows PEP8 Style Convention
    (pylint_stdout, pylint_stderr) = lint.py_run(file_path, return_std=True)
    pylint_comments += [pylint_stdout.getvalue()]

    # Set solution status
    if approve and (not comments) and (uses_format or uses_f_string): status = 'approve_as_optimal'
    elif not approve: status = 'disapprove_with_comment'
    else: status = 'refer_to_mentor'

    # Convert to json output format and print to analysis.json
    output = {}
    output['status'] = status
    output['comment'] = comments
    output['pylint_comment'] = pylint_comments
    json_output = json.dumps(output)
    file = open('analysis.json',  'w')
    file.write(json_output)
    file.close()

    return (comments, approve, pylint_comments, status)
