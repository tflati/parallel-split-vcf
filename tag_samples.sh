NAME="$1"
echo "$(tput bold) Tagging samples with tag=$NAME$(tput sgr0)" >&2
awk -v NAME="$NAME" '{print $0"\t"NAME}' -
