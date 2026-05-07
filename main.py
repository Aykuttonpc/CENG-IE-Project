import tkinter as tk
from tkinter import ttk, messagebox
from inventory_solver import solve_inventory


PRIMARY = "#1e3a8a"
ACCENT = "#0ea5e9"
BG = "#f1f5f9"
PANEL = "#ffffff"
TEXT = "#0f172a"
MUTED = "#64748b"


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Optimization - Lot Size & Reorder Point")
        self.root.geometry("1080x740")
        self.root.minsize(960, 680)
        self.root.configure(bg=BG)

        self.entries = {}
        self.result_labels = {}

        self._configure_styles()
        self._build_layout()

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=PRIMARY, font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=PANEL, foreground=PRIMARY, font=("Segoe UI", 11, "bold"))
        style.configure("Result.TLabel", background=PANEL, foreground=PRIMARY, font=("Consolas", 11, "bold"))
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("TLabelframe", background=PANEL, foreground=PRIMARY, borderwidth=1)
        style.configure("TLabelframe.Label", background=PANEL, foreground=PRIMARY, font=("Segoe UI", 11, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=8)
        style.configure("TEntry", padding=6)
        style.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            font=("Consolas", 10),
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background=PRIMARY,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", ACCENT)])

    def _build_layout(self):
        outer = ttk.Frame(self.root, padding=16, style="TFrame")
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="TFrame")
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(
            header,
            text="Optimal Lot Size (Q*) and Reorder Point (R*) Calculator",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="ENM320 / BIM2006 Term Project  -  Continuous review (Q, R) inventory model",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        body = ttk.Frame(outer, style="TFrame")
        body.pack(fill="both", expand=True)

        self._build_input_panel(body)
        self._build_output_panel(body)

        self._build_iteration_panel(outer)

    def _build_input_panel(self, parent):
        wrapper = ttk.LabelFrame(parent, text="  Inputs  ", padding=14)
        wrapper.pack(side="left", fill="y", padx=(0, 8))

        fields = [
            ("Unit cost (c)", "unit_cost", "20", "$/unit"),
            ("Ordering cost (k)", "ordering_cost", "100", "$/order"),
            ("Penalty cost (p)", "penalty_cost", "20", "$/unit"),
            ("Annual interest rate (I)", "interest_rate", "0.25", "fraction"),
            ("Lead time", "lead_time", "4", "months"),
            ("Lead time demand (mu)", "lt_demand", "500", "units"),
            ("Lead time SD (sigma)", "lt_sd", "100", "units"),
        ]

        for i, (label, key, default, unit) in enumerate(fields):
            ttk.Label(wrapper, text=label, style="Panel.TLabel").grid(
                row=i, column=0, sticky="w", pady=5
            )
            entry = ttk.Entry(wrapper, width=14, justify="right")
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky="ew", padx=8, pady=5)
            ttk.Label(wrapper, text=unit, style="Muted.TLabel").grid(
                row=i, column=2, sticky="w", pady=5
            )
            self.entries[key] = entry

        wrapper.columnconfigure(1, weight=1)

        button_row = ttk.Frame(wrapper, style="Panel.TFrame")
        button_row.grid(row=len(fields), column=0, columnspan=3, sticky="ew", pady=(14, 0))
        ttk.Button(button_row, text="Calculate", style="Primary.TButton", command=self.calculate).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(
            button_row, text="Load Test Problem", style="Secondary.TButton", command=self.load_test
        ).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(button_row, text="Reset", style="Secondary.TButton", command=self.reset_all).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        ttk.Separator(wrapper, orient="horizontal").grid(
            row=len(fields) + 1, column=0, columnspan=3, sticky="ew", pady=(14, 8)
        )

        ttk.Label(
            wrapper,
            text="Holding cost h = I x c is computed automatically.\n"
                 "Annual demand lambda = mu / (lead_time/12).",
            style="Muted.TLabel",
            justify="left",
        ).grid(row=len(fields) + 2, column=0, columnspan=3, sticky="w")

    def _build_output_panel(self, parent):
        wrapper = ttk.LabelFrame(parent, text="  Performance Measures  ", padding=14)
        wrapper.pack(side="left", fill="both", expand=True, padx=(8, 0))

        rows = [
            ("Annual demand (lambda)", "annual_demand", "{:.2f}", "units/year"),
            ("Holding cost per unit (h)", "holding_unit_cost", "${:.2f}", "/unit/year"),
            ("__sep__", None, None, None),
            ("Optimal lot size (Q*)", "Q", "{:.2f}", "units"),
            ("Reorder point (R*)", "R", "{:.2f}", "units"),
            ("Number of iterations", "iterations", "{:d}", ""),
            ("Safety stock (R - mu)", "safety_stock", "{:.2f}", "units"),
            ("__sep__", None, None, None),
            ("Avg annual holding cost", "holding_cost", "${:,.2f}", "/year"),
            ("Avg annual setup cost", "setup_cost", "${:,.2f}", "/year"),
            ("Avg annual penalty cost", "penalty_cost_annual", "${:,.2f}", "/year"),
            ("Total average cost", "total_avg_cost", "${:,.2f}", "/year"),
            ("__sep__", None, None, None),
            ("Avg time between orders", "avg_time_between_orders", "{:.4f}", "years"),
            ("F(R)  - no-stockout cycles", "proportion_no_stockout", "{:.4f}", ""),
            ("n(R)/Q - demand unmet", "proportion_demand_unmet", "{:.4f}", ""),
        ]

        for i, (label, key, fmt, unit) in enumerate(rows):
            if label == "__sep__":
                ttk.Separator(wrapper, orient="horizontal").grid(
                    row=i, column=0, columnspan=3, sticky="ew", pady=6
                )
                continue
            ttk.Label(wrapper, text=label, style="Panel.TLabel").grid(
                row=i, column=0, sticky="w", pady=3
            )
            value = ttk.Label(wrapper, text="-", style="Result.TLabel")
            value.grid(row=i, column=1, sticky="e", padx=12, pady=3)
            ttk.Label(wrapper, text=unit, style="Muted.TLabel").grid(
                row=i, column=2, sticky="w", pady=3
            )
            self.result_labels[key] = (value, fmt)

        wrapper.columnconfigure(0, weight=2)
        wrapper.columnconfigure(1, weight=1)
        wrapper.columnconfigure(2, weight=0)

    def _build_iteration_panel(self, parent):
        wrapper = ttk.LabelFrame(parent, text="  Iteration Details  ", padding=10)
        wrapper.pack(fill="both", expand=False, pady=(12, 0))

        cols = ("i", "Q", "R", "z", "F(R)", "L(z)", "n(R)")
        self.tree = ttk.Treeview(wrapper, columns=cols, show="headings", height=7)
        for c, w in zip(cols, (50, 130, 130, 90, 90, 90, 90)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(wrapper, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

    def load_test(self):
        defaults = {
            "unit_cost": "20",
            "ordering_cost": "100",
            "penalty_cost": "20",
            "interest_rate": "0.25",
            "lead_time": "4",
            "lt_demand": "500",
            "lt_sd": "100",
        }
        for key, value in defaults.items():
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, value)
        self.calculate()

    def reset_all(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for label, _ in self.result_labels.values():
            label.config(text="-")
        for child in self.tree.get_children():
            self.tree.delete(child)

    def calculate(self):
        try:
            values = {
                "unit_cost": float(self.entries["unit_cost"].get()),
                "ordering_cost": float(self.entries["ordering_cost"].get()),
                "penalty_cost": float(self.entries["penalty_cost"].get()),
                "interest_rate": float(self.entries["interest_rate"].get()),
                "lead_time": float(self.entries["lead_time"].get()),
                "lt_demand": float(self.entries["lt_demand"].get()),
                "lt_sd": float(self.entries["lt_sd"].get()),
            }
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "All fields must contain numeric values (e.g. 0.25, 100, 500).",
            )
            return

        try:
            result = solve_inventory(
                unit_cost=values["unit_cost"],
                ordering_cost=values["ordering_cost"],
                penalty_cost=values["penalty_cost"],
                interest_rate=values["interest_rate"],
                lead_time_months=values["lead_time"],
                lead_time_demand_avg=values["lt_demand"],
                lead_time_demand_sd=values["lt_sd"],
            )
        except ValueError as exc:
            messagebox.showerror("Invalid Input", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Calculation Error", f"Unexpected error:\n{exc}")
            return

        self._update_outputs(result)

    def _update_outputs(self, result):
        for key, (label, fmt) in self.result_labels.items():
            value = result[key]
            try:
                label.config(text=fmt.format(value))
            except (TypeError, ValueError):
                label.config(text=str(value))

        for child in self.tree.get_children():
            self.tree.delete(child)
        for it in result["iteration_log"]:
            self.tree.insert(
                "",
                "end",
                values=(
                    it["i"],
                    f"{it['Q']:.4f}",
                    f"{it['R']:.4f}",
                    f"{it['z']:.4f}",
                    f"{it['F']:.4f}",
                    f"{it['L_z']:.4f}",
                    f"{it['n_R']:.4f}",
                ),
            )

        if not result["converged"]:
            messagebox.showwarning(
                "Convergence Warning",
                "Algorithm reached maximum iterations without converging within tolerance. "
                "Results shown are the last computed values.",
            )


def main():
    root = tk.Tk()
    InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
