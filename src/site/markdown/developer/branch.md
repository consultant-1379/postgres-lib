# Work in Progress

```bash
msg=$1
branch=$(git rev-parse --abbrev-ref HEAD)
changes=$(git diff)
if [[ "${changes}" != "" ]]; then
    echo "YOU HAVE UNCOMMITTED CHANGES!!!"
    exit 1
fi
git checkout master
git reset --hard origin/master
git pull origin master
git merge ${branch} --squash
git commit -a -m "$msg"
git push origin HEAD:refs/for/master
git reset --hard origin/master
git checkout ${branch}
```