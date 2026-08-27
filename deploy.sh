#!/bin/sh

# amended by isabellhl.github.io
# on 7 Oct 2019

# If a command fails then the deploy stops
set -e

printf "\033[0;32m Deploying updates to GitHub:\033[0m\n"

# Build the project.
hugo -t academic # if using a theme, replace with `hugo -t <YOURTHEME>`

# public/ is a submodule holding the sringe.github.io repo. If it has not been
# checked out, it is an ordinary directory: git commands run inside it walk up
# and hit THIS repo instead, so the lines below would commit the whole build
# tree into the source repo and push that, leaving the live site untouched.
# Every command succeeds, so `set -e` does not catch it. Check first.
if [ ! -e public/.git ]; then
	printf "\033[0;31mpublic/ is not a submodule checkout -- run:\033[0m\n"
	printf "  git submodule update --init public\n"
	exit 1
fi

# Go To Public folder
cd public

printf "\033[0;32m Now in /public folder.\033[0m\n"

# Add changes to git.
printf "\033[0;32mChecking out master branch.\033[0m\n"
git checkout master
printf "\033[0;32mStaging changes.\033[0m\n"
git add .

# Commit changes.
printf "\033[0;32mCommitting.\033[0m\n"
msg="rebuilding site $(date)"
if [ -n "$*" ]; then
	msg="$*"
fi
git commit -m "$msg"

# Push source and build repos.
printf "\033[0;32mPushing to GitHub.\033[0m\n"
git push origin master
