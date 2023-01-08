Note: by contributing code to this project in any form, including sending
a pull request via Github, a code fragment or patch via private email or
public discussion groups, you agree to release your code under the terms
of the [LICENSEs](license.txt).

# IMPORTANT: HOW TO USE REDIS GITHUB ISSUES

Github issues SHOULD ONLY BE USED to report bugs, and for DETAILED feature
requests.

Issues and pull requests for documentation belong in the [redis-stack-docs](https://github.com/redis/redis-stack-docs) respository.

If you are reporting a security bug or vulnerability, see [SECURITY.md](SECURITY.md).

# How to provide a patch for a new feature

1. If it is a major feature or a semantical change, please don't start coding
straight away: if your feature is not a conceptual fit you'll lose a lot of
time writing the code without any reason. Start by posting in a GitHub issue issue at Github with the description of, exactly, what you want
to accomplish and why. Use cases are important for features to be accepted.

2. If in step 1 you get an acknowledgment from the project leaders, use the
   following procedure to submit a patch:

    a. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) Redis Stack on github.
    b. Create a topic branch (git checkout -b my_branch)
    c. Push to your branch (git push origin my_branch)
    d. Initiate a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) on this repository.
    e. Done :)

3. Keep in mind that we are very overloaded, so issues and PRs sometimes wait
for a *very* long time. However this is not lack of interest, as the project
gets more and more users, we find ourselves in a constant need to prioritize
certain issues/PRs over others. If you think your issue/PR is very important
try to popularize it, have other users commenting and sharing their point of
view and so forth. This helps.

Thanks!
