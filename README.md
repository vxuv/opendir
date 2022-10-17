# opendir
Simple wrapper for scraping open directories.


## Installation
```bash
pip3 install git+https://github.com/vxuv/opendir
```

## Usage
```python
  host = OpenDir('http://127.0.0.1/')
  for file in host.get_files():
      print(file)
```

