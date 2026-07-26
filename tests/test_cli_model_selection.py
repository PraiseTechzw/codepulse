import os

from codepulse.cli import build_parser


def test_build_parser_accepts_model_option():
    parser = build_parser()
    args = parser.parse_args(["--model", "cohere/north-mini-code:free"])
    assert args.model == "cohere/north-mini-code:free"
