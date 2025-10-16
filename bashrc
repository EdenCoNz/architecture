push () {
        git add .;
        git commit -m "$1"
        git push
}

if [ -z "$SSH_AUTH_SOCK" ] ; then
 eval `ssh-agent -s`
 ssh-add ~/.ssh/id_github
fi

alias claudeyolo='claude --dangerously-skip-permissions'
alias mint='ssh ed@mint.edenco.online'
alias mintlocal='ssh ed@192.168.1.210'
alias staging='ssh ed@staging.edenco.online'
alias staginglocal='ssh ed@192.168.1.211'