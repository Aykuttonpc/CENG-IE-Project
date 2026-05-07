import math
from normal_tables import lookup_z_from_F, loss_function


def solve_inventory(
    unit_cost,
    ordering_cost,
    penalty_cost,
    interest_rate,
    lead_time_months,
    lead_time_demand_avg,
    lead_time_demand_sd,
    tolerance=0.5,
    max_iter=500,
):
    if unit_cost <= 0 or ordering_cost <= 0 or penalty_cost <= 0:
        raise ValueError("Costs must be positive.")
    if interest_rate <= 0:
        raise ValueError("Interest rate must be positive.")
    if lead_time_months <= 0:
        raise ValueError("Lead time must be positive.")
    if lead_time_demand_avg <= 0 or lead_time_demand_sd <= 0:
        raise ValueError("Lead time demand and SD must be positive.")

    t = lead_time_months / 12.0
    h = interest_rate * unit_cost
    annual_demand = lead_time_demand_avg / t

    Q = math.sqrt(2.0 * ordering_cost * annual_demand / h)
    one_minus_F = Q * h / (penalty_cost * annual_demand)
    F = 1.0 - one_minus_F
    z = lookup_z_from_F(F)
    R = lead_time_demand_avg + lead_time_demand_sd * z
    L_z = loss_function(z)
    n_R = lead_time_demand_sd * L_z

    iteration_log = [
        {
            "i": 0,
            "Q": Q,
            "R": R,
            "z": z,
            "F": F,
            "L_z": L_z,
            "n_R": n_R,
        }
    ]

    iter_count = 0
    converged = False
    while iter_count < max_iter:
        iter_count += 1

        Q_new = math.sqrt(
            2.0 * annual_demand * (ordering_cost + penalty_cost * n_R) / h
        )
        one_minus_F_new = Q_new * h / (penalty_cost * annual_demand)
        F_new = 1.0 - one_minus_F_new
        z_new = lookup_z_from_F(F_new)
        R_new = lead_time_demand_avg + lead_time_demand_sd * z_new
        L_z_new = loss_function(z_new)
        n_R_new = lead_time_demand_sd * L_z_new

        iteration_log.append(
            {
                "i": iter_count,
                "Q": Q_new,
                "R": R_new,
                "z": z_new,
                "F": F_new,
                "L_z": L_z_new,
                "n_R": n_R_new,
            }
        )

        if abs(Q_new - Q) < tolerance and abs(R_new - R) < tolerance:
            Q, R, z, F, L_z, n_R = Q_new, R_new, z_new, F_new, L_z_new, n_R_new
            converged = True
            break

        Q, R, z, F, L_z, n_R = Q_new, R_new, z_new, F_new, L_z_new, n_R_new

    safety_stock = R - lead_time_demand_avg
    holding_cost = h * (Q / 2.0 + safety_stock)
    setup_cost = ordering_cost * annual_demand / Q
    penalty_cost_annual = penalty_cost * annual_demand * n_R / Q
    avg_time_between_orders = Q / annual_demand
    proportion_no_stockout = F
    proportion_demand_unmet = n_R / Q

    return {
        "inputs": {
            "unit_cost": unit_cost,
            "ordering_cost": ordering_cost,
            "penalty_cost": penalty_cost,
            "interest_rate": interest_rate,
            "lead_time_months": lead_time_months,
            "lead_time_demand_avg": lead_time_demand_avg,
            "lead_time_demand_sd": lead_time_demand_sd,
        },
        "annual_demand": annual_demand,
        "holding_unit_cost": h,
        "Q": Q,
        "R": R,
        "iterations": iter_count,
        "converged": converged,
        "iteration_log": iteration_log,
        "z": z,
        "F": F,
        "L_z": L_z,
        "n_R": n_R,
        "safety_stock": safety_stock,
        "holding_cost": holding_cost,
        "setup_cost": setup_cost,
        "penalty_cost_annual": penalty_cost_annual,
        "total_avg_cost": holding_cost + setup_cost + penalty_cost_annual,
        "avg_time_between_orders": avg_time_between_orders,
        "proportion_no_stockout": proportion_no_stockout,
        "proportion_demand_unmet": proportion_demand_unmet,
    }
