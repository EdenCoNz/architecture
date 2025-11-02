# Bash Scripting Cheatsheet

## Getting Started

### Introduction

This resource provides a quick reference for Bash scripting fundamentals, with links to deeper learning materials on language syntax and best practices.

### Basic Example

```bash
#!/usr/bin/env bash

name="John"
echo "Hello $name!"
```

### Variables

```bash
name="John"
echo $name
echo "$name"
echo "${name}!"
```

Quote variables unless they contain wildcards or command fragments to expand.

```bash
wildcard="*.txt"
options="iv"
cp -$options $wildcard /tmp
```

### String Quotes

```bash
name="John"
echo "Hi $name"    #=> Hi John
echo 'Hi $name'    #=> Hi $name
```

### Shell Execution

```bash
echo "I'm in $(pwd)"
echo "I'm in `pwd`"  # obsolescent syntax
```

### Conditional Execution

```bash
git commit && git push
git commit || echo "Commit failed"
```

### Functions

```bash
get_name() {
  echo "John"
}

echo "You are $(get_name)"
```

### Conditionals

```bash
if [[ -z "$string" ]]; then
  echo "String is empty"
elif [[ -n "$string" ]]; then
  echo "String is not empty"
fi
```

### Strict Mode

```bash
set -euo pipefail
IFS=$'\n\t'
```

### Brace Expansion

```bash
echo {A,B}.js
```

| Expression | Description |
|---|---|
| `{A,B}` | Same as `A B` |
| `{A,B}.js` | Same as `A.js B.js` |
| `{1..5}` | Same as `1 2 3 4 5` |
| `{{1..3},{7..9}}` | Same as `1 2 3 7 8 9` |

## Parameter Expansions

### Basics

```bash
name="John"
echo "${name}"
echo "${name/J/j}"    #=> "john" (substitution)
echo "${name:0:2}"    #=> "Jo" (slicing)
echo "${name::2}"     #=> "Jo" (slicing)
echo "${name::-1}"    #=> "Joh" (slicing)
echo "${name:(-1)}"   #=> "n" (slicing from right)
echo "${name:(-2):1}" #=> "h" (slicing from right)
echo "${food:-Cake}"  #=> $food or "Cake"
```

```bash
length=2
echo "${name:0:length}"  #=> "Jo"
```

### Pathname Expansion

```bash
str="/path/to/foo.cpp"
echo "${str%.cpp}"    # /path/to/foo
echo "${str%.cpp}.o"  # /path/to/foo.o
echo "${str%/*}"      # /path/to

echo "${str##*.}"     # cpp (extension)
echo "${str##*/}"     # foo.cpp (basepath)

echo "${str#*/}"      # path/to/foo.cpp
echo "${str##*/}"     # foo.cpp

echo "${str/foo/bar}" # /path/to/bar.cpp
```

### Substring Operations

```bash
str="Hello world"
echo "${str:6:5}"    # "world"
echo "${str: -5:5}"  # "world"
```

```bash
src="/path/to/foo.cpp"
base=${src##*/}   #=> "foo.cpp" (basepath)
dir=${src%$base}  #=> "/path/to/" (dirpath)
dir=${src%/*}     #=> "/path/to" (dirpath)
```

### Prefix Name Expansion

```bash
prefix_a=one
prefix_b=two
echo ${!prefix_*}  # all variables names starting with `prefix_`
# prefix_a prefix_b
```

### Indirection

```bash
name=joe
pointer=name
echo ${!pointer}
# joe
```

### Substitution Patterns

| Code | Description |
|---|---|
| `${foo%suffix}` | Remove suffix |
| `${foo#prefix}` | Remove prefix |
| `${foo%%suffix}` | Remove long suffix |
| `${foo/%suffix}` | Remove long suffix |
| `${foo##prefix}` | Remove long prefix |
| `${foo/#prefix}` | Remove long prefix |
| `${foo/from/to}` | Replace first match |
| `${foo//from/to}` | Replace all |
| `${foo/%from/to}` | Replace suffix |
| `${foo/#from/to}` | Replace prefix |

### Comments

```bash
# Single line comment
```

```bash
: '
This is a
multi line
comment
'
```

### Substrings

| Expression | Description |
|---|---|
| `${foo:0:3}` | Substring (position, length) |
| `${foo:(-3):3}` | Substring from the right |

