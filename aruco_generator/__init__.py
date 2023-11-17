import argparse
import os
import sys
from types import SimpleNamespace

try:
  import cv2 as cv
except ImportError:
  print("failed to import cv2. is opencv installed?", file=sys.stderr)
  sys.exit(1)

import numpy as np

def generate_dictionary(args):
  return cv.aruco.extendDictionary(args.num_markers, args.marker_bits)

def generate_markers(dictionary, args):
  px_per_cm = args.ppi / 2.54
  marker_full_bits = args.marker_bits + 2*args.border_bits
  canvas_bits = marker_full_bits + 2*args.margin_bits

  if args.size_includes_margin:
    canvas_size_cm = args.size_cm
    marker_size_cm = (marker_full_bits / canvas_bits) * canvas_size_cm
  else:
    marker_size_cm = args.size_cm
    canvas_size_cm = (canvas_bits / marker_full_bits) * marker_size_cm

  canvas_size_cm += 2 * args.crop_mark_length_cm

  cm_per_bit = marker_size_cm / marker_full_bits

  marker_size_px = round(marker_size_cm * px_per_cm)
  canvas_size_px = round(canvas_size_cm * px_per_cm)
  border_size_px = round((canvas_size_cm - marker_size_cm) * 0.5 * px_per_cm)
  crop_mark_length_px = round(args.crop_mark_length_cm * px_per_cm)
  crop_mark_width_px = round(args.crop_mark_width_cm * px_per_cm)

  # if args.size_includes_margin:
  #   marker_to_canvas_ratio = marker_size_cm/canvas_size_cm

  print("generating marker images", file=sys.stderr)
  print(f"border bits: {args.border_bits}", file=sys.stderr)
  print(f"margin bits: {args.margin_bits}", file=sys.stderr)
  print(f"ppi: {args.ppi}", file=sys.stderr)
  print(f"marker size: {marker_size_cm:.03f} cm / {marker_size_px} px", file=sys.stderr)
  print(f"crop mark length: {args.crop_mark_length_cm:.03f} cm / {crop_mark_length_px} px", file=sys.stderr)
  print(f"crop mark width: {args.crop_mark_width_cm:.03f} cm / {crop_mark_width_px} px", file=sys.stderr)
  print(f"canvas size: {canvas_size_cm:.03f} cm / {canvas_size_px} px", file=sys.stderr)
  print(f"invert: {'yes' if args.invert else 'no'}")

  marker_img = np.zeros(
    (marker_size_px, marker_size_px, 1),
    dtype="uint8"
  )
  canvas_img = np.zeros(
    (canvas_size_px, canvas_size_px, 1),
    dtype="uint8"
  )

  marker_start_px = border_size_px
  marker_stop_px = marker_start_px + marker_size_px

  # x,y,w,h
  crop_mark_rect = (
    0,
    crop_mark_length_px - crop_mark_width_px,
    crop_mark_length_px,
    crop_mark_width_px
  )
  crop_mark_transforms = [
    lambda x,y,w,h: (x,y,w,h),
    lambda x,y,w,h: (canvas_size_px-w-x, y, w, h),
    lambda x,y,w,h: (x, canvas_size_px-1-h-y, w, h),
    lambda x,y,w,h: (canvas_size_px-w-x, canvas_size_px-1-h-y, w, h),
  ]

  for i in range(args.num_markers):
    canvas_img[:,:] = 255
    marker = cv.aruco.generateImageMarker(dictionary, i, marker_size_px, marker_img, args.border_bits)
    canvas_img[marker_start_px:marker_stop_px, marker_start_px:marker_stop_px] = marker_img

    if crop_mark_length_px > 0 and crop_mark_width_px > 0:
      for transform in crop_mark_transforms:
        x,y,w,h = transform(*crop_mark_rect)
        y0 = y
        y1 = y0 + h
        x0 = x
        x1 = x0 + w
        canvas_img[y0:y1, x0:x1] = 0
        canvas_img[x0:x1, y0:y1] = 0

    if args.invert:
      canvas_img = np.vectorize(lambda x: 255-x)(canvas_img)

    yield i, canvas_img

def save(marker, path):
  cv.imwrite(path, marker)

def main():
  arg_parser = argparse.ArgumentParser()

  arg_parser.add_argument(
    "-n", "--num-markers", type=int, required=True,
    help="number of markers to generate"
  )
  arg_parser.add_argument(
    "-m", "--marker-bits", type=int, required=True,
    help="number of bits to use for the markers, minimum 3"
  )
  arg_parser.add_argument(
    "-o", "--output", required=True,
    help="output directory for marker images"
  )
  arg_parser.add_argument(
    "-b", "--border-bits", type=int, default=1,
    help="number of bits to use for the border around each marker"
  )
  arg_parser.add_argument(
    "-g", "--margin-bits", type=float, default=0,
    help="number of bits to use for the margin area around each marker and its border (but see -z/--size-includes-margin)"
  )
  arg_parser.add_argument(
    "-s", "--size-cm", type=float, default=5,
    help="size of each marker in centimeters"
  )
  arg_parser.add_argument(
    "-p", "--ppi", type=float, default=300,
    help="pixels per inch value for converting centimeters to pixels"
  )
  arg_parser.add_argument(
    "-z", "--size-includes-margin", action=argparse.BooleanOptionalAction,
    help="make --size-cm specify the size of the marker plus the margin, instead of only the marker"
  )
  arg_parser.add_argument(
    "-i", "--invert", action=argparse.BooleanOptionalAction,
    help="invert each marker's colors"
  )
  arg_parser.add_argument(
    "-l", "--crop-mark-length-cm", type=float, default=0.0,
    help="length of crop marks in centimeters"
  )
  arg_parser.add_argument(
    "-w", "--crop-mark-width-cm", type=float, default=0.05,
    help="width of crop marks in centimeters"
  )

  args = arg_parser.parse_args()

  os.makedirs(args.output, exist_ok=True)

  print(f"generating aruco dictionary of {args.num_markers} {args.marker_bits}x{args.marker_bits} markers", file=sys.stderr)
  dictionary = generate_dictionary(args)

  dictionary_path = os.path.join(args.output, "dictionary.yaml")
  print(f"writing {dictionary_path}", file=sys.stderr)
  dictionary_fs = cv.FileStorage(dictionary_path, cv.FileStorage_WRITE)
  try:
    dictionary.writeDictionary(dictionary_fs)
  finally:
    dictionary_fs.release()

  for i, marker in generate_markers(dictionary, args):
    path = os.path.join(args.output, f"{i:02d}.png")
    print(f"writing {path}")
    save(marker, path)
