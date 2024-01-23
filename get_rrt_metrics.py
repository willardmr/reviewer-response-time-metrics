import argparse
from lib.transform_data import transform_data
from lib.write_table_to_file import write_table_to_file
from lib.download_data import download_data

parser = argparse.ArgumentParser(description="Downloads PR review data from GitHub for a given repo")
parser.add_argument(
    "repo_owner", help="the owner of a GitHub repo. For 'https://github.com/Microsoft/TypeScript' would be 'Microsoft'"
)
parser.add_argument(
    "repo_name",
    help=
    "the name of a GitHub repo of the above owner. For 'https://github.com/Microsoft/TypeScript' would be 'TypeScript'"
)
parser.add_argument(
    "output_filename",
    help=
    "The name of the output markdown file."
)
parser.add_argument("-n", "--num-prs", type=int, help="the total number of PRs to download from the repo", default=1000)
args = parser.parse_args()

data = download_data(args.repo_owner, args.repo_name, args.num_prs)
reviews = transform_data(data)
write_table_to_file(reviews, args.output_filename)