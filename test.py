from inventory_solver import solve_inventory


def format_money(v):
    return f"${v:,.2f}"


def run_harvey():
    result = solve_inventory(
        unit_cost=20,
        ordering_cost=100,
        penalty_cost=20,
        interest_rate=0.25,
        lead_time_months=4,
        lead_time_demand_avg=500,
        lead_time_demand_sd=100,
    )

    print("=" * 64)
    print(" HARVEY'S SPECIALTY SHOP - TEST PROBLEM")
    print("=" * 64)

    print("\nDerived Parameters")
    print("-" * 64)
    print(f"  Annual demand (lambda)      : {result['annual_demand']:.2f}")
    print(f"  Holding cost per unit (h)   : {format_money(result['holding_unit_cost'])}")

    print("\nIteration Log")
    print("-" * 64)
    print(
        f"  {'i':>3} {'Q':>10} {'R':>10} {'z':>8} {'F(R)':>8} {'L(z)':>8} {'n(R)':>8}"
    )
    for it in result["iteration_log"]:
        print(
            f"  {it['i']:>3} {it['Q']:>10.4f} {it['R']:>10.4f} {it['z']:>8.4f} "
            f"{it['F']:>8.4f} {it['L_z']:>8.4f} {it['n_R']:>8.4f}"
        )
    print(f"  Converged after {result['iterations']} refinement iterations.")

    print("\nDecision Variables")
    print("-" * 64)
    print(f"  Optimal lot size  (Q*)     : {result['Q']:.2f}  (rounded: {round(result['Q'])})")
    print(f"  Reorder point     (R*)     : {result['R']:.2f}  (rounded: {round(result['R'])})")
    print(f"  Number of iterations       : {result['iterations']}")
    print(f"  Safety stock     (R - mu)  : {result['safety_stock']:.2f}")

    print("\nAverage Annual Costs")
    print("-" * 64)
    print(f"  Holding cost   = h*(Q/2+SS): {format_money(result['holding_cost'])}/year")
    print(f"  Setup cost     = k*lam/Q   : {format_money(result['setup_cost'])}/year")
    print(f"  Penalty cost   = p*lam*n/Q : {format_money(result['penalty_cost_annual'])}/year")
    print(f"  Total average cost          : {format_money(result['total_avg_cost'])}/year")

    print("\nService Measures")
    print("-" * 64)
    print(f"  Avg time between orders    : {result['avg_time_between_orders']:.4f} years "
          f"(~{result['avg_time_between_orders']*12:.2f} months)")
    print(f"  F(R) - no stockout cycles  : {result['proportion_no_stockout']:.4f} "
          f"(~{result['proportion_no_stockout']*100:.2f}%)")
    print(f"  n(R)/Q - unmet demand frac : {result['proportion_demand_unmet']:.4f} "
          f"(~{result['proportion_demand_unmet']*100:.4f}%)")

    print("\nReference values from midterm report")
    print("-" * 64)
    print("  Expected: Q ~= 289, R ~= 667, SS ~= 167")
    print(f"  Got:      Q  = {round(result['Q'])}, R  = {round(result['R'])}, "
          f"SS  = {round(result['safety_stock'])}")
    print("=" * 64)

    assert abs(result["Q"] - 289) <= 5, f"Q deviates: {result['Q']}"
    assert abs(result["R"] - 667) <= 5, f"R deviates: {result['R']}"
    print("\n[PASS] Algorithm matches Harvey's expected solution.")


if __name__ == "__main__":
    run_harvey()