### Length

| Expression | Description |
|---|---|
| `${#foo}` | Length of `$foo` |

### String Manipulation

```bash
str="HELLO WORLD!"
echo "${str,}"   #=> "hELLO WORLD!" (lowercase 1st letter)
echo "${str,,}"  #=> "hello world!" (all lowercase)

str="hello world!"
echo "${str^}"   #=> "Hello world!" (uppercase 1st letter)
echo "${str^^}"  #=> "HELLO WORLD!" (all uppercase)
```

### Default Values

| Expression | Description |
|---|---|
| `${foo:-val}` | `$foo`, or `val` if unset (or null) |
| `${foo:=val}` | Set `$foo` to `val` if unset (or null) |
| `${foo:+val}` | `val` if `$foo` is set (and not null) |
| `${foo:?message}` | Show error message and exit if unset |

Omitting the `:` removes nullity checks, e.g. `${foo-val}`.

## Loops

### Basic For Loop

```bash
for i in /etc/rc.*; do
  echo "$i"
done
```

### C-style For Loop

```bash
for ((i = 0 ; i < 100 ; i++)); do
  echo "$i"
done
```

### Ranges

```bash
for i in {1..5}; do
    echo "Welcome $i"
done
```

#### With Step Size

```bash
for i in {5..50..5}; do
    echo "Welcome $i"
done
```

### Reading Lines

```bash
while read -r line; do
  echo "$line"
done <file.txt
```

### Infinite Loop

```bash
while true; do
  ···
done
```

## Functions

### Defining Functions

```bash
myfunc() {
    echo "hello $1"
}

# Alternate syntax
function myfunc {
    echo "hello $1"
}

myfunc "John"
```

### Returning Values

```bash
myfunc() {
    local myresult='some value'
    echo "$myresult"
}

result=$(myfunc)
```

### Raising Errors

```bash
myfunc() {
  return 1
}

if myfunc; then
  echo "success"
else
  echo "failure"
fi
```

### Arguments

| Expression | Description |
|---|---|
| `$#` | Number of arguments |
| `$*` | All positional arguments (as single word) |
| `$@` | All positional arguments (as separate strings) |
| `$1` | First argument |
| `$_` | Last argument of previous command |

Note: `$@` and `$*` must be quoted to perform as described.

## Conditionals

### Condition Tests

| Condition | Description |
|---|---|
| `[[ -z STRING ]]` | Empty string |
| `[[ -n STRING ]]` | Not empty string |
| `[[ STRING == STRING ]]` | Equal |
| `[[ STRING != STRING ]]` | Not equal |
| `[[ NUM -eq NUM ]]` | Equal |
| `[[ NUM -ne NUM ]]` | Not equal |
| `[[ NUM -lt NUM ]]` | Less than |
| `[[ NUM -le NUM ]]` | Less than or equal |
| `[[ NUM -gt NUM ]]` | Greater than |
| `[[ NUM -ge NUM ]]` | Greater than or equal |
| `[[ STRING =~ STRING ]]` | Regexp |
| `(( NUM < NUM ))` | Numeric conditions |

### Additional Conditions

| Condition | Description |
|---|---|
| `[[ -o noclobber ]]` | If OPTIONNAME is enabled |
| `[[ ! EXPR ]]` | Not |
| `[[ X && Y ]]` | And |
| `[[ X \|\| Y ]]` | Or |

### File Conditions

| Condition | Description |
|---|---|
| `[[ -e FILE ]]` | Exists |
| `[[ -r FILE ]]` | Readable |
| `[[ -h FILE ]]` | Symlink |
| `[[ -d FILE ]]` | Directory |
| `[[ -w FILE ]]` | Writable |
| `[[ -s FILE ]]` | Size > 0 bytes |
| `[[ -f FILE ]]` | File |
| `[[ -x FILE ]]` | Executable |
| `[[ FILE1 -nt FILE2 ]]` | 1 is more recent |
| `[[ FILE1 -ot FILE2 ]]` | 2 is more recent |
| `[[ FILE1 -ef FILE2 ]]` | Same files |

### Conditional Examples

```bash
# String
if [[ -z "$string" ]]; then
  echo "String is empty"
elif [[ -n "$string" ]]; then
  echo "String is not empty"
else
  echo "This never happens"
fi
```

