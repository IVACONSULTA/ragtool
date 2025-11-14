# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and paste at: https://github.com/settings/ssh/new

# Change remote to SSH
git remote set-url origin ${sshRepoName}
# Push your changes
git push origin ${banch_name}