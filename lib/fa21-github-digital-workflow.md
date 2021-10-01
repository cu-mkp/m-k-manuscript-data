# FA21 Digital Sprints - Github &amp; Digital Workflows

## Main workflow: setting up to work in a branch in a github project

1. Create issue (or find one already created)
2. Assign to someone (or yourself)
3. Open the command line
4. If you are using the Linux Subsystem for Windows, run the command:
     1. `winhome`
5. Navigate to the repository you want to work in, e.g., `m-k-manuscript-data`
     1. For example, if this is where you start: `/mnt/c/Users/naomi/`, run the commands:
     2. /mnt/c/Users/naomi/ `cd Github`
     3. /mnt/c/Users/naomi/Github/ `cd m-k-manuscript-data`
6. Pull the most updated version of the repository
     1. `git fetch`
     2. `git pull`
7. Create new branch titled &quot;issue[##]&quot; (no spaces or special characters)
     1. `git checkout -b [name of branch e.g. issue73]`
8. Make edits to repository files (in text editors such as Atom, oXygen, or in whatever program suits the files you are working with)
9. Add file in local repository for tracking in github repository
     1. `git add .`
     2. `git commit -m '#[issue##]: [commit message]'` (this will ensure that this commit us linked to the issue you are working on)
10. Push to the remote server (for the first time, MUST BE TRACKED)
     1. `git push -u origin [branchname]`
11. Submit a pull request in github interface (browser) to merge your issue branch with master
     1. Go to the &quot;pull request&quot; tab where a message should appear asking if you would like to open a pull request
     2. Another option: In branch dropdown menu, select the branch you want to merge, then hit the &quot;new pull request&quot;
12. THC or NJR will merge the pull request unless there are conflicts to be resolved
13. Close the issue
14. `git checkout master` (= switch back to master branch)
     1. `git checkout main` (master/main depending on the repository)

## Other helpful commands

- `pwd` &quot;print working directory&quot; -- tells you where you are in the command line
- `ls` &quot;list&quot; -- tells you what files and folders are in the directory you are in
- `cd` &quot;change directory&quot; -- this followed by the name of the directory or a path will move you to that directory
- `cd ..` -- moves you up one directory
- `less` [name of file] script reader
- `q` &quot;quit&quot; -- exit out of a programming that is running

## Clone repository from github (to make a local version)

- [https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)
- Terry says SSH (better option) if you&#39;re using your regular computer (i.e., the same public key that&#39;s on your computer and associated with your GitHub account); otherwise HTTPS
     - See [https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh](https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
     - When you get to step 2., after the &quot;touch…&quot; command, do the following:
          - dyn-209-2-208-139:Github generaleditor$ `touch ~/.ssh/config`
          - dyn-209-2-208-139:Github generaleditor$ `nano ~/.ssh/config`
          - _This will open the text editor_
          - _Paste in the &quot;\* host…&quot;_
          - _Press &quot;ctrl&quot; + &quot;x&quot;, then &quot;y&quot;, then &quot;return&quot;_
          - dyn-209-2-208-139:Github generaleditor$
     - `$ git clone [https://github.com/](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY)[_YOUR-USERNAME_](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY)[/](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY)[_YOUR-REPOSITORY_](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY)_`_


## Check what branch you are in and make sure it is correct

- See also [https://www.git-tower.com/learn/git/faq/checkout-remote-branch](https://www.git-tower.com/learn/git/faq/checkout-remote-branch)
- _Navigate into the desired directory (i.e. m-k-manuscript-data)_
- `git branch` _(tells you which branch you are in)_
- `git fetch` _(tells you what is happening in remote repo)_
- `git status` _(tells you which branch you&#39;re on and how far ahead or behind you are from Origin)_
- If status is behind, pull the most current version
     - `git fetch`
     - `git pull`
