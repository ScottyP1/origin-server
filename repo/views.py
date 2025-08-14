from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import rest_framework.status as s
from .models import Repo
from .serializers import RepoSerializer
import requests
from socialAccounts.models import SocialAccount
from django.shortcuts import get_object_or_404


# ---------- helpers ----------

def fetch_commit_count_from_events(owner: str, repo: str, token: str, since_iso: str | None = None) -> int:
    """
    Count commits by summing PushEvent payload.distinct_size from the repo events feed.
    Fast and reflects activity almost immediately.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/events"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    total = 0
    page = 1
    while True:
        r = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
        r.raise_for_status()
        events = r.json()
        if not events:
            break

        for e in events:
            if e.get("type") != "PushEvent":
                continue
            if since_iso and e.get("created_at") and e["created_at"] < since_iso:
                continue
            payload = e.get("payload") or {}
            # distinct_size is unique commits in the push; size includes non-distinct
            total += int(payload.get("distinct_size", 0))

        if "next" not in r.links:
            break
        page += 1

    return total


# ---------- views ----------

class getTrackedRepos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user
        repos = Repo.objects.filter(client=client)
        return Response(RepoSerializer(repos, many=True).data, status=s.HTTP_200_OK)

    def delete(self, request, id):
        repo = get_object_or_404(Repo, id=id, client=request.user)
        repo.delete()
        return Response(status=s.HTTP_204_NO_CONTENT)


class getAllRepos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user
        account = SocialAccount.objects.filter(user=request.user, provider="github").first()
        if not account:
            return Response({"error": "No GitHub account connected"}, status=s.HTTP_400_BAD_REQUEST)

        headers = {"Authorization": f"Bearer {account.access_token}", "Accept": "application/vnd.github+json"}
        github_res = requests.get(
            "https://api.github.com/user/repos?type=owner&per_page=100&page=1",
            headers=headers
        )
        github_res.raise_for_status()
        github_data = github_res.json()

        tracked_ids = set(Repo.objects.filter(client=client).values_list("github_id", flat=True))
        untracked = [
            {"id": r["id"], "name": r["name"], "html_url": r["html_url"]}
            for r in github_data
            if r.get("id") not in tracked_ids
        ]

        # Return plain dicts; do NOT wrap in ModelSerializer
        return Response(untracked, status=s.HTTP_200_OK)


class AddRepoToUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        repo_id = request.data.get("id")
        repo_name_from_client = request.data.get("name")

        account = SocialAccount.objects.filter(user=user, provider="github").first()
        if not account:
            return Response({"error": "No GitHub account connected"}, status=s.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Accept": "application/vnd.github+json",
        }

        # Validate repo ID and get canonical metadata
        repo_meta = requests.get(f"https://api.github.com/repositories/{repo_id}", headers=headers)
        if repo_meta.status_code == 404:
            return Response({"error": "Repo not found with this id"}, status=s.HTTP_404_NOT_FOUND)
        repo_meta.raise_for_status()
        meta = repo_meta.json()

        full_name = meta.get("full_name")  # "owner/repo"
        html_url = meta.get("html_url", "")
        canon_name = meta.get("name", repo_name_from_client)

        # Open PRs / Issues (Search API)
        pr_q = f"is:open is:pr repo:{full_name}"
        issue_q = f"is:open is:issue repo:{full_name}"
        pr_res = requests.get(f"https://api.github.com/search/issues", headers=headers, params={"q": pr_q})
        pr_res.raise_for_status()
        pr_count = int(pr_res.json().get("total_count", 0))

        issue_res = requests.get(f"https://api.github.com/search/issues", headers=headers, params={"q": issue_q})
        issue_res.raise_for_status()
        issue_count = int(issue_res.json().get("total_count", 0))

        # Commit count (fast + near-real-time) from repo events
        try:
            owner, short_repo = full_name.split("/", 1)
            commit_count = fetch_commit_count_from_events(owner, short_repo, account.access_token)
        except Exception:
            # Fail-safe: don't block add; store 0 if events call fails
            commit_count = 0

        repo, _created = Repo.objects.get_or_create(client=user, github_id=repo_id)
        repo.name = canon_name
        repo.html_url = html_url
        repo.open_pr_count = pr_count
        repo.open_issue_count = issue_count
        repo.commit_count = commit_count
        repo.save()

        return Response(RepoSerializer(repo).data, status=s.HTTP_200_OK)
