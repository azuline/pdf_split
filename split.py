#!/usr/bin/env python3
"""A simple pdf splitter which makes books readable on small screens."""
import argparse
from copy import copy
from PyPDF2 import PdfReader, PdfWriter


def split_pdf_pages(args: argparse.Namespace):
    """Split pages of a pdf."""
    with open(args.source, "rb") as source_file, open(args.target, "wb") as target_file:
        in_pdf = PdfReader(source_file)
        page_count = len(in_pdf.pages)

        out_pdf = PdfWriter()

        first_split_page = 0
        if not args.split_first_page:
            # add first page untouched
            first_page = in_pdf.pages[0]
            out_pdf.add_page(first_page)
            first_split_page = 1

        # split all following pages by half and add both halfs
        for page_number in range(first_split_page, page_count):
            page = in_pdf.pages[page_number]

            actual_width = page.mediabox.upper_right[0]
            actual_height = page.mediabox.upper_right[1]
            width = actual_width - args.crop_left - args.crop_right
            height = actual_height - args.crop_top - args.crop_bottom
            cut_width = width // args.splits

            for split_num in range(args.splits):
                split_page = copy(page)
                split_page.mediabox = copy(page.mediabox)

                upper_y = args.crop_bottom + height
                lower_y = args.crop_bottom

                right_x = min(
                    args.crop_left + width,
                    args.crop_left + args.margin + width - cut_width * split_num,
                )
                left_x = max(
                    args.crop_left,
                    args.crop_left - args.margin + width - cut_width * (1 + split_num),
                )

                split_page.mediabox.upper_left = left_x, upper_y
                split_page.mediabox.upper_right = right_x, upper_y
                split_page.mediabox.lower_left = left_x, lower_y
                split_page.mediabox.lower_right = right_x, lower_y

                split_page.cropbox = split_page.mediabox

                out_pdf.add_page(split_page)

        out_pdf.write(target_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument(
        "--margin", help="additional margin per split", type=int, default=10
    )
    parser.add_argument(
        "--splits", help="number of splits per page", type=int, default=2
    )
    parser.add_argument(
        "--crop-left",
        type=int,
        default=0,
        help="Additional margin to crop an all pages",
    )
    parser.add_argument(
        "--crop-top", type=int, default=0, help="Additional margin to crop an all pages"
    )
    parser.add_argument(
        "--crop-right",
        type=int,
        default=0,
        help="Additional margin to crop an all pages",
    )
    parser.add_argument(
        "--crop-bottom",
        type=int,
        default=0,
        help="Additional margin to crop an all pages",
    )
    parser.add_argument(
        "--split-first-page", action="store_true", help="Split the first page as well"
    )
    args = parser.parse_args()
    if args.splits < 1:
        parser.error(
            "argument --splits: invalid choice: " "split count may not be zero."
        )
    split_pdf_pages(args)
