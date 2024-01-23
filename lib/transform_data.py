import isodate
import sys
from typing import Dict, List
import arrow

from lib.models import *

def transform_data(data):
    reviews: List[Review] = []
    for pr in data:
        # dict from name of login of requested reviewer -> time review should be done
        requested_reviews: Dict[str, arrow.Arrow] = {}

        # raw data transformation step
        for item in pr['timelineItems']['nodes']:
            # transform all datetime strings into localized arrow datetime objects
            if 'createdAt' in item:
                item['createdAt'] = arrow.get(item['createdAt'])
            if 'submittedAt' in item:
                item['submittedAt'] = arrow.get(item['submittedAt'])

        # computation step
        for item in pr['timelineItems']['nodes']:
            typename = item['__typename']
            if typename == 'ReviewRequestedEvent':
                if not 'login' in item['requestedReviewer']:
                    continue

                reviewer = item['requestedReviewer']['login']
                time_due = item['createdAt']

                requested_reviews[reviewer] = time_due

            elif typename == 'PullRequestReview':
                time = item['submittedAt']
                reviewer = item['author']['login']

                if reviewer in requested_reviews:
                    time_due = requested_reviews[reviewer]
                    reviews.append(Review(reviewer, isodate.duration_isoformat(time - time_due)))
                    requested_reviews.pop(reviewer, None)
                else:
                    # someone submitted a review even though nobody requested it
                    # we don't need to do anything in this case
                    pass

            elif typename == 'ReviewRequestRemovedEvent':
                if not 'login' in item['requestedReviewer']:
                    continue

                reviewer = item['requestedReviewer']['login']
                time = item['createdAt']

                if reviewer in requested_reviews:
                    requested_reviews.pop(reviewer, None)
                else:
                    # unusual state we don't expect to ever happen:
                    print(f"Review request removed but reviewer #{reviewer} not found", file=sys.stderr)

            elif typename in ['ClosedEvent', 'MergedEvent']:
                time = item['createdAt']

                # for every requested review when the PR is closed, see if it should've been completed yet or not
                for reviewer, time_due in requested_reviews.items():
                        reviews.append(Review(reviewer, isodate.duration_isoformat(time - time_due)))

            else:
                print(f"Unknown type: {typename}", file=sys.stderr)
    return reviews