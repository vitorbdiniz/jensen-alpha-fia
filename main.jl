include("./fatores_risco/risk_factors.jl");
using .factors;

function main()
    r = riskFactors(true, true, true);
    println(first(r,100));
    
end


main();