import subprocess

def run_git(files, message, branch="main"):
    # Stage changes
    subprocess.run(["git", "add", files], check=True)

    # Commit changes
    subprocess.run(["git", "commit", "-m", message], check=True)

    # Push to remote
    subprocess.run(["git", "push", "origin", branch], check=True)

# Example usage
run_git(".", "Updated serializer logic", "main")
