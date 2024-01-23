import json
import os
import sys

import requests

PRS_PER_BATCH = 100
API_TOKEN_KEY = 'GH_API_TOKEN'

def download_data(repo_owner, repo_name, num_prs):
  if not API_TOKEN_KEY in os.environ:
      print(f"There must be a '{API_TOKEN_KEY}' environment variable defined", file=sys.stderr)
      exit(1)
  
  token = os.environ[API_TOKEN_KEY]
  ENDPOINT = 'https://api.github.com/graphql'
  HEADERS = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github.starfire-preview+json",
  }
  
  query = '''
  query($repoOwner: String!, $repoName: String!, $prBefore: String, $prCount: Int = 100){
    repository(owner: $repoOwner, name: $repoName) {
      pullRequests(last: $prCount, before: $prBefore) {
        pageInfo {
          startCursor
          hasPreviousPage
        }
        nodes {
          title
          timelineItems(first: 200, itemTypes:[REVIEW_REQUESTED_EVENT, REVIEW_REQUEST_REMOVED_EVENT, PULL_REQUEST_REVIEW, CLOSED_EVENT, MERGED_EVENT]) {
            nodes {
              ... on ReviewRequestedEvent {
                __typename
                createdAt
                requestedReviewer {
                  ...ReviewerInfo
                }
              }
              ... on ReviewRequestRemovedEvent {
                __typename
                createdAt
                requestedReviewer {
                  ...ReviewerInfo
                }
              }
              ... on PullRequestReview {
                __typename
                state
                submittedAt
                author {
                  login
                }
              }
              ... on ClosedEvent {
                __typename
                createdAt
              }
              ... on MergedEvent {
                __typename
                createdAt
              }
            }
          }
        }
      }
    }
  }
  
  fragment ReviewerInfo on RequestedReviewer {
    ... on User {
      login
    }
    ... on Team {
      name
    }
  }
  '''
  
  start_cursor = None
  has_previous_page = True
  all_nodes = []
  
  while has_previous_page and len(all_nodes) < num_prs:
      variables = dict(
          repoOwner=repo_owner,
          repoName=repo_name,
          prBefore=start_cursor,
          prCount=PRS_PER_BATCH,
      )
      data = json.dumps({"query": query, "variables": variables})
  
      response = requests.post(ENDPOINT, headers=HEADERS, data=data)
      response.raise_for_status()
      result = response.json()
  
      if 'errors' in result:
          print(result['errors'], file=sys.stderr)
          exit(1)
  
      pull_requests = result['data']['repository']['pullRequests']
      start_cursor = pull_requests['pageInfo']['startCursor']
      has_previous_page = pull_requests['pageInfo']['hasPreviousPage']
  
      all_nodes.extend(pull_requests['nodes'])
      print(f"Loaded {len(all_nodes)} pull requests", file=sys.stderr)
  else:
      print("Loaded all pull requests successfully", file=sys.stderr)
  return all_nodes 
  