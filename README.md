# ai-utils
A collection of useful scripts related to AI workflows

no warranty provided, use at your own risk.

install with `pip install -r requirements.txt`

to make batch masked images (recommended settings):
```
python batch_create_masks.py --path C:/path/to/training/images --out C:/path/to/mask/outputs --edges --min-total-area=1 --contain --draw-contain
```

some options: use `python batch_create_masks.py --help` to view all options


`--include-textfile`: includes a .txt with the text read from the image

`--corners`: only create masks touching a corner

`--edges`: only create masks touching an edge or corner

`--min-area`: the minimum area for a single bounding box. Below this the bounding box is not drawn, as a 1-100 percentage.

`--min-total-area`: The minimum area that must be occupied by all bounding boxes, as a 1-100 percentage.

`--max-area`: the maximum area between all bounding boxes. If the total area of bounding boxes is greater than this amount, the mask is skipped, as a 1-100 percentage.

`--contain`: trace a bounding box around all combinations of bounding boxes; then remove bounding boxes that fall outside the largest bounded area within --max-area. This will help eliminate detections that are not located near other detections.

`--draw-contain`: optionally use with --contain, draws a bounding box around the traced area.

`--contain-under-min`: optionally used with --draw-contain, only draws contain if the detected boxes have less than the total area already.

`--use-color=False` (defaults to true) converts image to grayscale before performing OCR

`--use-binary` converts the image to black/white before performing OCR. Try `--use-color=False` before trying this option

for img2img batch masking:

DPM++2m SDE Karras, 10 steps

Resize by 1

mask mode: INPAINT NOT MASKED!!! (areas to clear are covered with black boxes).
If WHITE areas are meant to be removed, choose INPAINT MASKED. 

masked content: fill

# boost caption token

For keep tokens, pick the token to advance to the front of the captions. Regex matchs first instance of `foo` to end of string, and boosts:
`python boost_caption_tokens.py --path ./texts --regex "foo.*$"`

otherwise, just boost a single token:
`python boost_caption_tokens.py --path ./texts --regex "foo,"`


# gather random images for dataset
python random_gather.py --path=/path/to/image/folders --outpath=/path/to/output/folder --ignore-ends
