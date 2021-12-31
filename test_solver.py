import pathlib
import pytest

from nonogram_solver import file_reader


def get_dataset_item(element_path):
    input_file_path = element_path
    output_file_path = pathlib.Path('tests/output/' + element_path.stem)
    if input_file_path.is_file() and output_file_path.is_file():
        return input_file_path, output_file_path
    return None


def get_dataset(dataset_directory_path):
    return list(filter(
        bool, map(get_dataset_item, dataset_directory_path.iterdir())
    ))


@pytest.mark.parametrize(
    'input_file_path,expected_file_path',
    get_dataset(pathlib.Path('tests/input'))
)
def test(input_file_path, expected_file_path):
    nonogram = file_reader(input_file_path)
    nonogram.solve()
    with open(expected_file_path) as f:
        answer = f.read()

    if str(nonogram) != answer:
        raise ValueError('Test failed')
