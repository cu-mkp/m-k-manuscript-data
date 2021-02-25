# Github and oXygen Workflow (Making and Knowing Project)

The following workflow was first created in February 2019 as part of an XML-editing sprint undertaken by the Project team to ensure translation and encoding consistency. The notes include tutorials and internal protocols for editing [ms-xml/](https://github.com/cu-mkp/m-k-manuscript-data/tree/master/ms-xml).

## CONSISTENCY WORK OVERVIEW AND PROTOCOL:

1. Create issue
2. Assign to someone
3. Move issue into "in progress" column of Project
4. In command line, get into your m-k-manuscript-data repository
5. Pull the most updated version of m-k-manuscript-data
  ```
  git fetch
  git pull 
  ```
6. Create new branch titled `issue[##]`
  `git checkout -b [name of branch e.g. issue 73]`
7. In oXygen:
  1. Refresh content of m-k-manuscript-data
  2. find/replace etc.
    1. NB: Assume that there may be any number of spaces between the words in a phrase you are searching for. You may select "Ignore extra whitespace" to address this. Otherwise, you can also locate target phrases by the smallest component to match (e.g., &quot;vye&quot; or &quot;eau de&quot; when looking for &quot;eau de vye&quot;)
8. Add file in local repository for tracking in github repository
  1. git add .
  2. git commit -m &#39;#[issue##]: [commit message]&#39;
9. Push to the remote server (for the first time, MUST BE TRACKED)
  1. git push -u origin [branchname]
10. Update issue with a comment listing all actions taken in oXygen
  1. For translation work, list all variants used, any problems etc.
  2. List updates to VOCAB list
  3. About find/replace presets: assumed that no search options are checked (e.g. &quot;case sensitive&quot; or &quot;whole words only&quot;
    1. If any are checked, specify in comment
  4. If task could not be completed, label the issue &quot;blocked&quot;
    1. Do not close the issue, and update with comments about what problems there were or what needs to be resolved
11. Close the issue
12. Submit a pull request in github interface (browser) to merge your issue branch with master
  1. In branch dropdown menu, select the branch you want to merge, then hit the &quot;new pull request&quot;
13. THC will merge unless there are conflicts to be resolved
14. git checkout master (= switch back to master branch)
15. git branch (OPTIONAL - to check you&#39;re in the master)
16. git fetch
17. git pull -a

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif) ![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**CREATING ISSUES in GitHub for CONSISTENCY WORK**

1. Make sure you are in the &quot;[https://github.com/cu-mkp/m-k-manuscript-data](https://github.com/cu-mkp/m-k-manuscript-data)&quot; GitHub repo
2. Navigate to the &quot;Issues&quot; tab
3. Click &quot;New Issue&quot;
4. In the &quot;title&quot; bar, give a brief descriptive title so that the issue can be grasped at a glance
5. In the &quot;Leave a comment&quot; text box, elaborate on the issue.
6. Assign the appropriate labels (e.g., &quot;consistency,&quot; &quot;translation&quot;/&quot;markup,&quot; and &quot;straightforward&quot;/&quot;problematic&quot;
7. Assign the appropriate project label (&quot;Consistency issues in ms text&quot;)
8. Click &quot;Submit New Issue&quot;

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

_**Newly created issues (if tagged with the project label) will automatically be moved into the &quot;TO DO&quot; board of our &quot;Consistency issues&quot; GitHub project**_

ADDITIONAL INFO: PROJECTS IN GitHub

- New projects must be created in the &quot;Projects&quot; tab of the GitHub repository
- New issues can be automatically assigned to the proper board
  - Must be enabled in the project(s)
    - Option available by clicking on the &quot;...&quot; button in the upper right corner of a given project board
  - When creating the issue, &quot;assign&quot; the appropriate project(s) as one would assign a label so it will appear in the &quot;to do&quot; column of the project(s) automatically
- Terry&#39;s recommendations for columns
  - &quot;To do&quot;
    - Backlog, grabbag unlogged
  - &quot;Next&quot;
    - Prioritized from &quot;to do&quot;
  - &quot;In Progress&quot;
  - &quot;

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**CONSISTENCY WORKFLOW**

1. Make sure you are in the &quot;[https://github.com/cu-mkp/m-k-manuscript-data](https://github.com/cu-mkp/m-k-manuscript-data)&quot; GitHub repo
2. Navigate to the &quot;Projects&quot; tab
3. Select &quot;Consistency issues in ms text&quot;
4. Filter for your own assigned tasks

- As issues get worked through and/or commented on, they may generate decisions that can be spun off into new, better defined issues
  - New issues that spring from decisions should be given a &quot;decision&quot; label

**OXYGEN**

- Open Oxygen
- Project \&gt; New Project
- Name it &quot;m-k-manuscript-data&quot;
  - Save it in your local GitHub repo, in &quot;m-k-manuscript-data&quot;
- Open &quot;ms-xml&quot;
- Right click on each of the data folders and go to &quot;Validate&quot; &quot;Check Well-formedness&quot;
- If good, move on
- Right click on &quot;tl&quot; and go to &quot;Find/Replace in Files&quot; (or shift+command+h)
  - NB: Oxygen search documentation found by clicking on the question mark in the lower left of the pop-up box or by going here: [https://www.oxygenxml.com/doc/versions/20.1/ug-editor/topics/find-and-replace-text-in-files.html](https://www.oxygenxml.com/doc/versions/20.1/ug-editor/topics/find-and-replace-text-in-files.html)
- EXAMPLE
  - Text to find: mould
    - Don&#39;t select whole words only (that would only give you &quot;mould&quot; not &quot;moulds&quot; or &quot;moulds.&quot;
    - Ignore white space
      - NB: Assume that there may be any number of spaces between the words in a phrase you are searching for. You may select &quot;Ignore extra whitespace&quot; to address this. Otherwise, you can also locate target phrases by the smallest component to match (e.g., &quot;vye&quot; or &quot;eau de&quot; when looking for &quot;eau de vye&quot;)
    - Enable XML search options
      - &quot;Search only in: Element names&quot; = search only in the tag titles (e.g. tl → tool tag)
      - &quot;Search only in: Element contents&quot; = search only in the text NOT the tag titles
    - Scope
      - Allows to search within a parts of the project or its entirety
      - If one has opened &quot;Find/Replace in Files&quot; by right clicking on a specific directory (e.g., &quot;tl&quot; under ms-xml), it will by default search only within that directory
      - One can change the scope of this to include:
        - Project (entire project)
        - Specified path (type in directory path you would like to perform this action on)
        -
    - Filters
      - Include files: \*.xml --\&gt;this is the default; leave like this
  - Replace with: mold
  - Replace all \&gt; Preview
    - You&#39;ll be able to see what the changes will look like
    - NOTE: if you have left things case **in** sensitive, then a batch auto-replace would destroy case sensitivity in all the xml documents
      - &quot;Mould&quot; would become &quot;mold&quot;

- **HOW TO SEARCH FOR FRENCH WORD IN TCN AND FIND EQUIVALENT PLACE IN TL**
  - Search tcn
  - click on search result
  - in the text, right-click on the occurrence (or inside the nearest short element, e.g. a material tag; this will provide a path to that element and thus get you to where you need to be more quickly than targeting a whole ab).
  - select &quot;Copy XPath&quot;
  - go to the equivalent TL file
  - paste copied XPath into the box where it says XPath 2.0 ![](RackMultipart20210225-4-c0v23p_html_34762cb494677d2a.png)
  - press enter
  - and you&#39;re there! (you may need to click the file at the bottom where results are shown in order to open it in a window)
  - Tip: you can get back to your search query and results by clicking on the &#39;Find in files&#39; tab along the bottom of the screen: ![](RackMultipart20210225-4-c0v23p_html_af5c5fe0dd82fb0.gif)

  - To see tcn and tl in parallel: click on the tab with the tl file, go to &#39;Window&#39; in the Menu bar, and select &#39;Tile editors vertically&#39;. NB do not click on the &#39;split editor&#39; option, this won&#39;t work.

**ADVANCED SEARCH OPTIONS IN OXYGEN**

Problem of multi-word search terms being interrupted by arbitrary line breaks, e.g. Tiann&#39;s issue of searching for &#39;eau de v&#39; in order to capture &#39;eau de vie&#39; &#39;eau de vye&#39;. The arbitrarily created line-break in the xml file seems to have disrupted the search for the string on fol. 137v, line 15 (which was not picked up by the search.).

- Quick solution:
  - select &#39;ignore whitespace&#39;
  - locate target phrases by the smallest component to match. E.g., just &quot;vie&quot; and then &quot;vye&quot; and evaluate the results.

- **REGULAR EXPRESSION** (Oxygen documentation on this is weak so here is expert advice from THC)
  - search for &#39;de-v[iy]e&#39;
    - that is, &quot;de&quot; followed by a &quot;-&quot; followed by a &quot;v&quot; followed by either an &quot;i&quot; or a &quot;y&quot; followed by an &quot;e&quot;. The square brackets in the expression form a character class which defines a set of characters to match; i.e, &quot;I&quot; or &quot;y&quot;
  - To find all the cases where &quot;de&quot; is followed by whitespace and then &quot;vie&quot; or &quot;vye&quot;, search &#39;de\s+v[iy]e&#39;
    - that is, &quot;de&quot; followed by 1 or more (designated by the &quot;+&quot; character) whitespace characters (space, tab, return) followed by a &quot;v&quot; followed by either an &quot;i&quot; or a &quot;y&quot; followed by an &quot;e&quot;.
    - The \s is a shorthand character class which matches against a built-in, predefined set of characters, in this case all whitespace characters. Often you can specify the inverse (or negation) of shorthand character classes by using the corresponding upper-case character after the slash. So, \S matches against all non-whitespace characters. A couple other useful shorthand character classes in Oxygen&#39;s regular expression syntax are:
      - \w alphanumeric character (a &quot;word&quot; character&quot;) and its inverse \W: non-alphanumeric character
      - \d digit character (i.e., 0-9) and its inverse \D non-digit character
  - There are ways to specify character classes, but there&#39;s more complexity involved.
  - Helpfully, if &quot;Regular expression&quot; is selected in the Oxygen Find window, on entering a \ a list of shorthand character classes and &quot;escapes&quot; for other special characters will pop up. Unfortunately, Oxygen&#39;s documentation on regular expressions is pretty weak.

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**CLONE REPOSITORY FROM GITHUB (to make a local version)**

- [https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)
- Terry says SSH (better option) if you&#39;re using your regular computer (i.e., the same public key that&#39;s on your computer and associated with your GitHub account); otherwise HTTPS
  - See [https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh](https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**RE-CLONE REPOSITORY IF IT IS OUT OF DATE AND YOU DO NOT WANT TO SAVE/PUSH ANY LOCAL CHANGES**

- rm -fr [name of repository] _(removing the contents of the repository to re-clone it)_
  - For example,
    - rm -fr m-k-manuscript-data
- history | grep clone _(this gives you when you last ran that command)_
- _Provides a number of the last instance it was run_
- ![number provided]
  - For example,
    - !30

**CHECK YOUR BRANCH AND MAKE SURE IT IS CORRECT**

- See also [https://www.git-tower.com/learn/git/faq/checkout-remote-branch](https://www.git-tower.com/learn/git/faq/checkout-remote-branch)
- _Navigate into the desired directory (i.e. m-k-manuscript-data)_
- git branch _(tells you which branch you are in)_
- git fetch _(tells you what is happening in remote repo)_
- git status _(tells you which branch you&#39;re on and how far ahead or
 behind you are from Origin)_
- If status is behind, pull the most current version (see below)
- If ahead:
  - You&#39;re fucked
  - One option: try **RE-CLONE REPOSITORY** (above)

**PULL THE MOST CURRENT VERSION FROM REMOTE REPOSITORY**

- [https://git-scm.com/docs/git-pull](https://git-scm.com/docs/git-pull)
- git pull -a _(pulls ALL branches)_
-

**CREATE A NEW BRANCH**

- git checkout -b [name of branch e.g. issue 73]
(this creates a new branch named &quot;issue73&quot;)
- git branch (to check you&#39;re in the new branch (issue73)
- NB: In Oxygen, you will need to refresh the highest level of your directory for it to register the current directory
- MAKE YOUR CHANGES
- git add . (this tells git to start tracking any files in the directory not
 already tracked. We shouldn&#39;t have created any new files,
 but good to do this just in case.)
- git commit -m &#39;[#[issue] your message]&#39; (e.g., &#39;#73: change mould to mold&#39;)
(commits your changes to git and creates an automatic link
 in the commit message to the issue in question)
- git push -u origin issue73
- AFTER ALL HAS BEEN MERGED UP IN THE CLOUD… you don&#39;t want to be working in a merged branch on your local repository, so…
- git checkout master (to get back into the master branch)

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**GITHUB - REVERT TO PREVIOUS COMMIT:**

- [https://code.likeagirl.io/how-to-undo-the-last-commit-393e7db2840b](https://code.likeagirl.io/how-to-undo-the-last-commit-393e7db2840b)

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**GITHUB - CREATE A DIRECTORY (from the directory):**

- Better to create a file to put into the not-yet-created directory
- mkdir [directory name]
- EITHER:
  - Copy or move an existing file into the directory
    - cp [file name] [directory name]
    - mv [file name] [directory name]

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**SAVE COMMAND LINE &quot;COMMANDS&quot; HISTORY:**

- In command line
  - history _(lists the last number of commands you have typed - number depends on individual settings)_
  - history \&gt; history.txt _(saves history to a text file)_

![](RackMultipart20210225-4-c0v23p_html_237499165a11f2b9.gif)

**THC+NJR ONLY** **- CHECKOUT A SPECIFIC OR REMOTE BRANCH (WORK IN A SPECIFIC BRANCH)**

- git checkout --track origin/[name of branch] _(VERY IMPORTANT TO TRACK)_
  - For example,
    - git checkout --track origin/v0.2
- See [https://stackify.com/git-checkout-remote-branch/](https://stackify.com/git-checkout-remote-branch/)
