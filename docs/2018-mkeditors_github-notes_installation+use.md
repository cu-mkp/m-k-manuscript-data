> 2018-09-24 Notes by M&K team during training<br><br>
>Attendees: Terry, Pamela, Sophie, Tillmann, Tianna, and Naomi


# Git

-   Resource: Pro Git book, written by Scott Chacon and Ben Straub
    > [<u>https://git-scm.com/book/en/v2</u>](https://git-scm.com/book/en/v2)
    > (available online, as pdf and epub for free)

# GitHub

-   Resource:
    - [<u>https://help.github.com/</u>](https://help.github.com/)

    -   [<u>https://help.github.com/articles/git-and-github-learning-resources/</u>](https://help.github.com/articles/git-and-github-learning-resources/)

-   A website that hosts repositories through a version control program
    - called “Git”

-   Allows for distributed version control

-   You control when your local repository pushes to the remote server
    - (=”origin”)

# Installing GitHub

**PART I**

OSX:

-   Open the Terminal

-   Command: git (return)

-   Command: cd

-   Command: mkdir Github

    -   Note: it is not necessary to make a directory for your Github
        > work, but it does help to organize your files so that Git can
        > have a specific place to look

-   Command: cd Github

WINDOWS

-   Git command shell (separate installation process)

**PART II**

-   Go to github.com

-   Create an account

-   Join the cu-mkp organization (accessible at [<u>https://github.com/cu-mkp</u>](https://github.com/cu-mkp))

-   New cu-mkp “team”
    -  ([<u>https://github.com/orgs/cu-mkp/teams</u>](https://github.com/orgs/cu-mkp/teams)) has been created, **MK-editors**

    -   Given write access to m-k-manuscript-data
        > ([<u>https://github.com/cu-mkp/m-k-manuscript-data</u>](https://github.com/cu-mkp/m-k-manuscript-data))

-   **\*\*\*Editorial team will be working in cu-mkp /
    - m-k-manuscript-data**

-   Clone the desired repository

    -   Look for the green “clone or download” button (upper right)

    -   Select “clone with SSH”

        -   SSH is a security protocol that enables computers to talk to each other using public key cryptography

            -   Everyone has a private key and a public key

            -   [<u>https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/</u>](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/)

            -   [<u>https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/</u>](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/)

            -   If you are interested, some background on public key cryptography:

                -   Basic description: [<u>https://www.comodo.com/resources/small-business/digital-certificates2.php</u>](https://www.comodo.com/resources/small-business/digital-certificates2.php)

                -   Fuller description and history: [<u>https://www.theatlantic.com/magazine/archive/2002/09/a-primer-on-public-key-encryption/302574/</u>](https://www.theatlantic.com/magazine/archive/2002/09/a-primer-on-public-key-encryption/302574/)

    -   Copy the repository address

-   Command: git clone \[repository address\]


# Working with the Git repository from within the Terminal

-   See:
    - [<u>https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository</u>](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) for a full and authoritative (but understandable) review of the process

-   “.git” directory contains files that tracks and manages everything in the repository

    -   Becomes aware of files

    -   Tracks the files - anytime something happens to a file, it compares the repo before and after a change, and logs the differences as a delta

    -   This is a record of all changes to the repo

-   There are three states of your local repository

    -   **Untracked** - create file in directory but git repo does not know about it

        -   Use “add” command to make git aware of a new file (it is then “staged”)

        -   Command: git add .

            -   This adds your previously untracked file to the repo’s *awareness* !

            -   If you make a change to this file, you will lose the previous version, since git is not recording the file and its changes

    -   **Tracked** - git is aware of a file in your local repository

        -   Use the “commit” command to make git track the staged file

        -   Command: git commit -m ‘\[short message, e.g., adding
            -  TESTFILE\]’ \[filename, e.g., TESTFILE\]

        -   Saves to local repository

    -   **Committed** - the current version of the file is being logged by the local repository

        -   I.e., committing = taking a snapshot of the file

            -   NB: you should be committing often because any of those committed “snapshots” can be returned to / recovered at any time

        -   There is a version of the file saved in your local repo, and its changes will be logged in the local repo

-   “Syncing” your local repository with the remote (or origin)

    -   **Pull** from the origin to your local

        -   Command: git pull --rebase

            -   “--rebase” will sync all recent changes in the remote repo first and then include the your local ones. This will eliminate an annoying message asking you to explain a merge. If the merge screen asking to justify appears, type: :q

    -   **Push** from your local to the origin

        -   Command: git push

            -   If your local repo is behind the origin, you will be unable to push

            -   Always pull --rebase before you push

# Navigating and working in the command line

-   For more info on bash: [<u>https://programminghistorian.org/en/lessons/intro-to-bash</u>](https://programminghistorian.org/en/lessons/intro-to-bash)

    -   Contains information, tutorials, and commands

-   Command: man \[command, e.g., ls\]

    -   Brings up the manual for that particular command, showing its rules

-   Command: git status

    -   Lets you know the relative status of your local repo v the remote/origin

-   Command: git log

    -   Lets you see what’s been going on in Git recently

-   Command: df -h

    -   Checks how much free space you have on your computer

-   Command: ls

    -   Gives you a list of the folders/files in your current directory

-   Command: ls -la

    -   Gives you a list of ALL (even hidden) files in your current directory

-   Command: cd

    -   = change directory: helps you change directories

    -   If you type “cd” with nothing after it, it will take you back to your home directory

    -   If you type “cd” with the name of a parent or child directory relative to where you are, you will move to that directory

    -   SHORTCUT: type “cd” and then the first character or two of your desired directory, then press \[tab\] and it will fill in the directory that matches the beginning of these characters

        -   If this freezes, then there is more than one directory that begins the same way. Type another character or two so it is unique

-   Command: cd ..

    -   = go up a level in directories

    -   cd ../.. = go up 2 levels!

-   Command: less \[filename of a file in your current directory\]

    -   Allows you to see the file’s contents

    -   NB: for filenames with spaces, precede each space with a backslash

-   Command: q

    -   = quit

    -   If you are stuck in a screen, use the q command to get back to the command line

-   Command: pwd

    -   = print working directory: tells you where you are (what directory you’re in)

-   Command: mkdir

    -   = make directory: create new directory

-   Command: mv \[filename\] \[new filename\]

    -   = move (but actually means rename the file)

-   Command: touch

    -   Creates a quick file

-   DANGER: Command: rm -fr/

    -   = remove, force (don’t ask questions or check if you’re sure), recursively from this directory

    -   wipes your hard drive — DO NOT DO THIS
