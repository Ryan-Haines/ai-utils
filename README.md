# ai-utils
A collection of useful scripts related to AI workflows

install with `pip install -r requirements.txt`

to make batch masked images:
```
python batch_create_masks.py --path C:/path/to/training/images --out C:/path/to/mask/outputs
```

options:

--include-textfile: includes a .txt with the text read from the image
--corners: only create masks touching a corner
--edges: only create masks touching an edge or corner
