import os
import re
from github import Github

def get_latest_leetcode(repo):
    """Fetches the latest solved LeetCode problem from the LeetCode repo."""
    commits = repo.get_commits()
    for commit in commits:
        files = commit.files
        for file in files:
            if file.filename.endswith(('.cpp', '.py', '.java', '.js')):
                name = os.path.basename(file.filename)
                return f"[{name}]({repo.html_url}/blob/main/{file.filename})"
    return "No recent LeetCode activity found."

def get_recent_activity(user, profile_repo_name, leetcode_repo_name):
    """Fetches recent activity from all repositories."""
    activity = []
    repos = user.get_repos(sort="updated", direction="desc")
    count = 0
    for repo in repos:
        if repo.name == profile_repo_name or repo.name == leetcode_repo_name:
            continue
        
        if count >= 5: # Limit to 5 recent activities
            break
            
        commits = repo.get_commits()
        if commits.totalCount > 0:
            latest_commit = commits[0]
            if repo.private:
                activity.append(f"- Committed to a private repository")
            else:
                activity.append(f"- Committed to [{repo.name}]({repo.html_url}): {latest_commit.commit.message.splitlines()[0]}")
            count += 1
            
    return "\n".join(activity) if activity else "No recent activity found."

def update_readme(token, username):
    g = Github(token)
    user = g.get_user(username)
    
    profile_repo = user.get_repo(username)
    leetcode_repo = user.get_repo("LeetCode")
    
    leetcode_content = f"### Latest LeetCode Solution\n- {get_latest_leetcode(leetcode_repo)}"
    activity_content = f"### Recent GitHub Activity\n{get_recent_activity(user, username, 'LeetCode')}"
    
    readme_file = profile_repo.get_contents("README.md")
    readme_text = readme_file.decoded_content.decode("utf-8")
    
    # Update LeetCode block
    new_readme_text = re.sub(
        r"<!-- LEETCODE_START -->.*?<!-- LEETCODE_END -->",
        f"<!-- LEETCODE_START -->\n{leetcode_content}\n<!-- LEETCODE_END -->",
        readme_text,
        flags=re.DOTALL
    )
    
    # Update Activity block
    new_readme_text = re.sub(
        r"<!-- ACTIVITY_START -->.*?<!-- ACTIVITY_END -->",
        f"<!-- ACTIVITY_START -->\n{activity_content}\n<!-- ACTIVITY_END -->",
        new_readme_text,
        flags=re.DOTALL
    )
    
    if new_readme_text != readme_text:
        profile_repo.update_file(
            readme_file.path,
            "Update profile README with latest activity",
            new_readme_text,
            readme_file.sha
        )
        print("README updated successfully.")
    else:
        print("No changes detected in README.")

if __name__ == "__main__":
    token = os.getenv("GH_PAT")
    username = os.getenv("GITHUB_USERNAME")
    if token and username:
        update_readme(token, username)
    else:
        print("Missing environment variables GH_PAT or GITHUB_USERNAME")
