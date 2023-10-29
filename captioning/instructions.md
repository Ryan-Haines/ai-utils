### `Append_filename_to_caption` Function Documentation

---

#### **Description**

`Append_filename_to_caption` is a Python function that traverses a directory structure starting from a specified root folder. It identifies image files and their corresponding `.txt` files to append modified file names based on transformation rules.

---

#### **Parameters**

- `input_folder (str)`: The root folder to begin directory traversal.
- `clean (bool)`: If set to `True`, sanitizes the file names by removing digits and replacing hyphens and underscores with spaces. Default is `False`.
- `strip_text (str, optional)`: Text to be removed from the file names. Default is `None`.
- `strip_regex (str, optional)`: Regular expression pattern to be removed from the file names. Default is `None`.
- `replace_tuples (list of tuples, optional)`: A list of tuples, where each tuple contains a pair of strings. The first string is the text to find, and the second is the text to replace it with. Default is an empty list.

---

#### **Usage**

```python
process_txt(input_folder='/path/to/root', clean=True, strip_text='strip_this', strip_regex='[0-9]', replace_tuples=[('find1', 'replace1'), ('find2', 'replace2')])

