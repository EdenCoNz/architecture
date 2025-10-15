push () {
        git add .;
        git commit -m "$1"
        git push
}
alias claudeyolo='claude --dangerously-skip-permissions'
alias mint='ssh ed@mint.edenco.online'
alias mintlocal='ssh ed@192.168.1.210'
alias staging='ssh ed@staging.edenco.online'
alias staginglocal='ssh ed@192.168.1.211'