try:
    import src.utils.auto_gen_utils as auto_gen_utils
except Exception as e:
    print(f'ERROR: {e}')
    import utils.auto_gen_utils as auto_gen_utils

def test_example():
    example = 'Project A'
    result = auto_gen_utils.format_project_name_helper(example)
    expected = 'project_a'
    assert result == expected 