```bash
# Combinations
if [[ X && Y ]]; then
  ...
fi
```

```bash
# Equal
if [[ "$A" == "$B" ]]
```

```bash
# Regex
if [[ "A" =~ . ]]
```

```bash
if (( $a < $b )); then
   echo "$a is smaller than $b"
fi
```

```bash
if [[ -e "file.txt" ]]; then
  echo "file exists"
fi
```

## Arrays

### Defining Arrays

```bash
Fruits=('Apple' 'Banana' 'Orange')
```

```bash
Fruits[0]="Apple"
Fruits[1]="Banana"
Fruits[2]="Orange"
```

### Working with Arrays

```bash
echo "${Fruits[0]}"           # Element #0
echo "${Fruits[-1]}"          # Last element
echo "${Fruits[@]}"           # All elements, space-separated
echo "${#Fruits[@]}"          # Number of elements
echo "${#Fruits}"             # String length of 1st element
echo "${#Fruits[3]}"          # String length of Nth element
echo "${Fruits[@]:3:2}"       # Range (position 3, length 2)
echo "${!Fruits[@]}"          # Keys of all elements
```

### Array Operations

```bash
Fruits=("${Fruits[@]}" "Watermelon")    # Push
Fruits+=('Watermelon')                  # Also push
Fruits=( "${Fruits[@]/Ap*/}" )          # Remove by regex
unset Fruits[2]                         # Remove one item
Fruits=("${Fruits[@]}")                 # Duplicate
Fruits=("${Fruits[@]}" "${Veggies[@]}") # Concatenate
words=($(< datafile))                   # From file (split by IFS)
```

### Array Iteration

```bash
for i in "${arrayName[@]}"; do
  echo "$i"
done
```

## Dictionaries (Associative Arrays)

### Defining

```bash
declare -A sounds

sounds[dog]="bark"
sounds[cow]="moo"
sounds[bird]="tweet"
sounds[wolf]="howl"
```

### Working with Dictionaries

```bash
echo "${sounds[dog]}"  # Dog's sound
echo "${sounds[@]}"    # All values
echo "${!sounds[@]}"   # All keys
echo "${#sounds[@]}"   # Number of elements
unset sounds[dog]      # Delete dog
```

### Dictionary Iteration

#### Iterate Over Values

```bash
for val in "${sounds[@]}"; do
  echo "$val"
done
```

#### Iterate Over Keys

```bash
for key in "${!sounds[@]}"; do
  echo "$key"
done
```

## Options

### Shell Options

```bash
set -o noclobber  # Avoid overwriting files
set -o errexit    # Exit on error
set -o pipefail   # Show hidden failures
set -o nounset    # Expose unset variables
```

### Glob Options

```bash
shopt -s nullglob    # Non-matching globs removed
shopt -s failglob    # Non-matching globs throw errors
shopt -s nocaseglob  # Case insensitive globs
shopt -s dotglob     # Wildcards match dotfiles
shopt -s globstar    # Allow ** for recursive matches
```

Set `GLOBIGNORE` as colon-separated patterns to remove from glob matches.

## History

### Commands

| Command | Description |
|---|---|
| `history` | Show history |
| `shopt -s histverify` | Don't execute expanded result immediately |

### Expansions

| Expression | Description |
|---|---|
| `!$` | Expand last parameter of most recent command |
| `!*` | Expand all parameters of most recent command |
| `!-n` | Expand nth most recent command |
| `!n` | Expand nth command in history |
| `!<command>` | Expand most recent invocation of command |

### History Operations

| Code | Description |
|---|---|
| `!!` | Execute last command again |
| `!!:s/<FROM>/<TO>/` | Replace first occurrence |
| `!!:gs/<FROM>/<TO>/` | Replace all occurrences |
| `!$:t` | Expand only basename from last parameter |
| `!$:h` | Expand only directory from last parameter |

### Slices

| Code | Description |
|---|---|
| `!!:n` | Expand only nth token from most recent |
| `!^` | Expand first argument |
| `!$` | Expand last token |
| `!!:n-m` | Expand range of tokens |
| `!!:n-$` | Expand nth token to last |

## Miscellaneous

### Numeric Calculations

```bash
$((a + 200))      # Add 200 to $a
$(($RANDOM%200))  # Random number 0..199

declare -i count  # Declare as integer
count+=1          # Increment
```

