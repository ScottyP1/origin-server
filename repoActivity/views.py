import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from repo.models import Repo
from .models import RepoActivity
from .serializers import RepoActivitySerializer


class AllRepoActivity(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        access_token = user.github_access

        if not access_token:
            return Response({"error": "GitHub token not found"}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}
        user_repos = Repo.objects.filter(client=user)

        total_new_events = 0

        for repo in user_repos:
            owner = user.username
            repo_name = repo.name

            try:
                # ✅ Sync Commits
                total_new_events += self.sync_commits(repo, headers, owner, repo_name)

                # ✅ Sync Pull Requests
                total_new_events += self.sync_pull_requests(repo, headers, owner, repo_name)

                # ✅ Sync Issues
                total_new_events += self.sync_issues(repo, headers, owner, repo_name)

                # ✅ Sync Events (optional)
                total_new_events += self.sync_events(repo, headers, owner, repo_name)

            except Exception as e:
                print(f"Error syncing repo {repo.name}: {e}")
                continue

        # Return the most recent 25 activities
        activities = RepoActivity.objects.filter(client=user).order_by('-created_at')[:25]
        serializer = RepoActivitySerializer(activities, many=True)

        return Response({
            "status": "ok",
            "total_new_events": total_new_events,
            "activities": serializer.data
        })

    def sync_commits(self, repo, headers, owner, repo_name):
        url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return 0

        commits = response.json()
        new_events = 0

        for commit in commits[:5]:
            github_id = commit.get("sha")
            author = commit.get("commit", {}).get("author", {}).get("name")
            message = commit.get("commit", {}).get("message")
            created_at = commit.get("commit", {}).get("author", {}).get("date")

            _, created = RepoActivity.objects.get_or_create(
                github_id=github_id,
                defaults={
                    "client": repo.client,
                    "repo": repo,
                    "type": "Commit",
                    "author": author,
                    "description": message,
                    "created_at": created_at,
                }
            )
            if created:
                new_events += 1

        return new_events

    def sync_pull_requests(self, repo, headers, owner, repo_name):
        url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls?state=all"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return 0

        prs = response.json()
        new_events = 0

        for pr in prs[:5]:
            github_id = str(pr.get("id"))
            author = pr.get("user", {}).get("login")
            title = pr.get("title")
            created_at = pr.get("created_at")

            _, created = RepoActivity.objects.get_or_create(
                github_id=github_id,
                defaults={
                    "client": repo.client,
                    "repo": repo,
                    "type": "PullRequest",
                    "author": author,
                    "description": title,
                    "created_at": created_at,
                }
            )
            if created:
                new_events += 1

        return new_events

    def sync_issues(self, repo, headers, owner, repo_name):
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=all"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return 0

        issues = response.json()
        new_events = 0

        for issue in issues[:5]:
            # skip PRs (GitHub mixes issues and PRs here)
            if "pull_request" in issue:
                continue

            github_id = str(issue.get("id"))
            author = issue.get("user", {}).get("login")
            title = issue.get("title")
            created_at = issue.get("created_at")

            _, created = RepoActivity.objects.get_or_create(
                github_id=github_id,
                defaults={
                    "client": repo.client,
                    "repo": repo,
                    "type": "Issue",
                    "author": author,
                    "description": title,
                    "created_at": created_at,
                }
            )
            if created:
                new_events += 1

        return new_events

    def sync_events(self, repo, headers, owner, repo_name):
        url = f"https://api.github.com/repos/{owner}/{repo_name}/events"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return 0

        events = response.json()
        new_events = 0

        for event in events[:5]:
            github_id = str(event.get("id"))
            event_type = event.get("type")
            actor = event.get("actor", {}).get("login", None)
            payload = event.get("payload", {})
            description = str(payload)[:500]
            created_at = event.get("created_at")

            _, created = RepoActivity.objects.get_or_create(
                github_id=github_id,
                defaults={
                    "client": repo.client,
                    "repo": repo,
                    "type": event_type,
                    "author": actor,
                    "description": description,
                    "created_at": created_at,
                }
            )
            if created:
                new_events += 1

        return new_events
