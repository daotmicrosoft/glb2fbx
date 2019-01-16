import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="description of this tool")
    parser.add_argument(
        "-myflag",
        help="description of this flag")

    args = parser.parse_args()