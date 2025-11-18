#!/bin/bash

# Script to commit and push all GitHub-ready files
# Run: chmod +x commit-github-files.sh && ./commit-github-files.sh

echo "🚀 Preparing to commit GitHub community files..."

# Add all new files
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short

echo ""
read -p "Do you want to commit these changes? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Commit with descriptive message
    git commit -m "docs: add comprehensive GitHub community files and templates

- Add issue templates (bug, feature, docs, question)
- Add pull request template with checklist
- Add Code of Conduct (Contributor Covenant 2.1)
- Add Support documentation with FAQ
- Add GitHub workflows (CI/CD, greetings)
- Add Dependabot configuration
- Add FUNDING.yml for sponsorship
- Add .editorconfig for consistent coding style
- Add .dockerignore for Docker builds
- Update README with professional badges and layout
- Add repository setup guide

This makes the project more professional and contributor-friendly."

    echo ""
    echo "✅ Changes committed successfully!"
    echo ""
    read -p "Do you want to push to GitHub? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "📤 Pushing to GitHub..."
        git push origin main
        echo ""
        echo "🎉 Successfully pushed to GitHub!"
        echo ""
        echo "📍 Next steps:"
        echo "1. Visit your repository on GitHub"
        echo "2. Check the new Issue Templates"
        echo "3. Configure repository settings (see .github/REPOSITORY_SETUP.md)"
        echo "4. Add screenshots to README.md"
        echo "5. Set repository description and topics"
    else
        echo "⏸️  Changes committed but not pushed. Run 'git push origin main' when ready."
    fi
else
    echo "❌ Commit cancelled. No changes made."
fi