### Subshells

```bash
(cd somedir; echo "I'm now in $PWD")
pwd # still in first directory
```

### Redirection

```bash
python hello.py > output.txt            # stdout to file
python hello.py >> output.txt           # append stdout
python hello.py 2> error.log            # stderr to file
python hello.py 2>&1                    # stderr to stdout
python hello.py 2>/dev/null             # stderr to null
python hello.py >output.txt 2>&1        # both to file
python hello.py &>/dev/null             # both to null
echo "$0: warning: too many users" >&2  # diagnostic to stderr

python hello.py < foo.txt      # feed file to stdin
diff <(ls -r) <(ls)            # Compare outputs without files
```

### Inspecting Commands

```bash
command -V cd
#=> "cd is a function/alias/whatever"
```

### Trap Errors

```bash
trap 'echo Error at about $LINENO' ERR
```

Or:

```bash
traperr() {
  echo "ERROR: ${BASH_SOURCE[1]} at about ${BASH_LINENO[0]}"
}

set -o errtrace
trap traperr ERR
```

### Case/Switch

```bash
case "$1" in
  start | up)
    vagrant up
    ;;

  *)
    echo "Usage: $0 {start|stop|ssh}"
    ;;
esac
```

### Source Relative

```bash
source "${0%/*}/../share/foo.sh"
```

### Printf

```bash
printf "Hello %s, I'm %s" Sven Olga
#=> "Hello Sven, I'm Olga"

printf "1 + 1 = %d" 2
#=> "1 + 1 = 2"

printf "This is how you print a float: %f" 2
#=> "This is how you print a float: 2.000000"

printf '%s\n' '#!/bin/bash' 'echo hello' >file
# format string applied to each group of arguments
printf '%i+%i=%i\n' 1 2 3  4 5 9
```

### Transform Strings

| Command Option | Description |
|---|---|
| `-c` | Operations apply to characters not in set |
| `-d` | Delete characters |
| `-s` | Replace repeated characters |
| `-t` | Truncates |
| `[:upper:]` | All upper case letters |
| `[:lower:]` | All lower case letters |
| `[:digit:]` | All digits |
| `[:space:]` | All whitespace |
| `[:alpha:]` | All letters |
| `[:alnum:]` | All letters and digits |

#### Example

```bash
echo "Welcome To Devhints" | tr '[:lower:]' '[:upper:]'
# WELCOME TO DEVHINTS
```

### Directory of Script

```bash
dir=${0%/*}
```

### Getting Options

```bash
while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do case $1 in
  -V | --version )
    echo "$version"
    exit
    ;;
  -s | --string )
    shift; string=$1
    ;;
  -f | --flag )
    flag=1
    ;;
esac; shift; done
if [[ "$1" == '--' ]]; then shift; fi
```

### Heredoc

```bash
cat <<END
hello world
END
```

Treats a source code section as a file input stream.

### Herestring

```bash
tr '[:lower:]' '[:upper:]' <<< "Will be uppercased, even $variable"
```

Treats a string as standard input (stdin).

### Process Substitution

```bash
# loop on myfunc output lines
while read -r line; do
  echo "$line"
done < <(myfunc)

# compare content of two folders
diff <(ls "$dir1") <(ls "$dir2")
```

Allows command input/output to be treated as a file.

### Reading Input

```bash
echo -n "Proceed? [y/n]: "
read -r ans
echo "$ans"
```

The `-r` option disables legacy backslash behavior.

```bash
read -n 1 ans    # Just one character
```

### Special Variables

| Expression | Description |
|---|---|
| `$?` | Exit status of last task |
| `$!` | PID of last background task |
| `$$` | PID of shell |
| `$0` | Filename of shell script |
| `$_` | Last argument of previous command |
| `${PIPESTATUS[n]}` | Return value of piped commands (array) |

### Go to Previous Directory

```bash
pwd # /home/user/foo
cd bar/
pwd # /home/user/foo/bar
cd -
pwd # /home/user/foo
```

### Check Command Result

```bash
if ping -c 1 google.com; then
  echo "You appear to have working internet"
fi
```

### Grep Check

```bash
if grep -q 'foo' ~/.bash_history; then
  echo "You appear to have typed 'foo' in the past"
fi
```

---

Source: https://devhints.io/bash
