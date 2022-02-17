# #!/bin/bash
module load multiwfn/3.8

# declare -a StringArray=("o-o" "o-nh" "o-no" "nh-o" "nh-nh" "nh-no" "no-o" "no-nh" "no-no")
# # declare -a StringArray=("ba2-2-p")

# for val in "${StringArray[@]}"; do
#     cd /home/asnow/p2015120004/asnow/honours/na1/derivative_charges/charges-$val
#     orca_2aim charges-$val
#     # echo -e "7\n12\n2\n0.188973\n1\ny\n0\no\nq" | Multiwfn ${val}.wfn
# done

cd /Volumes/MonARCH/honours/cyclisation_benchmarking/wb97m-v/bron_acid_1/ba1-2-r
echo -e "7\n12\n1\ny\n0\no\nq" | multiwfn ba1-2-r.wfn
cd /Volumes/MonARCH/honours/cyclisation_benchmarking/wb97m-v/bron_acid_2/ba2-2-r
echo -e "7\n12\n1\ny\n0\no\nq" | multiwfn ba2-2-r.wfn
cd /Volumes/MonARCH/honours/cyclisation_benchmarking/wb97m-v/bron_base/bb-2-r
echo -e "7\n12\n1\ny\n0\no\nq" | multiwfn bb-2-r.wfn
cd /Volumes/MonARCH/honours/cyclisation_benchmarking/wb97m-v/lewis_acid/la-2-r
echo -e "7\n12\n1\ny\n0\no\nq" | multiwfn la-2-r.wfn
cd /Volumes/MonARCH/honours/cyclisation_benchmarking/wb97m-v/non_activated/na-1-r
echo -e "7\n12\n1\ny\n0\no\nq" | multiwfn na-1-r.wfn
cd /Volumes/MonARCH/honours/lb2/benchmarking/lb2r-alt
echo -e "7\n12\n1\ny\n0\no\nq" | multiwfn lb2r-alt.wfn